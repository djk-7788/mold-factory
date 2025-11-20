import csv
import shutil
from datetime import datetime, date
from pathlib import Path

# ===== 설정 =====
DAILY_LIMIT = 100  # 하루 최대 발행 개수 (원하면 숫자 바꿔도 됨)

# ===== 경로 설정 =====
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]  # .../automation/generator -> mold-factory

PENDING_DIR = PROJECT_ROOT / "pending"
POSTS_DIR = PROJECT_ROOT / "content" / "posts"
PUBLISHED_DIR = PROJECT_ROOT / "published"
LOGS_DIR = PROJECT_ROOT / "automation" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_DIR / "publish_log.csv"


def ensure_log_file():
    """로그 파일이 없으면 헤더를 만들어 줌."""
    if not LOG_FILE.exists():
        with LOG_FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["date", "time", "batch_id", "filename",
                 "src", "dest", "backup", "rolled_back"]
            )


def read_log_rows():
    """전체 로그를 리스트로 읽어서 반환."""
    if not LOG_FILE.exists():
        return []

    with LOG_FILE.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_log_rows(rows):
    """rows(딕셔너리 리스트)를 통째로 다시 써줌."""
    fieldnames = ["date", "time", "batch_id", "filename",
                  "src", "dest", "backup", "rolled_back"]
    with LOG_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def get_today_count(rows):
    """오늘 이미 발행된 개수(롤백 안 된 것만)를 계산."""
    today_str = date.today().isoformat()
    count = 0
    for r in rows:
        if r["date"] == today_str and r.get("rolled_back", "0") != "1":
            count += 1
    return count


def get_next_batch_id(rows):
    """다음 배치 ID를 계산."""
    max_id = 0
    for r in rows:
        try:
            bid = int(r.get("batch_id", "0"))
            if bid > max_id:
                max_id = bid
        except ValueError:
            continue
    return max_id + 1


def list_pending_files():
    """pending 폴더의 .md 파일 목록을 이름 기준 정렬해서 가져오기."""
    if not PENDING_DIR.exists():
        return []
    files = [p for p in PENDING_DIR.glob("*.md") if p.is_file()]
    return sorted(files, key=lambda p: p.name)


def main():
    print("=== 하루 발행 스크립트 (안정 모드) 시작 ===")
    print(f"프로젝트 루트 : {PROJECT_ROOT}")
    print(f"대기 큐(pending) : {PENDING_DIR}")
    print(f"발행 폴더(posts) : {POSTS_DIR}")
    print(f"백업 폴더(published) : {PUBLISHED_DIR}")
    print(f"로그 파일 : {LOG_FILE}")
    print()

    ensure_log_file()
    rows = read_log_rows()

    pending_files = list_pending_files()
    pending_count = len(pending_files)
    print(f"현재 pending 대기 파일 수 : {pending_count}")

    if pending_count == 0:
        print("📂 발행할 pending 파일이 없습니다.")
        return

    # 오늘 이미 발행된 개수 & 남은 쿼터 계산
    today_count = get_today_count(rows)
    remaining_quota = max(0, DAILY_LIMIT - today_count)

    print(f"오늘 이미 발행된 개수 : {today_count}")
    print(f"오늘 남은 쿼터(DAILY_LIMIT={DAILY_LIMIT}) : {remaining_quota}")

    if remaining_quota <= 0:
        print("🚫 오늘은 이미 최대 발행량에 도달했습니다. 내일 다시 발행하세요.")
        return

    # 오늘 이 실행에서 발행하고 싶은 개수 입력
    try:
        raw = input("오늘 몇 개를 발행할까요? (예: 50): ").strip()
        want_count = int(raw)
    except ValueError:
        print("숫자를 제대로 입력하지 않아 작업을 종료합니다.")
        return

    if want_count <= 0:
        print("0개 이하는 발행할 수 없습니다. 작업을 종료합니다.")
        return

    # 실제 발행 개수 계산
    real_count = min(want_count, remaining_quota, pending_count)
    print(f"▶ 이번 실행에서 실제 발행할 개수 : {real_count}")

    if real_count <= 0:
        print("발행 가능한 개수가 0개입니다. 작업을 종료합니다.")
        return

    # 배치 ID 부여
    batch_id = get_next_batch_id(rows)
    print(f"이번 배치 ID : {batch_id}")
    print()

    # 발행 실행
    today_str = date.today().isoformat()
    now_time = datetime.now().strftime("%H:%M:%S")

    for i, pending_file in enumerate(pending_files[:real_count], start=1):
        filename = pending_file.name
        src = pending_file
        dest = POSTS_DIR / filename
        backup = PUBLISHED_DIR / filename

        # 폴더 보장
        POSTS_DIR.mkdir(parents=True, exist_ok=True)
        PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)

        # pending -> posts 이동
        shutil.move(str(src), str(dest))
        # posts -> published 복사 (백업)
        shutil.copy2(str(dest), str(backup))

        # 로그 한 줄 추가
        row = {
            "date": today_str,
            "time": now_time,
            "batch_id": str(batch_id),
            "filename": filename,
            "src": str(src.relative_to(PROJECT_ROOT)),
            "dest": str(dest.relative_to(PROJECT_ROOT)),
            "backup": str(backup.relative_to(PROJECT_ROOT)),
            "rolled_back": "0",
        }
        rows.append(row)

        print(f"[{i}/{real_count}] 발행 완료 : {filename}")

    # 로그 저장
    write_log_rows(rows)

    print()
    print(f"🎉 이번 실행에서 발행한 파일 수 : {real_count}개")
    print(f"📊 오늘 누적 발행 수(롤백 안 된 것 기준) : {get_today_count(rows)}개")
    print("이제 필요하면 build_site.py 로 Hugo 빌드를 돌리면 됩니다.")


if __name__ == "__main__":
    main()
