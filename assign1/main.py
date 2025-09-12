import argparse
import os
from dotenv import load_dotenv
from timetable.loader import load_from_json, load_from_csv
from schedule_runner import get_todays_classes, format_message
from kakao_client import KakaoClient
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

def run_job(dry_run=False):
    load_dotenv()
    # For now, we'll hardcode the timetable path. This could be a CLI arg.
    timetable_path = "data/sample.json"

    if timetable_path.endswith(".json"):
        timetable = load_from_json(timetable_path)
    elif timetable_path.endswith(".csv"):
        timetable = load_from_csv(timetable_path)
    else:
        raise ValueError("Unsupported timetable file format.")

    todays_classes = get_todays_classes(timetable)
    message = format_message(todays_classes, timetable.timezone)

    message_prefix = os.getenv("MESSAGE_PREFIX")
    if message_prefix:
        message = f"{message_prefix}\n{message}"

    if dry_run:
        print("--- DRY RUN ---")
        print(message)
        print("-----------------")
    else:
        client = KakaoClient()
        client.send_self_message(message)

def main():
    parser = argparse.ArgumentParser(description="KakaoTalk Daily Schedule Notifier")
    parser.add_argument("--once", action="store_true", help="Send the schedule message immediately.")
    parser.add_argument("--dry-run", action="store_true", help="Print the message to the console instead of sending.")
    parser.add_argument("--schedule", action="store_true", help="Run the scheduler to send messages at the configured time.")

    args = parser.parse_args()

    if args.once or args.dry_run:
        run_job(dry_run=args.dry_run)
    elif args.schedule:
        print("Starting scheduler...")
        scheduler = BlockingScheduler(timezone="Asia/Seoul")
        scheduler.add_job(run_job, CronTrigger(hour=8, minute=0))
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass
    else:
        print("No action specified. Use --once, --dry-run, or --schedule.")

if __name__ == "__main__":
    main()
