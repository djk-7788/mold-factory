# keywords_to_posts.py
# 키워드 CSV -> pending 폴더에 Hugo용 .md 초안 자동 생성 (C-3 버전)

import csv
import os
import random
import re
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------
# 기본 경로 설정
# ---------------------------
# 이 파일 위치: mold-factory/automation/generator/keywords_to_posts.py
# 프로젝트 루트: mold-factory/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

KEYWORD_CSV = PROJECT_ROOT / "automation" / "keywords" / "generated_keywords.csv"
PENDING_DIR = PROJECT_ROOT / "pending"          # 큐 대기 폴더
CONTENT_POSTS_DIR = PROJECT_ROOT / "content" / "posts"  # 참조용(출력 경로 아님!)

# ---------------------------
# 슬러그 만들기 유틸
# ---------------------------

def slugify(text: str) -> str:
    """
    키워드에서 파일/slug로 쓸 안전한 문자열 만들기
    - 공백 -> -
    - 특수문자 제거
    - 한글은 그대로 두고, 영어는 소문자로
    """
    text = text.strip()

    # 괄호 안 "변형" 표시는 제거 (예: "욕실 곰팡이 제거 방법 (1 변형)")
    text = re.sub(r"\([^)]*변형[^)]*\)", "", text).strip()

    # 공백류를 모두 하나의 공백으로
    text = re.sub(r"\s+", " ", text)

    # 공백 -> 하이픈
    text = text.replace(" ", "-")

    # 파일명에 안 좋은 특수문자 제거
    text = re.sub(r"[^\w\-가-힣]", "", text)

    # 하이픈 중복 제거
    text = re.sub(r"-{2,}", "-", text)

    return text.strip("-")


# ---------------------------
# 날짜 랜덤 생성 유틸
# ---------------------------

def random_past_datetime(days_back_min: int = 30, days_back_max: int = 120) -> datetime:
    """
    오늘 기준 과거 랜덤 날짜 생성
    - days_back_min ~ days_back_max 범위의 일수만큼 과거로
    """
    days_back = random.randint(days_back_min, days_back_max)
    base_date = datetime.now() - timedelta(days=days_back)

    # 랜덤 시/분/초 섞기
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    return base_date.replace(hour=hour, minute=minute, second=second, microsecond=0)


# ---------------------------
# 본문 텍스트 생성 (아주 심플한 템플릿)
# ---------------------------

def build_body(keyword: str) -> str:
    """
    키워드 하나를 받아서 기본 설명/원인/해결법 섹션이 있는
    간단한 한국어 본문을 만들어 준다.
    실제 운영하면서 텍스트 템플릿은 마음껏 바꿔도 됨.
    """
    return f"""
계속 반복되는 '{keyword}' 문제를 해결하려면,
먼저 원인을 대략이라도 짚어 보는 게 중요합니다.
전문 업체를 부르기 전에 스스로 점검해 볼 수 있는 기본 관리 방법들을 정리했습니다.

왜 이런 문제가 생길까요?
- 집 안에서 '{keyword}'가 특히 자주 보이는 위치가 있을 수 있습니다.
- 환기가 잘 되지 않거나, 물기가 자주 남는 공간일 수 있습니다.
- 청소는 하고 있지만, 세정제 사용법이나 순서가 맞지 않을 수도 있습니다.

이렇게 해결해 보세요
1. 오늘 한 번만이라도 '{keyword}'가 생기는 위치를 자세히 관찰해 보세요.
2. 물기가 자주 남는 곳이라면, 한동안은 의도적으로 환기와 건조 시간을 늘려 줍니다.
3. 세정제나 도구를 여러 개 섞어 쓰기보다, 한 번에 한 가지씩 사용해 보세요.
4. 1주일 정도만 같은 패턴으로 관리해 보고, 변화가 있는지 체크합니다.

작은 관리 팁
- 하루에 몇 분만 투자해도 '{keyword}' 문제를 꽤 줄일 수 있습니다.
- 너무 완벽하게 해결하려고 하기보다, "조금 더 나아지는 것"에 집중해 보세요.
- 어느 정도 기준이 잡히면, 그때 필요한 용품을 천천히 찾아도 늦지 않습니다.
""".strip() + "\n"


# ---------------------------
# 키워드 CSV 읽기
# ---------------------------

