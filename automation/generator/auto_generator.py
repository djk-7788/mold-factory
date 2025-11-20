import random
import datetime
from pathlib import Path


# --- 경로 설정 -----------------------------------------------------

# 이 파일(auto_generator.py)이 있는 위치 기준으로 경로 계산
GENERATOR_DIR = Path(__file__).resolve().parent          # ...\automation\generator
AUTOMATION_DIR = GENERATOR_DIR.parent                    # ...\automation
PROJECT_ROOT = AUTOMATION_DIR.parent                     # ...\mold-factory

TEMPLATES_DIR = AUTOMATION_DIR / "templates"             # ...\automation\templates
POSTS_DIR = PROJECT_ROOT / "content" / "posts"           # ...\content\posts


# --- 유틸 함수들 ----------------------------------------------------


def load_lines(path: Path):
    """한 줄에 하나씩 들어있는 텍스트 파일 불러오기 (빈 줄은 무시)."""
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            lines.append(line)
    return lines


def load_blocks(path: Path):
    """FAQ 같이 여러 줄로 된 블록들을 불러올 때 사용.
    빈 줄 기준으로 블록을 나눈다.
    """
    text = path.read_text(encoding="utf-8")
    blocks = [block.strip() for block in text.split("\n\n") if block.strip()]
    return blocks


def sanitize_for_toml(text: str) -> str:
    """TOML 문자열 안에 들어갈 때 큰따옴표를 안전하게 바꿔준다."""
    return text.replace('"', "'")


# --- 템플릿 로딩 ----------------------------------------------------


def load_templates():
    """templates 폴더에서 각종 템플릿들을 불러온다."""
    templates = {}

    paths = {
        "intro": TEMPLATES_DIR / "intro.txt",
        "body": TEMPLATES_DIR / "body.txt",
        "causes": TEMPLATES_DIR / "causes.txt",
        "solutions": TEMPLATES_DIR / "solutions.txt",
        "tips": TEMPLATES_DIR / "tips.txt",
        "outro": TEMPLATES_DIR / "outro.txt",
        "faq": TEMPLATES_DIR / "faq.txt",
    }

    # 필수 파일 존재 확인
    for key, path in paths.items():
        if not path.exists():
            raise FileNotFoundError(f"템플릿 파일이 없습니다: {path}")

    templates["intro"] = load_lines(paths["intro"])
    templates["body"] = load_lines(paths["body"])
    templates["causes"] = load_lines(paths["causes"])
    templates["solutions"] = load_lines(paths["solutions"])
    templates["tips"] = load_lines(paths["tips"])
    templates["outro"] = load_lines(paths["outro"])
    templates["faq"] = load_blocks(paths["faq"])

    return templates


# --- MD 파일 생성 로직 ---------------------------------------------


def build_markdown(
    slug: str,
    title: str,
    summary: str,
    templates: dict,
    date_str: str = None,
) -> str:
    """하나의 포스트 내용을 템플릿에서 랜덤으로 조합해 MD 문자열을 만든다.

    date_str:
        - 외부에서 날짜 문자열(ISO 형식)을 넘겨주면 그 값을 사용하고
        - 넘겨주지 않으면(=None) 현재 시간을 사용한다.
    """

    # 날짜 (Hugo가 이해할 수 있는 형식)
    if date_str is None:
        date_str = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    intro = random.choice(templates["intro"])
    body_core = random.choice(templates["body"])
    outro = random.choice(templates["outro"])

    # 원인/해결/팁/FAQ는 중복되지 않게 샘플링 (개수 부족하면 그대로 사용)
    causes = random.sample(templates["causes"], k=min(3, len(templates["causes"])))
    solutions = random.sample(
        templates["solutions"], k=min(3, len(templates["solutions"]))
    )
    tips = random.sample(templates["tips"], k=min(2, len(templates["tips"])))
    faqs = random.sample(templates["faq"], k=min(3, len(templates["faq"])))

    title_safe = sanitize_for_toml(title)
    summary_safe = sanitize_for_toml(summary)

    front_matter = f"""+++
title = "{title_safe}"
date = "{date_str}"
draft = false
summary = "{summary_safe}"
slug = "{slug}"
+++
"""

    # 본문 구성
    md_parts = []

    md_parts.append(front_matter)
    md_parts.append("")  # 빈 줄

    md_parts.append(intro)
    md_parts.append("")
    md_parts.append(body_core)
    md_parts.append("")

    # 원인 섹션
    md_parts.append("## 왜 이런 문제가 생길까요?")
    md_parts.append("")
    for c in causes:
        md_parts.append(f"- {c}")
    md_parts.append("")

    # 해결 섹션
    md_parts.append("## 이렇게 해결해 보세요")
    md_parts.append("")
    for idx, s in enumerate(solutions, start=1):
        md_parts.append(f"{idx}. {s}")
    md_parts.append("")

    # 팁 섹션
    md_parts.append("## 작은 관리 팁")
    md_parts.append("")
    for t in tips:
        md_parts.append(f"- {t}")
    md_parts.append("")

    # FAQ 섹션
    md_parts.append("## 자주 묻는 질문")
    md_parts.append("")
    for block in faqs:
        md_parts.append(block)
        md_parts.append("")

    # 마무리
    md_parts.append(outro)
    md_parts.append("")

    return "\n".join(md_parts)


def generate_posts():
    print("=== 템플릿 기반 자동 포스트 생성기 시작 ===\n")
    print(f"프로젝트 루트: {PROJECT_ROOT}")
    print(f"출력 폴더: {POSTS_DIR}")
    print("템플릿 폴더:", TEMPLATES_DIR)
    print("")

    templates = load_templates()
    print("✅ 템플릿 로딩 완료!\n")

    base_slug = input(
        "기본 슬러그를 입력하세요 (예: bathroom-mold, kitchen-smell 등): "
    ).strip()
    base_title = input(
        "기본 제목을 입력하세요 (예: 욕실 곰팡이 깨끗하게 없애는 방법): "
    ).strip()
    summary = input(
        "요약 문장을 입력하세요 (검색 결과에 보일 짧은 설명): "
    ).strip()

    if not base_slug:
        print("❌ 슬러그는 반드시 필요합니다. 프로그램을 종료합니다.")
        return

    try:
        count_str = input("몇 개의 변형 페이지를 만들까요? (예: 5): ").strip()
        count = int(count_str)
    except ValueError:
        print("❌ 숫자를 제대로 입력하지 않아 기본값 1개만 생성합니다.")
        count = 1

    if count < 1:
        print("❌ 최소 1개 이상이어야 합니다. 1개만 생성합니다.")
        count = 1

    POSTS_DIR.mkdir(parents=True, exist_ok=True)

    for i in range(1, count + 1):
        if count == 1:
            slug = base_slug
            title = base_title
        else:
            slug = f"{base_slug}-{i}"
            title = f"{base_title} ({i} 변형)"

        # 여기서는 date_str를 넘기지 않으므로 자동으로 "현재 시간" 사용
        md_content = build_markdown(slug, title, summary, templates)
        output_path = POSTS_DIR / f"{slug}.md"
        output_path.write_text(md_content, encoding="utf-8")

        print(f"✅ 생성 완료: {output_path}")

    print("\n=== 모든 작업 완료! Hugo에서 빌드해보세요. ===")


if __name__ == "__main__":
    generate_posts()
