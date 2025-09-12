# kakao_auth.py
import os
import json
import time
import secrets
import requests
from urllib.parse import urlencode
from datetime import datetime, timezone
from dotenv import load_dotenv

AUTH_BASE = "https://kauth.kakao.com/oauth/authorize"
TOKEN_URL = "https://kauth.kakao.com/oauth/token"

def main():
    load_dotenv()

    client_id = os.getenv("KAKAO_CLIENT_ID")
    redirect_uri = os.getenv("KAKAO_REDIRECT_URI")
    client_secret = os.getenv("KAKAO_CLIENT_SECRET", "").strip()  # 콘솔에서 '사용'일 때만 값 설정

    if not client_id or not redirect_uri:
        print("Error: KAKAO_CLIENT_ID와 KAKAO_REDIRECT_URI를 .env에 설정하세요.")
        return

    # 선택 동의(추가 동의) 강제: scope=talk_message, prompt=login
    state = secrets.token_urlsafe(12)
    auth_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "talk_message",
        "prompt": "login",
        "state": state,
    }
    auth_url = f"{AUTH_BASE}?{urlencode(auth_params)}"

    print("브라우저에서 아래 URL을 열어 동의를 진행하세요:")
    print(auth_url)
    print()

    auth_code = input("리다이렉트된 URL의 code 파라미터 값을 입력하세요: ").strip()
    if not auth_code:
        print("Error: code 값이 비어 있습니다.")
        return

    # 토큰 교환: x-www-form-urlencoded
    token_payload = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code": auth_code,
    }
    # Client Secret을 콘솔에서 '사용'으로 켠 경우에만 포함
    if client_secret:
        token_payload["client_secret"] = client_secret

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        resp = requests.post(TOKEN_URL, headers=headers, data=token_payload, timeout=15)
        resp.raise_for_status()
        tokens = resp.json()

        # 메타 정보 보강(얻은 시각/만료 예정 시각)
        now = datetime.now(timezone.utc)
        tokens["_obtained_at_utc"] = now.isoformat()
        if "expires_in" in tokens:
            tokens["_expires_at_utc"] = (now.timestamp() + int(tokens["expires_in"]))

        # 저장
        with open("tokens.json", "w", encoding="utf-8") as f:
            json.dump(tokens, f, ensure_ascii=False, indent=2)

        print("토큰을 tokens.json에 저장했습니다.")

        # scope 점검
        scope_str = tokens.get("scope", "")
        if "talk_message" not in scope_str.split():
            print("\n경고: 현재 토큰 scope에 'talk_message'가 없습니다.")
            print("→ 인가 URL에 scope=talk_message가 포함되었는지 확인하고, 다시 동의 과정을 수행하세요.")
        else:
            print("확인: scope에 'talk_message'가 포함되었습니다. '나에게 보내기' 전송이 가능합니다.")

    except requests.HTTPError as e:
        body = e.response.text if getattr(e, "response", None) else ""
        print(f"Error getting tokens: HTTP {getattr(e.response, 'status_code', '?')}")
        if body:
            print(f"Response body: {body}")
    except requests.RequestException as e:
        print(f"Error getting tokens (network): {e}")

if __name__ == "__main__":
    main()