def load_keywords(csv_path: Path):
    if not csv_path.exists():
        print(f"[오류] 키워드 CSV 파일을 찾을 수 없습니다: {csv_path}")
        return []

    keywords = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        # 컬럼 이름이 'keyword' 라고 가정
        if "keyword" not in reader.fieldnames:
            print("[오류] CSV 첫 줄에 'keyword' 헤더가 있어야 합니다.")
            print(f"현재 헤더: {reader.fieldnames}")
            return []

        for row in reader:
            kw = (row.get("keyword") or "").strip()
            if kw:
                keywords.append(kw)

    return keywords


# ---------------------------
# 메인 로직
# ---------------------------

def main():
    print("=== 키워드 → pending/.md 자동 생성기 (C-3 버전) 시작 ===\n")

    print(f"키워드 CSV : {KEYWORD_CSV}")
    print(f"대기 폴더(pending) : {PENDING_DIR}")
    print(f"(참고) Hugo posts 폴더 : {CONTENT_POSTS_DIR}\n")

    # 폴더 없으면 만들기
    PENDING_DIR.mkdir(parents=True, exist_ok=True)

    # 1) 키워드 로드
    keywords = load_keywords(KEYWORD_CSV)
    if not keywords:
        print("[오류] 사용할 키워드를 찾지 못했습니다. CSV 내용을 확인해 주세요.")
        return

    total = len(keywords)
    print(f"불러온 키워드 개수: {total}")

    # 2) 몇 개 사용할지 확인
    raw_n = input("이번 실행에서 사용할 키워드 개수는 몇 개로 할까요? (예: 5, 엔터시 전체): ").strip()
    if raw_n:
        try:
            n = int(raw_n)
            n = max(1, min(n, total))
        except ValueError:
            print("숫자가 아니라서 전체 키워드를 사용합니다.")
            n = total
    else:
        n = total

    # 키워드 섞어서 상위 n개 사용
    random.shuffle(keywords)
    use_keywords = keywords[:n]

    # 3) 키워드당 변형 개수
    raw_v = input("키워드당 몇 개의 변형 페이지를 만들까요? (예: 3): ").strip()
    try:
        variants_per_keyword = max(1, int(raw_v))
    except ValueError:
        variants_per_keyword = 1

    print(f"\n▶ 실제 사용할 키워드 개수 : {len(use_keywords)}")
    print(f"▶ 키워드당 변형 페이지 수 : {variants_per_keyword}\n")

    created_files = []

    # 4) 생성 루프
    for idx, kw in enumerate(use_keywords, start=1):
        print(f"[{idx}/{len(use_keywords)}] 키워드: {kw}")

        base_slug = slugify(kw)
        if not base_slug:
            print("  → 슬러그를 만들 수 없어 건너뜁니다.")
            continue

        for v in range(1, variants_per_keyword + 1):
            # v1, v2 ... 형태로 변형 버전 부여
            slug = f"{base_slug}-v{v}"

            # 파일 경로: pending/슬러그.md
            filename = f"{slug}.md"
            out_path = PENDING_DIR / filename

            # 혹시 중복 파일이 이미 있다면 살짝 이름 변경
            dup_counter = 2
            while out_path.exists():
                alt_slug = f"{base_slug}-v{v}-{dup_counter}"
                filename = f"{alt_slug}.md"
                out_path = PENDING_DIR / filename
                slug = alt_slug
                dup_counter += 1

            # 랜덤 과거 날짜
            dt = random_past_datetime()
            date_str = dt.isoformat(timespec="seconds")

            title = kw  # 타이틀은 일단 키워드 그대로 사용
            summary = f"{kw}에 대한 생활 문제 해결 가이드입니다."

            body = build_body(kw)

            # TOML front matter + 본문 조립
            front_matter = f"""+++
title = "{title}"
date = "{date_str}"
draft = false
summary = "{summary}"
slug = "{slug}"
+++
"""

            content = front_matter + "\n" + body

            # 파일 쓰기
            with out_path.open("w", encoding="utf-8") as f:
                f.write(content)

            print(f"  ✅ 생성 완료: {out_path}")
            created_files.append(out_path)

    print("\n=== 작업 완료! 이번 실행에서 생성된 파일 수 :", len(created_files), "===")
    if created_files:
        print("이제 'daily_publish.py'를 사용해서 하루 발행 개수를 조절하면서")
        print("Hugo 사이트에 조금씩 발행하면 됩니다.")
    else:
        print("생성된 파일이 없습니다. CSV나 입력값을 다시 확인해 주세요.")


if __name__ == "__main__":
    main()
