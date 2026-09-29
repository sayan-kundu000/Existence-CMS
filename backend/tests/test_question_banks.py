import pytest
from app.data.question_banks import ASSESSMENT_REGISTRY, QUESTION_BANKS


def test_question_banks_exact_counts():
    """Verify Section: Exactly 43 questions per assessment = 129 items total."""
    assert len(QUESTION_BANKS["MBTI"]) == 43, f"Expected 43 MBTI questions, got {len(QUESTION_BANKS['MBTI'])}"
    assert len(QUESTION_BANKS["DISC"]) == 43, f"Expected 43 DISC questions, got {len(QUESTION_BANKS['DISC'])}"
    assert len(QUESTION_BANKS["BIG_FIVE"]) == 43, f"Expected 43 BIG_FIVE questions, got {len(QUESTION_BANKS['BIG_FIVE'])}"

    assert ASSESSMENT_REGISTRY["MBTI"]["question_count"] == 43
    assert ASSESSMENT_REGISTRY["DISC"]["question_count"] == 43
    assert ASSESSMENT_REGISTRY["BIG_FIVE"]["question_count"] == 43


def test_question_banks_uniqueness_and_no_repetition():
    """Verify: zero duplicate IDs, zero duplicate texts in wording and meaning across all banks."""
    seen_ids = set()
    seen_texts = set()

    for test_key, questions in QUESTION_BANKS.items():
        assert len(questions) == 43
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

    assert len(seen_ids) == 129
    assert len(seen_texts) == 129


def test_question_banks_dimension_coverage():
    """Verify all dimensions in each framework are properly covered."""
    # MBTI dimensions
    mbti_dims = [q["dimension"] for q in QUESTION_BANKS["MBTI"]]
    assert mbti_dims.count("EI") == 11
    assert mbti_dims.count("SN") == 11
    assert mbti_dims.count("TF") == 11
    assert mbti_dims.count("JP") == 10
    assert sum([mbti_dims.count(d) for d in ["EI", "SN", "TF", "JP"]]) == 43

    # DISC dimensions
    disc_dims = [q["dimension"] for q in QUESTION_BANKS["DISC"]]
    assert disc_dims.count("D") == 11
    assert disc_dims.count("I") == 11
    assert disc_dims.count("S") == 11
    assert disc_dims.count("C") == 10
    assert sum([disc_dims.count(d) for d in ["D", "I", "S", "C"]]) == 43

    # Big Five dimensions
    b5_dims = [q["dimension"] for q in QUESTION_BANKS["BIG_FIVE"]]
    assert b5_dims.count("O") == 9
    assert b5_dims.count("C") == 9
    assert b5_dims.count("E") == 9
    assert b5_dims.count("A") == 8
    assert b5_dims.count("N") == 8
    assert sum([b5_dims.count(d) for d in ["O", "C", "E", "A", "N"]]) == 43
