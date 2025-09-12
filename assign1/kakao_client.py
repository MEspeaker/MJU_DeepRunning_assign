import os
import json
import time
import requests
from dotenv import load_dotenv

class KakaoClient:
    def __init__(self, token_file="tokens.json"):
        load_dotenv()
        self.client_id = os.getenv("KAKAO_CLIENT_ID")
        self.client_secret = os.getenv("KAKAO_CLIENT_SECRET")
        self.token_file = token_file
        self.tokens = self._load_tokens()

    def _load_tokens(self):
        try:
            with open(self.token_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def _save_tokens(self, tokens):
        with open(self.token_file, 'w') as f:
            json.dump(tokens, f)
        self.tokens = tokens

    def refresh_token(self):
        if not self.tokens or 'refresh_token' not in self.tokens:
            raise Exception("No refresh token found. Please run kakao_auth.py first.")

        url = "https://kauth.kakao.com/oauth/token"
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": self.tokens['refresh_token'],
        }
        if self.client_secret:
            payload["client_secret"] = self.client_secret

        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            new_tokens = response.json()
            # Kakao doesn't always return a new refresh token
            if 'refresh_token' not in new_tokens:
                new_tokens['refresh_token'] = self.tokens['refresh_token']
            self._save_tokens(new_tokens)
            print("Successfully refreshed tokens.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error refreshing token: {e}")
            print(f"Response: {response.text}")
            return False

    def send_self_message(self, message, max_retries=3):
        if not self.tokens:
            raise Exception("No tokens found. Please run kakao_auth.py first.")

        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        headers = {
            "Authorization": f"Bearer {self.tokens['access_token']}"
        }
        
        template_object = {
            "object_type": "text",
            "text": message,
            "link": {
                "web_url": "https://developers.kakao.com",
                "mobile_web_url": "https://developers.kakao.com"
            }
        }
        
        payload = {'template_object': json.dumps(template_object)}

        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, data=payload)
                if response.status_code == 401: # Unauthorized
                    print("Access token expired. Refreshing token...")
                    if not self.refresh_token():
                        return False # Stop if refresh fails
                    headers["Authorization"] = f"Bearer {self.tokens['access_token']}"
                    continue # Retry the request with the new token
                
                response.raise_for_status()
                print("Successfully sent KakaoTalk message.")
                return True

            except requests.exceptions.RequestException as e:
                print(f"Error sending message (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt) # Exponential backoff
                else:
                    print("Max retries reached. Failed to send message.")
                    return False
        return False
