# preview_site.py
# Hugo 로컬 미리보기 서버 자동 실행 스크립트

import subprocess
from pathlib import Path

def main():
    # 이 파일 위치 기준으로 프로젝트 루트(mold-factory) 자동 계산
    script_path = Path(__file__).resolve()
    project_root = script_path.parents[2]  # ...\automation\generator\ -> ...\mold-factory\

    print("=== Hugo 로컬 미리보기 서버 실행 ===")
    print(f"프로젝트 루트 : {project_root}")
    print("서버를 종료하려면 창에서 Ctrl + C 를 누르세요.\n")

    # hugo server -D 실행 (초안 포함 미리보기)
    cmd = ["hugo", "server", "-D"]

    try:
        subprocess.run(cmd, cwd=project_root)
    except KeyboardInterrupt:
        print("\n서버를 종료했습니다. (KeyboardInterrupt)")
    except Exception as e:
        print("\n[오류] Hugo 서버 실행 중 문제가 발생했습니다.")
        print(e)

if __name__ == "__main__":
    main()
