#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import random
import re
from pathlib import Path
from datetime import datetime

# 이미 존재하는 index.md가 있을 때 덮어쓸지 여부
# 대량 수정 테스트 중엔 True, 실서비스 들어가면 False로 바꾸면 됨.
OVERWRITE_IF_EXISTS = True

DEFAULT_DATE_FMT = "%Y-%m-%dT%H:%M:%S+09:00"


def get_project_root() -> Path:
    """
    automation/ 폴더 기준으로 프로젝트 루트(mold-factory) 찾기
    """
    return Path(__file__).resolve().parents[1]


def ensure_directories(root: Path):
    """
    필요한 기본 폴더 생성
    """
    (root / "content" / "posts").mkdir(parents=True, exist_ok=True)
    (root / "automation" / "logs").mkdir(parents=True, exist_ok=True)


def slugify(keyword: str) -> str:
    """
    키워드로부터 URL용 slug 생성
    """
    s = keyword.strip().lower()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^0-9a-z가-힣\-]", "", s)
    s = re.sub(r"-{2,}", "-", s)
    return s or "post"


def load_products(csv_path: Path) -> dict:
    """
    products.csv를 읽어서
    { keyword: {title, desc, price, url} } 형태의 딕셔너리로 반환
    """
    products = {}
    if not csv_path.exists():
        print("[INFO] products.csv 없음 → product_block은 기본 문구 사용")
        return products

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row.get("keyword") or "").strip()
            if not key:
                continue
            products[key] = {
                "title": (row.get("product_title") or "").strip(),
                "desc": (row.get("product_desc") or "").strip(),
                "price": (row.get("product_price") or "").strip(),
                "url": (row.get("product_url") or "").strip(),
            }
    return products


# ---------- E3-2: 요약(summary) 자동 생성 함수 ----------

def generate_summary(keyword: str, manual_summary: str) -> str:
    """
    CSV에 summary가 있으면 그대로 사용,
    없으면 키워드 기반 템플릿으로 한 줄 요약 자동 생성
    """
    manual_summary = (manual_summary or "").strip()
    if manual_summary:
        return manual_summary

    templates = [
        f"{keyword}가 생기는 원인과, 집에서 쉽게 해결하는 방법을 한 번에 정리한 가이드입니다.",
        f"{keyword} 때문에 고민일 때, 원인 정리부터 실제 해결 순서까지 차근차근 정리해 드립니다.",
        f"처음 보는 사람도 따라 할 수 있도록 {keyword} 해결 방법을 단계별로 설명한 페이지입니다.",
        f"{keyword} 문제를 줄이고 재발을 막는 데 도움이 되는 관리 팁을 모아 정리했습니다.",
        f"{keyword}를 빠르게 정리하고, 다시 생기지 않도록 예방하는 방법까지 한 번에 확인할 수 있습니다.",
    ]
    return random.choice(templates)


# -------------------------------------------------------

