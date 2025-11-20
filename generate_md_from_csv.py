import csv
import os
import datetime

# CSV 파일 이름 (mold-factory 바로 아래)
CSV_PATH = "keywords.csv"

# Hugo 포스트가 들어가는 폴더
OUTPUT_DIR = os.path.join("content", "posts")


def toml_escape(s: str) -> str:
    """TOML에서 문제될 수 있는 문자 간단히 처리"""
    if s is None:
        return ""
    return s.replace("\n", " ").replace("\r", " ").replace('"', '\\"')


def make_toml_array(values):
    """빈값 빼고 TOML 배열 문자열로 변환"""
    cleaned = [v for v in values if v]  # 빈 문자열 제거
    if not cleaned:
        return None
    inner = ", ".join(f'"{toml_escape(v)}"' for v in cleaned)
    return f"[{inner}]"


def main():
    print("CSV → MD 자동 생성 시작!")

    base_dir = os.getcwd()
    print(f"현재 작업 폴더: {base_dir}")

    # 출력 폴더 확인 (없으면 생성)
    full_output_dir = os.path.join(base_dir, OUTPUT_DIR)
    os.makedirs(full_output_dir, exist_ok=True)
    print(f"출력 폴더: {full_output_dir}")

    # CSV 열기
    try:
        f = open(CSV_PATH, newline="", encoding="utf-8-sig")
    except FileNotFoundError:
        print(f"ERROR: {CSV_PATH} 파일을 찾을 수 없습니다.")
        print("→ C:\\sites\\mold-factory 폴더 안에 keywords.csv가 있는지 확인해주세요.")
        return

    with f:
        reader = csv.DictReader(f)

        count = 0
        for row in reader:
            slug = (row.get("slug") or "").strip()
            if not slug:
                print("경고: slug가 비어 있어 이 행은 건너뜁니다.")
                continue

            title = (row.get("title") or "").strip()
            summary = (row.get("summary") or "").strip()

            causes = [
                (row.get("cause1") or "").strip(),
                (row.get("cause2") or "").strip(),
                (row.get("cause3") or "").strip(),
            ]
            solutions = [
                (row.get("solution1") or "").strip(),
                (row.get("solution2") or "").strip(),
                (row.get("solution3") or "").strip(),
            ]
            tips = [
                (row.get("tip1") or "").strip(),
                (row.get("tip2") or "").strip(),
            ]

            body = (row.get("body") or "").strip()

            now = datetime.datetime.now().isoformat()

            # --- front matter(TOML) 만들기 ---
            front_lines = []
            front_lines.append("+++")
            front_lines.append(f'title = "{toml_escape(title)}"')
            front_lines.append(f'date = "{now}"')
            front_lines.append("draft = false")

            if summary:
                front_lines.append(f'summary = "{toml_escape(summary)}"')

            causes_array = make_toml_array(causes)
            if causes_array:
                front_lines.append(f"causes = {causes_array}")

            solutions_array = make_toml_array(solutions)
            if solutions_array:
                front_lines.append(f"solutions = {solutions_array}")

            tips_array = make_toml_array(tips)
            if tips_array:
                front_lines.append(f"tips = {tips_array}")

            front_lines.append("+++")
            front_lines.append("")  # 빈 줄 하나

            if body:
                front_lines.append(body)

            content = "\n".join(front_lines)

            # 파일 저장 경로: content/posts/slug.md
            filename = f"{slug}.md"
            output_path = os.path.join(full_output_dir, filename)

            with open(output_path, "w", encoding="utf-8") as out_f:
                out_f.write(content)

            print(f"생성 완료: {output_path}")
            count += 1

    print(f"\n총 생성된 파일 개수: {count}개")


if __name__ == "__main__":
    main()
