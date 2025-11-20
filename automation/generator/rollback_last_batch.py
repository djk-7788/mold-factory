import csv
import shutil
from pathlib import Path
from datetime import datetime

# ===== 경로 설정 =====
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]

PENDING_DIR = PROJECT_ROOT / "pending"
POSTS_DIR = PROJECT_ROOT / "content" / "posts"
PUBLISHED_DIR = PROJECT_ROOT / "published"
LOGS_DIR = PROJECT_ROOT / "automation" / "logs"
LOG_FILE = LOGS_DIR / "publish_log.csv"


def read_log_rows():
    if not LOG_FILE.exists():
        return []

    with LOG_FILE.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_log_rows(rows):
    fieldnames = ["date", "time", "batch_id", "filename",
                  "src", "dest", "backup", "rolled_back"]
    with LOG_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def get_last_batch_id(rows):
    """롤백 안 된 배치 중 가장 최근 batch_id 반환."""
    max_id = None
    for r in rows:
        if r.get("rolled_back", "0") == "1":
            continue
        try:
            bid = int(r.get("batch_id", "0"))
        except ValueError:
            continue
        if max_id is None or bid > max_id:
            max_id = bid
    return max_id


def main():
    print("=== 마지막 배치 롤백 스크립트 시작 ===")
    print(f"프로젝트 루트 : {PROJECT_ROOT}")
    print(f"로그 파일 : {LOG_FILE}")
    print()

    rows = read_log_rows()
    if not rows:
        print("📂 로그가 없어서 롤백할 배치를 찾을 수 없습니다.")
        return

    last_batch_id = get_last_batch_id(rows)
    if last_batch_id is None:
        print("✅ 롤백 가능한 배치가 없습니다. (모든 배치가 이미 롤백 표시됨)")
        return

    print(f"이번에 롤백할 batch_id : {last_batch_id}")
    target_rows = [r for r in rows if int(r.get("batch_id", "0")) == last_batch_id]

    if not target_rows:
        print("⚠ 로그에 해당 배치가 없어서 롤백할 수 없습니다.")
        return

    confirm = input("정말 이 배치를 롤백하시겠습니까? (y/n): ").strip().lower()
    if confirm != "y":
        print("롤백을 취소했습니다.")
        return

    restored_count = 0

    # posts -> pending 으로 되돌리기
    for r in target_rows:
        filename = r["filename"]
        post_path = POSTS_DIR / filename
        pending_path = PENDING_DIR / filename

        if post_path.exists():
            PENDING_DIR.mkdir(parents=True, exist_ok=True)
            shutil.move(str(post_path), str(pending_path))
            restored_count += 1
            print(f"↩ 롤백: {filename} (posts -> pending)")
        else:
            print(f"⚠ posts에 파일이 없어 건너뜀: {filename}")

    # 해당 배치 로그에 rolled_back 표시
    now_time = datetime.now().strftime("%H:%M:%S")
    for r in rows:
        try:
            bid = int(r.get("batch_id", "0"))
        except ValueError:
            continue
        if bid == last_batch_id:
            r["rolled_back"] = "1"
            # 시간도 업데이트해줄까?
            r["time"] = now_time

    write_log_rows(rows)

    print()
    print(f"🎯 롤백 완료! 되돌린 파일 수: {restored_count}개")
    print("이제 원하면 다시 daily_publish.py로 발행을 돌릴 수 있습니다.")


if __name__ == "__main__":
    main()