def main():
    root = get_project_root()
    ensure_directories(root)

    template_path = root / "automation" / "templates" / "base.md"
    csv_path = root / "automation" / "data" / "keywords.csv"
    products_csv_path = root / "automation" / "data" / "products.csv"
    log_path = root / "automation" / "logs" / "generate_log.csv"

    if not template_path.exists():
        print(f"[ERROR] base.md 템플릿이 없습니다: {template_path}")
        return
    if not csv_path.exists():
        print(f"[ERROR] keywords.csv 파일이 없습니다: {csv_path}")
        return

    # 상품 정보 로딩 (E2)
    products = load_products(products_csv_path)

    # 템플릿 읽기
    base_template = template_path.read_text(encoding="utf-8")

    # 날짜 문자열 (지금 시간 기준)
    now_str = datetime.now().strftime(DEFAULT_DATE_FMT)

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            keyword = (row.get("keyword") or "").strip()
            summary_raw = (row.get("summary") or "").strip()

            if not keyword:
                continue

            slug = slugify(keyword)

            # --- E3-2: 요약 자동 생성 적용 ---
            summary = generate_summary(keyword, summary_raw)

            # --- E3-3: 본문 고도화 (introduction / cause / solution / tip) ---

            # 도입부: 공감 + 목표
            introduction = (
                f"{keyword} 때문에 매번 청소할 때마다 스트레스를 받는 분들이 많습니다.\n"
                f"이 글에서는 처음 해보는 사람도 따라 할 수 있도록, {keyword}를 안전하고 꾸준하게 정리하는 방법을 단계별로 정리해 드릴게요."
            )

            # 원인 블록: 3가지 정도로 구조화
            cause_block = (
                f"- **습기와 물기**: {keyword}는 대부분 물기가 마르지 못하고 오래 남아 있을 때 잘 생깁니다.\n"
                f"- **오염과 찌꺼기 누적**: 세제 찌꺼기나 비누 거품, 먼지 등이 쌓이면 {keyword}가 자라기 좋은 환경이 됩니다.\n"
                f"- **환기 부족**: 사용 후 문을 꽉 닫아두거나 공기가 잘 통하지 않는 구조라면, 안쪽이 눅눅해지면서 문제가 반복될 수 있습니다."
            )

            # 해결 블록: 준비물 / 1차 / 2차 / 마무리 구조
            solution_block = (
                f"1. **상태 먼저 점검하기**  \n"
                f"   - {keyword}가 생긴 위치(모서리, 고무 패킹, 틈새 등)와 범위를 눈으로 확인합니다.\n"
                f"   - 곰팡이·때가 심한 구역과 그렇지 않은 구역을 대략 나눠두면 이후 관리가 편해집니다.\n\n"
                f"2. **기본 준비물 챙기기**  \n"
                f"   - 고무장갑, 부드러운 솔이나 칫솔, 마른 천이나 키친타월을 준비합니다.\n"
                f"   - 집에 있는 중성세제 또는 전용 세정제가 있다면 함께 준비해 주세요.\n\n"
                f"3. **1차로 부드럽게 닦아내기**  \n"
                f"   - 세제를 묻힌 후 {keyword}가 보이는 부분을 너무 세게 문지르지 말고, 여러 번에 나눠서 부드럽게 닦아줍니다.\n"
                f"   - 틈새나 모서리는 칫솔을 이용하면 상대적으로 쉽게 정리할 수 있습니다.\n\n"
                f"4. **필요하면 2차로 집중 관리하기**  \n"
                f"   - 한 번에 지워지지 않는 부분은 세제를 조금 더 묻힌 뒤 10~20분 정도 둔 다음 다시 문질러 주세요.\n"
                f"   - 전용 곰팡이 제거제나 세정제를 쓸 경우, 제품 설명에 적힌 사용 시간과 환기 방법을 반드시 지켜주는 것이 중요합니다.\n\n"
                f"5. **마무리로 충분히 헹구고 건조시키기**  \n"
                f"   - 세제를 깨끗이 헹궈낸 뒤, 마른 천으로 최대한 물기를 닦아줍니다.\n"
                f"   - 가능하다면 반나절 이상 문을 열어 두거나, 선풍기·환풍기를 이용해 충분히 말려주는 것이 좋습니다.\n\n"
                f"6. **다음에 덜 힘들게 만드는 습관 만들기**  \n"
                f"   - 한 번에 완벽하게 없애려 하기보다, 앞으로는 한 달에 한 번 정도 가볍게 닦아주는 루틴을 만드는 것이 더 효율적입니다."
            )

            # 팁 블록: 현실적인 관리 팁
            tip_block = (
                f"- 오늘 한 번에 완벽하게 끝내려 하기보다, **2~3번에 나눠서** 조금씩 정리한다고 생각하면 마음이 한결 편합니다.\n"
                f"- {keyword}가 잘 생기는 구역은 스마트폰 알림이나 캘린더에 \"10분만 청소\" 같은 메모를 남겨두면 꾸준히 관리하는 데 도움이 됩니다.\n"
                f"- 계절이 바뀌는 시기(환절기·장마철 전후)에 한 번씩 집중 관리해 두면, 평소에는 훨씬 가볍게 정리할 수 있습니다.\n"
                f"- 세정제나 제거제를 새로 사용할 때는, 눈에 잘 안 보이는 작은 구역에 먼저 테스트해 본 뒤 전체에 사용하는 것이 안전합니다."
            )

            # --- 상품 블록 (E2 자동 삽입) ---
            prod = products.get(keyword)
            if prod and prod["title"] and prod["url"]:
                product_block = (
                    f'<div class="product-card">\n'
                    f'  <p><strong>{prod["title"]}</strong></p>\n'
                    f'  <p>{prod["desc"]}</p>\n'
                    f'  <p>가격: {prod["price"]}</p>\n'
                    f'  <p><a href="{prod["url"]}" target="_blank" rel="nofollow">상품 보러가기</a></p>\n'
                    f'</div>'
                )
            else:
                # products.csv에 매칭되는 상품이 없을 때 기본 문구
                product_block = (
                    f"- {keyword} 상황에 맞는 전용 세정제나 제거제를 함께 사용하면 시간을 아끼면서 더 확실한 효과를 얻을 수 있습니다.\n"
                    f"- AliExpress / Temu 등 해외 쇼핑몰과 연동하면 저렴한 제품을 자동으로 추천하는 구조로 확장할 수 있습니다."
                )

            # --- FAQ 자동 생성 (E3-1 업그레이드) ---
            faq_templates = [
                ("얼마나 걸리나요?", f"{keyword} 문제는 보통 2~7일 정도 꾸준히 관리하면 눈에 띄게 개선되는 경우가 많습니다."),
                ("다시 생기지 않게 하려면?", f"{keyword} 예방의 핵심은 건조와 환기이며, 사용 후 물기와 오염을 최대한 빨리 제거해 주는 습관이 중요합니다."),
                ("집에 있는 세제로도 되나요?", f"초기 단계라면 기본 세제로도 어느 정도 관리가 가능하지만, 심하거나 오래된 경우에는 전용 제품을 함께 사용하는 것이 좋습니다."),
                ("전문 업체를 불러야 하나요?", f"대부분의 {keyword} 문제는 셀프로도 충분히 관리할 수 있지만, 범위가 넓고 오래 방치된 경우에는 전문가 도움을 받는 것이 시간·체력 면에서 유리할 수 있습니다."),
                ("얼마나 자주 관리해야 하나요?", f"일반적으로 한 달에 1~2번 정도만 정기적으로 관리해도 {keyword}가 심해지는 것을 충분히 예방할 수 있습니다."),
                ("냄새가 심할 때는?", f"{keyword}와 함께 냄새가 심하다면, 우선 환기와 건조를 해 준 뒤 냄새 전용 탈취제나 소독제를 병행하면 효과가 좋습니다."),
                ("어떤 제품을 쓰면 좋나요?", f"{keyword} 전용 세정제·제거제를 함께 사용하면 전체 관리 시간과 노력은 줄이고, 눈에 보이는 개선 속도는 더 빠르게 만들 수 있습니다."),
            ]

            selected_faqs = random.sample(faq_templates, 5)

            faq_block = ""
            for q, a in selected_faqs:
                faq_block += f"**Q. {keyword}는 {q}**\nA. {a}\n\n"

            # --- 템플릿 치환 ---
            content = base_template
            content = content.replace("{{keyword}}", keyword)
            content = content.replace("{{date}}", now_str)
            content = content.replace("{{slug}}", slug)
            content = content.replace("{{summary}}", summary)
            content = content.replace("{{introduction}}", introduction)
            content = content.replace("[[cause_block]]", cause_block)
            content = content.replace("[[solution_block]]", solution_block)
            content = content.replace("[[product_block]]", product_block)
            content = content.replace("[[tip_block]]", tip_block)
            content = content.replace("[[faq_block]]", faq_block)

            # --- 파일 생성 ---
            post_dir = root / "content" / "posts" / slug
            post_dir.mkdir(parents=True, exist_ok=True)
            post_path = post_dir / "index.md"

            if post_path.exists() and not OVERWRITE_IF_EXISTS:
                print(f"[SKIP] 이미 존재 → {keyword} ({post_path})")
                continue

            post_path.write_text(content, encoding="utf-8")
            print(f"[OK] 생성됨 → {post_path}")

            # 로그 기록
            with log_path.open("a", encoding="utf-8") as logf:
                logf.write(f"{now_str},{keyword},{slug}\n")


if __name__ == "__main__":
    main()
