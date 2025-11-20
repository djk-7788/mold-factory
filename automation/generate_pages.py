#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
from pathlib import Path
from datetime import datetime
import re

OVERWRITE_IF_EXISTS = False
DEFAULT_DATE_FMT = "%Y-%m-%dT%H:%M:%S+09:00"

def get_project_root() -> Path:
    return Path(__file__).resolve().parents[1]

def ensure_directories(root: Path):
    (root / "content" / "posts").mkdir(parents=True, exist_ok=True)
    (root / "automation" / "logs").mkdir(parents=True, exist_ok=True)

def slugify(keyword: str) -> str:
    s = keyword.strip().lower()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^0-9a-z가-힣\-]", "", s)
    s = re.sub(r"-{2,}", "-", s)
    return s or "post"

def main():
    root = get_project_root()
    ensure_directories(root)

    template_path = root / "automation" / "templates" / "base.md"
    csv_path = root / "automation" / "data" / "keywords.csv"
    log_path = root / "automation" / "logs" / "generate_log.csv"

    if not template_path.exists():
        print("[ERROR] base.md 템플릿이 없습니다.")
        return
    if not csv_path.exists():
        print("[ERROR] keywords.csv 파일이 없습니다.")
        return

    base_template = template_path.read_text(encoding="utf-8")
    now_str = datetime.now().strftime(DEFAULT_DATE_FMT)

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            keyword = row.get("keyword", "").strip()
            summary = row.get("summary", "").strip()
            if not keyword:
                continue

            slug = slugify(keyword)

            # --- 여기서 각 블록 문장들을 직접 만든다 ---
            introduction = f"{keyword} 문제를 쉽게 해결하는 가이드입니다."
            cause_block = (
                f"- {keyword}는 보통 습기, 환기 부족, 잘못된 사용 습관이 겹치면서 생깁니다.\n"
                f"- 원인을 정확히 알고 관리하면 같은 문제가 다시 생길 확률을 크게 줄일 수 있습니다."
            )
            solution_block = (
                f"1. 먼저 현재 {keyword} 상태를 눈으로 확인합니다.\n"
                f"2. 집에 있는 세제·솔·수건 등을 이용해 가볍게 1차 청소를 합니다.\n"
                f"3. 심한 경우 전용 세정제나 곰팡이 제거제를 함께 사용하는 것이 좋습니다."
            )
            product_block = (
                f"- {keyword} 상황에 맞는 전용 세정제, 곰팡이 제거제, 탈취제를 함께 사용하면\n"
                f"  작업 시간과 힘을 줄이면서 효과를 더 높일 수 있습니다."
            )
            tip_block = (
                f"- 한 번에 끝내려 하기보다, 며칠에 걸쳐 꾸준히 관리하는 편이 더 오래 갑니다.\n"
                f"- 사용 후에는 최대한 빨리 건조·환기시키는 습관을 들이면 재발을 줄일 수 있습니다."
            )
            faq_block = (
                f"**Q. {keyword}를 완전히 없애는 데 얼마나 걸리나요?**\n"
                f"A. 상태에 따라 다르지만, 보통 1~2주 정도 꾸준히 관리하면 눈에 띄게 좋아지는 경우가 많습니다.\n\n"
                f"**Q. 집에 있는 기본 세제만 써도 되나요?**\n"
                f"A. 초기 단계라면 가능하지만, 냄새가 심하거나 얼룩이 깊으면 전용 제품을 함께 쓰는 게 좋습니다."
            )

            content = base_template
            content = content.replace("{{keyword}}", keyword)
            content = content.replace("{{date}}", now_str)
            content = content.replace("{{slug}}", slug)
            content = content.replace("{{summary}}", summary or f"{keyword} 문제를 해결하는 방법을 정리했습니다.")
            content = content.replace("{{introduction}}", introduction)
            content = content.replace("[[cause_block]]", cause_block)
            content = content.replace("[[solution_block]]", solution_block)
            content = content.replace("[[product_block]]", product_block)
            content = content.replace("[[tip_block]]", tip_block)
            content = content.replace("[[faq_block]]", faq_block)

            post_dir = root / "content" / "posts" / slug
            post_dir.mkdir(parents=True, exist_ok=True)
            post_path = post_dir / "index.md"

            if post_path.exists() and not OVERWRITE_IF_EXISTS:
                print(f"[SKIP] 이미 존재: {keyword}")
                continue

            post_path.write_text(content, encoding="utf-8")
            print(f"[OK] 생성됨 → {post_path}")

            with open(log_path, "a", encoding="utf-8") as logf:
                logf.write(f"{now_str},{keyword},{slug}\n")


if __name__ == "__main__":
    main()
