# validate_site.py
# public/ 폴더 안의 HTML 파일들을 점검하는 스크립트

from pathlib import Path
from html.parser import HTMLParser


class SimpleHTMLChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.title = ""
        self.has_meta_description = False
        self.has_canonical = False
        self.h1_count = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs_dict = {k.lower(): v for k, v in attrs}

        if tag == "title":
            self.in_title = True

        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            content = attrs_dict.get("content", "")
            if name == "description" and content.strip():
                self.has_meta_description = True

        elif tag == "link":
            rel = attrs_dict.get("rel", "").lower()
            href = attrs_dict.get("href", "")
            # rel="canonical" 이고 href 있으면 canonical 있다고 판단
            if "canonical" in rel and href.strip():
                self.has_canonical = True

        elif tag == "h1":
            self.h1_count += 1

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data.strip()


def check_html_file(html_path: Path):
    """하나의 HTML 파일을 열어서 기본 요소를 점검한다."""
    text = html_path.read_text(encoding="utf-8", errors="ignore")

    parser = SimpleHTMLChecker()
    parser.feed(text)

    issues = []

    if not parser.title:
        issues.append("title 없음")

    if not parser.has_meta_description:
        issues.append("meta description 없음")

    if not parser.has_canonical:
        issues.append("canonical 없음")

    if parser.h1_count == 0:
        issues.append("h1 없음")

    return issues


def main():
    # 이 파일 기준으로 프로젝트 루트(mold-factory) 찾기
    script_path = Path(__file__).resolve()
    project_root = script_path.parents[2]  # .../automation/generator/ -> .../mold-factory/
    public_folder = project_root / "public"

    print("=== Hugo 빌드 결과 HTML 점검 시작 (validate_site.py) ===")
    print(f"프로젝트 루트 : {project_root}")
    print(f"public 폴더   : {public_folder}\n")

    if not public_folder.exists():
        print("❌ public 폴더가 없습니다. 먼저 build_site.py 로 빌드를 해주세요.")
        return

    html_files = sorted(public_folder.rglob("*.html"))

    if not html_files:
        print("❌ public 폴더 안에 HTML 파일이 없습니다.")
        return

    total = len(html_files)
    ok_count = 0
    issue_count = 0
    detailed_problems = []

    print(f"검색된 HTML 파일 개수: {total}\n")

    for html_path in html_files:
        rel_path = html_path.relative_to(public_folder)
        issues = check_html_file(html_path)

        if issues:
            issue_count += 1
            detailed_problems.append((rel_path, issues))
        else:
            ok_count += 1

    # 요약 출력
    print("=== 점검 결과 요약 ===")
    print(f"✅ 문제 없는 페이지: {ok_count}개")
    print(f"⚠️  점검이 필요한 페이지: {issue_count}개\n")

    # 문제 있는 파일 상세 출력
    if detailed_problems:
        print("=== ⚠️ 세부 문제 목록 ===")
        for rel_path, issues in detailed_problems:
            issue_list_str = ", ".join(issues)
            print(f"- {rel_path} -> {issue_list_str}")
    else:
        print("🎉 모든 HTML 파일이 기본 요건(title/meta/canonical/h1)을 만족합니다!")

    print("\n=== 점검 종료 ===")


if __name__ == "__main__":
    main()
