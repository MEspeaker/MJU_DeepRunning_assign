# 프로젝트 제목

카카오톡 데일리 시간표 알리미 (ChatGPT5 바이브코딩 기반)

# 프로젝트 개요

이 프로젝트는 매일 지정한 시각(기본 KST 오전 8시)에 당일 수업 일정을 카카오톡 나에게 보내기로 전송하는 파이썬 애플리케이션입니다. 시간표는 JSON 또는 CSV 파일에서 읽어오며, 요일·학기 기간·휴일 정보를 반영해 그날 필요한 항목만 선별합니다. 전송 메시지는 수업명, 강의실, 교수명을 간결한 텍스트로 구성합니다. 초기 1회 OAuth 2.0 인증으로 발급한 토큰을 로컬(tokens.json)에 저장하고, 이후에는 액세스 토큰 만료 시 리프레시 토큰으로 갱신합니다. 전송 없이 포맷만 확인하는 드라이런 모드가 있으며, 로컬 파이썬 실행 또는 Docker 컨테이너 실행을 모두 지원합니다. 컨테이너 또는 실행 환경이 켜져 있는 동안에만 스케줄링이 수행됩니다.

본 프로젝트는 ChatGPT5 바이브코딩을 사용해 초기 설계, 코드 뼈대 작성, 오류 수정 과정을 반복적으로 진행했습니다.

주요 구성은 다음과 같습니다.

- main.py: 진입점. --once(즉시 전송), --dry-run(출력만), --schedule(정시 실행) 처리 및 스케줄러 시작.

- kakao_auth.py: 최초 인증 코드 발급 및 토큰 교환(1회).

- kakao_client.py: 카카오톡 “나에게 보내기” 전송 및 토큰 갱신.

- schedule_runner.py: 오늘 수업 선별과 메시지 포맷 생성.

- timetable/loader.py, models.py: JSON/CSV 로드와 유효성 검증.

- data/sample.json, data/sample.csv: 샘플 시간표.

- requirements.txt, .env.example, Dockerfile, README.md: 의존성, 환경변수 예시, 컨테이너 빌드/실행 안내.

본 프로젝트는 “나에게 보내기” 전송만 대상으로 합니다. 친구에게 전송하는 기능은 포함되어 있지 않으며, 해당 기능은 별도 권한 및 절차가 필요합니다.

## 설정(Setup)
**1.의존성 설치(Install Dependencies)**

`pip install -r requirements.txt`

**2.카카오 애플리케이션 생성(Create a Kakao Application)**

Kakao Developers에 로그인합니다.

새 애플리케이션을 생성합니다.

Product > Kakao Login을 활성화하고 Redirect URI를 설정합니다.

인증 스크립트가 동작하려면 Redirect URI가 반드시 필요합니다. 권장 예시: http://localhost:5000/oauth

Consent Items(동의 항목) 탭으로 이동하여 카카오톡 메시지 전송 접근을 확인합니다.

콘솔 정책에 따라 ‘필수’로 지정할 수 없는 경우가 있으므로, 인가 시 scope=talk_message로 선택 동의를 요청해야 합니다.

앱의 REST API Key를 확인합니다(이 값이 KAKAO_CLIENT_ID입니다).

**3.환경 변수 설정(Configure Environment Variables)**

프로젝트 루트에서 예시 파일을 복사해 .env를 생성합니다.

`cp .env.example .env`


.env 파일을 열어 카카오 앱 정보를 입력합니다.

KAKAO_CLIENT_ID=your_rest_api_key
KAKAO_CLIENT_SECRET=your_client_secret # Optional(있는 경우에만)
KAKAO_REDIRECT_URI=http://localhost:5000/oauth # 카카오 앱 설정의 URI와 정확히 일치해야 함
TIMEZONE=Asia/Seoul
MESSAGE_PREFIX= # Optional: 모든 메시지 앞에 붙일 접두사

**4.카카오 인증(Authentication with Kakao)**

최초 1회 인증 스크립트를 실행해 API 토큰을 발급받습니다.

`python kakao_auth.py`


스크립트가 출력하는 인가(authorization) URL을 브라우저에 열어 로그인합니다.

필요한 권한에 동의합니다.

설정한 Redirect URI로 리다이렉트되며, URL에 code 파라미터가 포함됩니다(예: http://localhost:5000/oauth?code=YOUR_CODE_HERE).

이 code 값을 터미널에 입력합니다.

완료되면 프로젝트 디렉터리에 tokens.json이 생성되며, 여기에 액세스/리프레시 토큰이 저장됩니다.

**사용법(Usage)**

기본적으로 data/sample.json에서 시간표를 불러옵니다. 이 파일을 수정하거나 새 파일을 만들어 사용할 수 있으며, JSON과 CSV 형식을 모두 지원합니다.

애플리케이션 실행(Running the Application)

즉시 전송:

`python main.py --once`


드라이런(전송 없이 출력만):
포맷팅된 메시지를 콘솔에만 출력합니다.

`python main.py --dry-run`


일일 스케줄러 실행:
매일 오전 8시(Asia/Seoul) 기준으로 작업을 실행하는 스케줄러를 시작합니다.

`python main.py --schedule`

**도커(Docker)**

이 애플리케이션은 Docker 및 Docker Compose로도 실행할 수 있습니다.

도커 이미지 빌드(Build the Docker Image)
`docker build -t kakao-scheduler .`

컨테이너 실행(Run the Container)

프로젝트 디렉터리에 .env와 tokens.json이 있어야 합니다. 컨테이너는 설정된 방식에 따라 작업을 실행합니다.

`docker rm -f kakao-bot 2>nul & docker run -d --name kakao-bot --env-file .env -v "%cd%\tokens.json:/app/tokens.json" -v "%cd%\data:/app/data:ro" -w /app --entrypoint python kakao-scheduler main.py --schedule`

