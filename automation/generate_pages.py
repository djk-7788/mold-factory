#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
import random
from pathlib import Path
from datetime import datetime
import re

OVERWRITE_IF_EXISTS = False
DEFAULT_DATE_FMT = "%Y-%m-%dT%H:%M:%S+09:00"

SUPPORTED_LANGS = {"ko", "en", "es", "pt"}


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure_directories(root: Path):
    # 기본 posts 폴더 (구버전 호환용)
    (root / "content" / "posts").mkdir(parents=True, exist_ok=True)

    # 언어별 posts 폴더
    for lang in SUPPORTED_LANGS:
        (root / "content" / lang / "posts").mkdir(parents=True, exist_ok=True)

    # 로그 폴더
    (root / "automation" / "logs").mkdir(parents=True, exist_ok=True)


def slugify(keyword: str) -> str:
    s = keyword.strip().lower()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^0-9a-z가-힣\-]", "", s)
    s = re.sub(r"-{2,}", "-", s)
    return s or "post"


# -----------------------------
#  E2: products.csv 불러오기
# -----------------------------
def load_products(csv_path: Path) -> dict:
    products = {}
    if not csv_path.exists():
        print("[INFO] products.csv 없음 → 기본 product_block 사용")
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


# -----------------------------
# 실행 시작
# -----------------------------
def main():
    root = get_project_root()
    ensure_directories(root)

    template_path = root / "automation" / "templates" / "base.md"

    # E4: keywords_typed.csv 우선 사용
    typed_csv_path = root / "automation" / "keywords_typed.csv"
    raw_csv_path = root / "automation" / "keywords.csv"

    if typed_csv_path.exists():
        csv_path = typed_csv_path
        print(f"[INFO] 분류된 키워드 사용 : {csv_path}")
    else:
        csv_path = raw_csv_path
        print(f"[INFO] 키워드 파일 로드 : {csv_path}")

    products_csv_path = root / "automation" / "data" / "products.csv"
    log_path = root / "automation" / "logs" / "generate_log.csv"

    products = load_products(products_csv_path)
    print(f"[INFO] 상품 매핑 {len(products)}개 로딩 완료")

    if not template_path.exists():
        print("[ERROR] base.md 템플릿이 없습니다.")
        return
    if not csv_path.exists():
        print("[ERROR] 키워드 CSV 파일이 없습니다.")
        return

    base_template = template_path.read_text(encoding="utf-8")
    now_str = datetime.now().strftime(DEFAULT_DATE_FMT)

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"[INFO] 키워드 {len(rows)}개 로딩 완료")

    for row in rows:
        keyword = (row.get("keyword") or "").strip()
        summary = (row.get("summary") or "").strip()

        if not keyword:
            continue

        # -----------------
        # E5: 언어 컬럼 처리
        # -----------------
        lang = (row.get("lang") or "ko").strip().lower()
        if lang not in SUPPORTED_LANGS:
            lang = "ko"

        slug = slugify(keyword)

        # --- 본문 자동 생성 블록 ---
        introduction = f"{keyword} 문제를 쉽게 해결하는 가이드입니다."

        cause_block = (
            f"- {keyword}는 주로 습기, 잘못된 관리, 오염 누적 등으로 발생합니다.\n"
            f"- 원인을 파악하고 관리하면 같은 문제의 재발 확률을 크게 줄일 수 있습니다."
        )

        solution_block = (
            f"1. 먼저 {keyword} 상태를 눈으로 확인합니다.\n"
            f"2. 집에 있는 세제·솔·수건 등으로 1차 청소를 합니다.\n"
            f"3. 심한 경우 전용 세정제나 제거제를 함께 사용하는 것이 좋습니다."
        )

        tip_block = (
            f"- 한 번에 끝내려 하지 말고 며칠에 걸쳐 꾸준히 관리하는 것이 더 오래 갑니다.\n"
            f"- 사용 후에는 최대한 빨리 건조 및 환기시키면 재발을 줄일 수 있습니다."
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
            product_block = (
                f"- {keyword} 상황에 맞는 전용 세정제나 제거제를 함께 사용하면 효과가 높아집니다.\n"
                f"- 향후 AliExpress / Temu 상품 자동 연동 예정입니다."
            )

        # --- FAQ 자동 생성 (E3-1 업그레이드) ---
        faq_templates = [
            ("얼마나 걸리나요?", f"{keyword} 문제는 보통 2~7일 정도 꾸준히 관리하면 눈에 띄게 개선됩니다."),
            ("다시 생기지 않게 하려면?", f"{keyword} 예방의 핵심은 건조와 환기이며, 사용 후 물기 제거가 가장 중요합니다."),
            ("집에 있는 세제로도 되나요?", "초기 단계라면 기본 세제로도 가능하지만, 심한 경우 전용 제품을 함께 쓰는 것이 좋습니다."),
            ("전문 업체를 불러야 하나요?", f"대부분의 {keyword} 문제는 셀프로 충분히 관리 가능하지만, 심각한 경우 전문가 방문이 빠릅니다."),
            ("얼마나 자주 관리해야 하나요?", f"일반적으로 한 달에 1~2번 관리하면 {keyword}가 재발할 확률을 크게 줄일 수 있습니다."),
            ("냄새가 심할 때는?", f"{keyword}가 심하면 일단 건조·환기 후 전용 탈취제를 쓰면 효과가 좋습니다."),
            ("어떤 제품을 쓰면 좋나요?", f"{keyword} 전용 세정제나 제거제를 함께 사용하면 관리 시간이 줄어듭니다."),
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
        content = content.replace("{{summary}}", summary or f"{keyword} 문제 해결 방법")
        content = content.replace("{{introduction}}", introduction)
        content = content.replace("[[cause_block]]", cause_block)
        content = content.replace("[[solution_block]]", solution_block)
        content = content.replace("[[product_block]]", product_block)
        content = content.replace("[[tip_block]]", tip_block)
        content = content.replace("[[faq_block]]", faq_block)
        content = content.replace("{{lang}}", lang)

        # --- 파일 생성 (E5: 언어별 폴더) ---
        post_dir = root / "content" / lang / "posts" / slug
        post_dir.mkdir(parents=True, exist_ok=True)
        post_path = post_dir / "index.md"

        if post_path.exists() and not OVERWRITE_IF_EXISTS:
            print(f"[SKIP] 이미 존재: {keyword} ({lang})")
            continue

        post_path.write_text(content, encoding="utf-8")
        print(f"[OK] 생성됨 → {post_path}")

        # 로그 기록 (언어 포함)
        with log_path.open("a", encoding="utf-8") as logf:
            logf.write(f"{now_str},{lang},{keyword},{slug}\n")


if __name__ == "__main__":
    main()
