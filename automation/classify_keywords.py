import csv
from pathlib import Path

# 1) 프로젝트 루트 & 파일 경로
ROOT = Path(__file__).resolve().parents[1]
KEYWORDS_CSV = ROOT / "automation" / "keywords.csv"
OUTPUT_CSV = ROOT / "automation" / "keywords_typed.csv"


# 2) 키워드에서 유형 판별하는 함수
def classify_keyword(keyword: str) -> str:
    """
    키워드 문자열을 보고 유형을 판별한다.
    mold / odor / stain / clean / other 중 하나를 반환.
    """
    kw = keyword.strip()

    # 우선순위 중요! (위에서부터 차례대로 체크)
    if "곰팡이" in kw:
        return "mold"

    if ("냄새" in kw) or ("악취" in kw) or ("취" in kw and "악취" not in kw):
        return "odor"

    # 기름때, 물때, 찌든때, 얼룩, 녹 등 '때 제거' 계열
    stain_words = ["기름때", "물때", "찌든때", "찌든 때", "얼룩", "녹 제거", "녹제거"]
    if any(word in kw for word in stain_words) or "때 제거" in kw:
        return "stain"

    # 청소/세척/관리/보관/정리
    clean_words = ["청소", "세척", "관리", "보관", "정리", "청소법", "청소 방법"]
    if any(word in kw for word in clean_words):
        return "clean"

    # 그 밖에는 일단 other
    return "other"


def main():
    if not KEYWORDS_CSV.exists():
        raise FileNotFoundError(f"키워드 파일을 찾을 수 없습니다: {KEYWORDS_CSV}")

    print(f"[INFO] 키워드 파일 로드: {KEYWORDS_CSV}")

    with KEYWORDS_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []

        # 기존 컬럼 + type 컬럼 추가
        if "type" not in fieldnames:
            fieldnames = fieldnames + ["type"]

        rows = list(reader)

    # 분류 작업
    stats = {"mold": 0, "odor": 0, "stain": 0, "clean": 0, "other": 0}

    for row in rows:
        keyword = row.get("keyword", "").strip()
        if not keyword:
            row["type"] = "other"
            stats["other"] += 1
            continue

        t = classify_keyword(keyword)
        row["type"] = t
        stats[t] += 1

    # 결과 저장
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] 분류 완료 → {OUTPUT_CSV}")
    print("\n[통계]")
    for k, v in stats.items():
        print(f" - {k}: {v}개")


if __name__ == "__main__":
    main()
