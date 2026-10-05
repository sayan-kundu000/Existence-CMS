import pytest
from app.data.question_banks import ASSESSMENT_REGISTRY, QUESTION_BANKS


def test_question_banks_exact_counts():
    """Verify Section: Exactly 75 questions per assessment = 225 items total."""
    assert len(QUESTION_BANKS["MBTI"]) == 75, f"Expected 75 MBTI questions, got {len(QUESTION_BANKS['MBTI'])}"
    assert len(QUESTION_BANKS["DISC"]) == 75, f"Expected 75 DISC questions, got {len(QUESTION_BANKS['DISC'])}"
    assert len(QUESTION_BANKS["BIG_FIVE"]) == 75, f"Expected 75 BIG_FIVE questions, got {len(QUESTION_BANKS['BIG_FIVE'])}"

    assert ASSESSMENT_REGISTRY["MBTI"]["question_count"] == 75
    assert ASSESSMENT_REGISTRY["DISC"]["question_count"] == 75
    assert ASSESSMENT_REGISTRY["BIG_FIVE"]["question_count"] == 75


def test_question_banks_uniqueness_and_no_repetition():
    """Verify: zero duplicate IDs, zero duplicate texts in wording and meaning across all banks."""
    seen_ids = set()
    seen_texts = set()

    for test_key, questions in QUESTION_BANKS.items():
        assert len(questions) == 75
        for q in questions:
            # Check ID uniqueness
            assert q["id"] not in seen_ids, f"Duplicate question ID found: {q['id']}"
            seen_ids.add(q["id"])

            # Check text uniqueness
            clean_text = q["text"].lower().strip().rstrip(".!?")
            assert clean_text not in seen_texts, f"Duplicate or repeated question text found in {test_key}: {q['text']}"
            seen_texts.add(clean_text)

            # Ensure valid Likert scale
            assert q.get("scale_type") == "likert_5"
            assert len(q["text"]) > 20, f"Question too short or empty: {q['text']}"

    assert len(seen_ids) == 225
    assert len(seen_texts) == 225


def test_question_banks_dimension_coverage():
    """Verify all dimensions in each framework are properly covered."""
    # MBTI dimensions
    mbti_dims = [q["dimension"] for q in QUESTION_BANKS["MBTI"]]
    assert mbti_dims.count("EI") == 19
    assert mbti_dims.count("SN") == 19
    assert mbti_dims.count("TF") == 19
    assert mbti_dims.count("JP") == 18
    assert sum([mbti_dims.count(d) for d in ["EI", "SN", "TF", "JP"]]) == 75

    # DISC dimensions
    disc_dims = [q["dimension"] for q in QUESTION_BANKS["DISC"]]
    assert disc_dims.count("D") == 19
    assert disc_dims.count("I") == 19
    assert disc_dims.count("S") == 19
    assert disc_dims.count("C") == 18
    assert sum([disc_dims.count(d) for d in ["D", "I", "S", "C"]]) == 75

    # Big Five dimensions
    b5_dims = [q["dimension"] for q in QUESTION_BANKS["BIG_FIVE"]]
    assert b5_dims.count("O") == 15
    assert b5_dims.count("C") == 15
    assert b5_dims.count("E") == 15
    assert b5_dims.count("A") == 15
    assert b5_dims.count("N") == 15
    assert sum([b5_dims.count(d) for d in ["O", "C", "E", "A", "N"]]) == 75
