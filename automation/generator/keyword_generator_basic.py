import csv
from pathlib import Path

# === 경로 설정 ===

GENERATOR_DIR = Path(__file__).resolve().parent          # ...\automation\generator
AUTOMATION_DIR = GENERATOR_DIR.parent                    # ...\automation
KEYWORDS_DIR = AUTOMATION_DIR / "keywords"               # ...\automation\keywords

SEED_FILE = KEYWORDS_DIR / "seed_rules.txt"
OUTPUT_FILE = KEYWORDS_DIR / "generated_keywords.csv"


def load_seed_rules():
    """seed_rules.txt 에서 한 줄씩 읽어서 리스트로 반환."""
    if not SEED_FILE.exists():
        raise FileNotFoundError(f"시드 규칙 파일을 찾을 수 없습니다: {SEED_FILE}")

    rules = []
    for line in SEED_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rules.append(line)
    return rules


def generate_from_korean_rule(rule: str):
    """한글 규칙(욕실, 주방 등)에서 키워드 여러 개 생성."""
    place = None
    topic = None

    # 장소 추출
    if "욕실" in rule:
        place = "욕실"
    elif "주방" in rule:
        place = "주방"
    elif "베란다" in rule:
        place = "베란다"
    elif "옷" in rule:
        place = "옷"

    # 주제 추출
    if "곰팡이" in rule:
        topic = "곰팡이"
    elif "악취" in rule:
        topic = "악취"
    elif "습기" in rule:
        topic = "습기"
    elif "냄새" in rule:
        topic = "냄새"

    if not place or not topic:
        # 규칙을 못 알아들으면 그냥 한 줄짜리 키워드만 반환
        return [rule]

    keywords = [
        f"{place} {topic} 제거 방법",
        f"{place} {topic} 없애는 법",
        f"{place} {topic} 원인",
        f"{place} {topic} 냄새 없애는 법",
        f"{place} {topic} 관리 방법",
        f"{place} {topic} 생기는 이유",
        f"{place} {topic} 예방 방법",
        f"{place} {topic} 세정제 추천",
    ]

    # 장소+부위 조합 몇 개 추가
    if place == "욕실":
        keywords += [
            f"{place} 실리콘 {topic} 제거",
            f"{place} 천장 {topic} 없애는 법",
            f"{place} 타일 줄눈 {topic} 지우기",
        ]
    elif place == "주방":
        keywords += [
            f"{place} 싱크대 {topic} 없애는 법",
            f"{place} 배수구 {topic} 제거 방법",
        ]
    elif place == "베란다":
        keywords += [
            f"{place} 창틀 {topic} 제거",
            f"{place} 곰팡이 {topic} 잡는 방법",
        ]
    elif place == "옷":
        keywords += [
            f"{place} {topic} 빼는 방법",
            f"{place} {topic} 빠르게 없애는 법",
        ]

    return keywords


def generate_from_english_rule(rule: str):
    """영어 규칙에서 기본적인 키워드 여러 개 생성."""
    rule_lower = rule.lower()

    # 아주 단순한 패턴만 사용 (나중에 GPT 버전으로 갈아끼울 예정)
    if "how to remove" in rule_lower and "+" in rule:
        parts = [p.strip() for p in rule.split("+")]
        base = parts[-1]
        keywords = [
            f"how to remove {base}",
            f"best way to remove {base}",
            f"how to quickly remove {base}",
            f"{base} removal tips",
        ]
        return keywords

    if "why does my" in rule_lower and "+" in rule:
        parts = [p.strip() for p in rule.split("+")]
        base = " ".join(parts[1:])  # room + smell 정도
        keywords = [
            f"why does my {base}",
            f"why does my {base} so bad",
            f"{base} causes and fixes",
        ]
        return keywords

    if "how to clean" in rule_lower and "+" in rule:
        parts = [p.strip() for p in rule.split("+")]
        base = parts[-1]
        keywords = [
            f"how to clean {base}",
            f"best way to clean {base}",
            f"{base} cleaning tips",
        ]
        return keywords

    # 그 외엔 일단 원문 그대로
    return [rule]


def generate_keywords_from_rule(rule: str):
    """한 줄 규칙에서 여러 키워드 리스트로 변환."""
    # 한글/영어 대충 구분 (영문자가 있으면 영어 규칙으로 봄)
    if any("a" <= ch.lower() <= "z" for ch in rule if ch.isalpha()):
        return generate_from_english_rule(rule)
    else:
        return generate_from_korean_rule(rule)


def main():
    print("=== 키워드 기본 생성기 V0.1 시작 ===")
    print(f"시드 규칙 파일: {SEED_FILE}")
    print(f"출력 CSV 파일:  {OUTPUT_FILE}\n")

    rules = load_seed_rules()
    print(f"불러온 규칙 개수: {len(rules)}")
    all_keywords = []
    seen = set()

    for rule in rules:
        kws = generate_keywords_from_rule(rule)
        print(f"\n[규칙] {rule}")
        print(f" → 생성된 키워드 {len(kws)}개")

        for kw in kws:
            kw = kw.strip()
            if not kw:
                continue
            if kw in seen:
                continue
            seen.add(kw)
            all_keywords.append((kw, rule))

    # CSV로 저장
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["keyword", "source_rule"])
        writer.writerows(all_keywords)

    print("\n=== 생성 완료 ===")
    print(f"총 키워드 개수: {len(all_keywords)}")
    print(f"저장 위치: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
