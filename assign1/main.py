# main.py
import argparse
import os
from datetime import datetime
from dotenv import load_dotenv

from timetable.loader import load_from_json, load_from_csv
from schedule_runner import get_todays_classes, format_message
from kakao_client import KakaoClient

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from pytz import timezone

# 고정 타임존(KST)
KST = timezone("Asia/Seoul")


def run_job(dry_run: bool = False) -> None:
    """스케줄러가 실행하는 본 작업"""
    print(f"[run_job] start at {datetime.now(KST).isoformat()}", flush=True)
    load_dotenv()

    # 시간표 파일: .env에 TIMETABLE_FILE 지정 시 우선 사용, 없으면 기본값
    timetable_path = os.getenv("TIMETABLE_FILE", "data/sample.json")

    # 시간표 로드
    if timetable_path.endswith(".json"):
        timetable = load_from_json(timetable_path)
    elif timetable_path.endswith(".csv"):
        timetable = load_from_csv(timetable_path)
    else:
        raise ValueError("Unsupported timetable file format. Use .json or .csv")

    # 오늘 수업 → 메시지 포맷
    todays_classes = get_todays_classes(timetable)
    message = format_message(todays_classes, timetable.timezone)

    # 선택적 프리픽스
    message_prefix = os.getenv("MESSAGE_PREFIX")
    if message_prefix:
        message = f"{message_prefix}\n{message}"

    # 전송 또는 드라이런
    try:
        if dry_run:
            print("--- DRY RUN ---", flush=True)
            print(message, flush=True)
            print("----------------", flush=True)
        else:
            client = KakaoClient()
            client.send_self_message(message)
            print("[run_job] message sent", flush=True)
    except Exception as e:
        # 전송 오류를 명확히 출력
        print(f"[run_job] send failed: {e}", flush=True)
    finally:
        print(f"[run_job] end at {datetime.now(KST).isoformat()}", flush=True)


def on_event(e) -> None:
    """APScheduler 이벤트 리스너: 성공/실패 로그"""
    if e.exception:
        print(f"[JOB ERROR] {e.job_id}: {e.exception} (scheduled at {e.scheduled_run_time})", flush=True)
    else:
        print(f"[JOB OK] {e.job_id} ran at {e.scheduled_run_time}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="KakaoTalk Daily Schedule Notifier")
    parser.add_argument("--once", action="store_true", help="Send the schedule message immediately.")
    parser.add_argument("--dry-run", action="store_true", help="Print the message to the console instead of sending.")
    parser.add_argument("--schedule", action="store_true", help="Run the scheduler to send messages at the configured time.")
    args = parser.parse_args()

    if args.once or args.dry_run:
        run_job(dry_run=args.dry_run)
        return

    if args.schedule:
        # 스케줄 설정: .env에서 읽어 제어
        # SCHEDULE_EVERY_MINUTE=true 면 1분마다 실행(테스트용)
        load_dotenv()
        every_min = os.getenv("SCHEDULE_EVERY_MINUTE", "").lower() in ("1", "true", "yes", "on")
        hour = int(os.getenv("SCHEDULE_HOUR", "8"))
        minute = int(os.getenv("SCHEDULE_MINUTE", "0"))

        print("Starting scheduler...", flush=True)
        scheduler = BlockingScheduler(timezone=KST)
        scheduler.add_listener(on_event, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

        if every_min:
            trigger = CronTrigger(minute="*", second=0, timezone=KST)
            print("[schedule] mode=every-minute (second=0)", flush=True)
        else:
            trigger = CronTrigger(hour=hour, minute=minute, timezone=KST)
            print(f"[schedule] mode=daily {hour:02d}:{minute:02d} KST", flush=True)

        # 미스파이어/코얼레스: 절전·재시작 후 누락 복구 및 중복 실행 방지
        job = scheduler.add_job(
            run_job,
            trigger,
            coalesce=True,
            misfire_grace_time=3600,
        )

        # APScheduler 버전에 따라 next_run_time 속성이 없을 수 있으므로 방어적으로 출력
        nrt = getattr(job, "next_run_time", None)
        print(f"[schedule] job registered. next={nrt if nrt else 'N/A'}", flush=True)

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass
        return

    print("No action specified. Use --once, --dry-run, or --schedule.", flush=True)


if __name__ == "__main__":
    main()

