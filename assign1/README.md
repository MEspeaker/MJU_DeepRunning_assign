# KakaoTalk Daily Schedule Notifier

This project is a Python application that automatically sends your daily class schedule to your KakaoTalk as a "Message to me" every morning.

## Features

- Fetches daily schedule from a JSON or CSV timetable.
- Sends a formatted KakaoTalk message with the day's classes.
- Automatically runs every day at a scheduled time (default 8:00 AM KST).
- Handles Kakao API authentication (OAuth2) and automatic token refresh.
- Supports dry-run mode for testing.
- Can be run as a standalone Python script or as a Docker container.

## Prerequisites

- Python 3.11+
- A Kakao Account

## Setup

### 1. Install Dependencies

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

### 2. Create a Kakao Application

1.  Go to the [Kakao Developers](https://developers.kakao.com/) website and log in.
2.  Create a new application.
3.  Under "Product" > "Kakao Login", enable the feature. Configure the redirect URI.
    - You must add a redirect URI for the authentication script to work. A good default is `http://localhost:5000/oauth`.
4.  Go to the "Consent Items" tab and make sure "Access to Kakao Talk Message" is set to "Required".
5.  Take note of your app's **REST API Key** (this is your `KAKAO_CLIENT_ID`).

### 3. Configure Environment Variables

Create a `.env` file in the project root by copying the example file:

```bash
cp .env.example .env
```

Now, edit the `.env` file with your Kakao application details:

```
KAKAO_CLIENT_ID=your_rest_api_key
KAKAO_CLIENT_SECRET=your_client_secret # Optional, if you have one
KAKAO_REDIRECT_URI=http://localhost:5000/oauth # Must match the one in your Kakao app
TIMEZONE=Asia/Seoul
MESSAGE_PREFIX= # Optional: Add a prefix to every message
```

### 4. Authenticate with Kakao

Run the one-time authentication script to get your API tokens:

```bash
python kakao_auth.py
```

1.  The script will print an authorization URL. Copy and paste this URL into your web browser.
2.  Log in and grant the required permissions.
3.  You will be redirected to your `REDIRECT_URI`. The URL will contain a `code` parameter (e.g., `http://localhost:5000/oauth?code=YOUR_CODE_HERE`).
4.  Copy the `code` value from the URL and paste it into the terminal where the script is running.

This will create a `tokens.json` file in your project directory, which stores your access and refresh tokens.

## Usage

### Timetable

The application loads the schedule from `data/sample.json` by default. You can edit this file or create your own. Both JSON and CSV formats are supported.

### Running the Application

**Send a message immediately:**

```bash
python main.py --once
```

**Test without sending (Dry Run):**

This will print the formatted message to your console.

```bash
python main.py --dry-run
```

**Run the daily scheduler:**

This will start a scheduler that runs the job every day at 8:00 AM (Asia/Seoul time).

```bash
python main.py --schedule
```

## Docker

You can also run the application using Docker and Docker Compose.

### Build the Docker Image

```bash
docker build -t kakao-scheduler .
```

### Run the Container

Make sure your `.env` file and `tokens.json` are in the project directory. The container will use the cron scheduler to run the job.

```bash
docker run -d --name kakao-bot --env-file .env -v $(pwd)/tokens.json:/app/tokens.json kakao-scheduler
```