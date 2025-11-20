import os
import shutil
from datetime import datetime

# ----------------------------
# 기본 경로 설정
# ----------------------------
PROJECT_ROOT = r"C:\sites\mold-factory"
PENDING = os.path.join(PROJECT_ROOT, "pending")
PUBLISHED = os.path.join(PROJECT_ROOT, "published")
POSTS = os.path.join(PROJECT_ROOT, "content", "posts")

# ----------------------------
# 안전 로그 기록
# ----------------------------
LOG_FILE = os.path.join(PROJECT_ROOT, "publish_log.txt")

def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {msg}\n")
    print(msg)

# ----------------------------
# 폴더 존재 여부 체크
# ----------------------------
def ensure_folders():
    for folder in [PENDING, PUBLISHED, POSTS]:
        if not os.path.exists(folder):
            os.makedirs(folder)

# ----------------------------
# 자동 회귀(rollback)
# ----------------------------
def rollback(moved_files):
    log("⚠ 오류 발생! 자동 복구(rollback)을 시작합니다.")

    for src, dst in moved_files:
        try:
            shutil.move(dst, src)
            log(f"  ↩ 복구됨: {os.path.basename(src)}")
        except:
            log(f"  ❌ 복구 실패: {os.path.basename(src)}")

    log("rollback 완료.\n")

# ----------------------------
# 발행 기능
# ----------------------------
def publish_today(limit):
    ensure_folders()
    pending_files = sorted(os.listdir(PENDING))

    if not pending_files:
        log("📭 pending 폴더가 비어 있습니다. 발행할 파일 없음.")
        return

    count = min(limit, len(pending_files))
    log(f"오늘 발행할 개수: {count}")

    moved_records = []

    try:
        for i in range(count):
            fname = pending_files[i]

            src = os.path.join(PENDING, fname)
            dst_posts = os.path.join(POSTS, fname)
            dst_published = os.path.join(PUBLISHED, fname)

            # -------- posts 폴더 이동 --------
            shutil.move(src, dst_posts)
            moved_records.append((src, dst_posts))
            log(f"  📌 posts 이동 완료: {fname}")

            # -------- published 백업 --------
            shutil.copy(dst_posts, dst_published)
            log(f"  📦 published 백업 완료: {fname}")

        log(f"🎉 오늘 발행 완료! 총 {count}개")

    except Exception as e:
        log(f"❌ 오류 발생: {e}")
        rollback(moved_records)

# ----------------------------
# 실행
# ----------------------------
if __name__ == "__main__":
    print("=== 하루 발행 스크립트 (안정 모드) 시작 ===")
    try:
        amount = int(input("오늘 몇 개를 발행할까요? : "))
        publish_today(amount)
    except ValueError:
        print("❌ 숫자를 입력해야 합니다.")
