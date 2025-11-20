#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
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

            content = base_template
            content = content.replace("{{keyword}}", keyword)
            content = content.replace("{{date}}", now_str)
            content = content.replace("{{slug}}", slug)
            content = content.replace("{{summary}}", summary)

            blocks = {
                "introduction": f"{keyword} 문제를 쉽게 해결하는 가이드입니다.",
                "cause_block": f"- {keyword}는 다양한 환경적 요인이 원인입니다.",
                "solution_block": f"1. 먼저 {keyword}의 상태를 확인하세요.",
                "product_block": f"- {keyword} 관련 제품을 곧 자동 추천합니다.",
                "tip_block": f"- {keyword}는 습기 관리가 핵심입니다.",
                "faq_block": f"**Q. {keyword}는 얼마나 걸리나요?**\nA. 보통 며칠이면 개선됩니다."
            }

            for k, v in blocks.items():
                content = content.replace(f"{{{{{k}}}}}", v)

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
