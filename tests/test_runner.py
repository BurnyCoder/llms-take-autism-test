from llms_take_autism_test.runner import parse_completion_table
from llms_take_autism_test.types import QuestionnaireItem


def test_parse_completion_table_accepts_valid_tsv() -> None:
    items = [
        QuestionnaireItem("aq10", 1, "Question 1", "agree"),
        QuestionnaireItem("aq10", 2, "Question 2", "disagree"),
    ]
    raw = "1\tDefinitely Agree\n2\tSlightly Disagree\nNOTE\tShort note\n"

    parsed = parse_completion_table(raw, items)

    assert [row["item_id"] for row in parsed] == [1, 2]
    assert parsed[0]["score"] == 1
    assert parsed[1]["score"] == 1
    assert parsed[0]["note"] == "Short note"


def test_parse_completion_table_rejects_missing_rows() -> None:
    items = [
        QuestionnaireItem("aq10", 1, "Question 1", "agree"),
        QuestionnaireItem("aq10", 2, "Question 2", "disagree"),
    ]
    raw = "1\tDefinitely Agree\nNOTE\tShort note\n"

    try:
        parse_completion_table(raw, items)
    except ValueError as exc:
        assert "expected set" in str(exc)
    else:
        raise AssertionError("Expected parser to reject missing item rows")
