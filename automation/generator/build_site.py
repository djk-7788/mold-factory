import subprocess
import os
from pathlib import Path
from datetime import datetime

# ======================================
# 경로 설정
# ======================================
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]   # mold-factory/
PUBLIC_DIR = PROJECT_ROOT / "public"
LOGS_DIR = PROJECT_ROOT / "automation" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

BUILD_LOG = LOGS_DIR / "build_log.txt"


def log(message):
    """로그 출력 + 파일 기록"""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{timestamp} {message}"
    print(line)
    with BUILD_LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_hugo_build():
    """Hugo 빌드 실행"""
    log("🚀 Hugo 빌드를 시작합니다...")

    start_time = datetime.now()

    process = subprocess.Popen(
        ["hugo"],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )

    stdout, stderr = process.communicate()
    duration = datetime.now() - start_time

    # 콘솔 출력 & 로그 저장
    log("=== Hugo STDOUT ===")
    for line in stdout.splitlines():
        log(line)

    if stderr.strip():
        log("=== Hugo STDERR ===")
        for line in stderr.splitlines():
            log(line)

    # 종료 코드 체크
    if process.returncode != 0:
        log(f"❌ Hugo 빌드 실패! returncode={process.returncode}")
        return False, duration
    else:
        log("🎉 Hugo 빌드 성공!")
        return True, duration


def count_public_html():
    """public 폴더 내 HTML 파일 수 집계"""
    if not PUBLIC_DIR.exists():
        return 0

    html_files = list(PUBLIC_DIR.rglob("*.html"))
    return len(html_files)


def main():
    print("=== Hugo 자동 빌드 스크립트 시작 ===")
    log("\n========== 새로운 빌드 시작 ==========")

    success, duration = run_hugo_build()

    log(f"⏱ 빌드 소요 시간: {duration}")

    if success:
        html_count = count_public_html()
        log(f"📄 public 디렉토리 내 HTML 파일 총 개수: {html_count}")
        log("🔥 빌드 완료. 사이트가 배포 가능한 상태입니다.")
    else:
        log("🚨 빌드 실패. 로그를 확인하세요.")

    print("\n=== 빌드 작업 종료 ===")


if __name__ == "__main__":
    main()
