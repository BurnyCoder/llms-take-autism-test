from llms_take_autism_test.sources import parse_adult_aq_text, parse_aq10_text

AQ10_SAMPLE = """
AQ-10
Please tick one option per question only:
  1
       I often notice small sounds when others do
       not
  2
       I usually concentrate more on the whole
       picture, rather than the small details
  3
       I find it easy to do more than one thing at
       once
  4
       If there is an interruption, I can switch back to
       what I was doing very quickly
  5
       I find it easy to 'read between the lines' when
       someone is talking to me
  6
       I know how to tell if someone listening to me
       is getting bored
  7
       When I'm reading a story I find it difficult to
       work out the characters' intentions
  8
       I like to collect information about categories of
       things
  9
       I find it easy to work out what someone is
       thinking or feeling just by looking at their face
 10    I find it difficult to work out people's intentions
SCORING: Only 1 point can be scored for each question. Score 1 point for Definitely or
Slightly Agree on each of items 1, 7, 8, and 10. Score 1 point for Definitely or Slightly
Disagree on each of items 2, 3, 4, 5, 6, and 9.
"""

ADULT_AQ_SAMPLE = """
The Adult Autism Spectrum Quotient (AQ)
Responses that score 1 point are marked. Other responses score 0. For total score, sum all items.
I prefer to do things with others rather than on my own.
I prefer to do things the same way over and over again.
If I try to imagine something, I find it very easy to create a picture in my mind.
I frequently get so strongly absorbed in one thing that I lose sight of other things.
I often notice small sounds when others do not.
I usually notice car number plates or similar strings of information.
"""


def test_parse_aq10_text_extracts_items_and_scoring() -> None:
    items = parse_aq10_text(AQ10_SAMPLE, expected_count=10)

    assert len(items) == 10
    assert items[0].text == "I often notice small sounds when others do not"
    assert items[0].keyed_response == "agree"
    assert items[1].keyed_response == "disagree"
    assert items[-1].item_id == 10
    assert items[-1].keyed_response == "agree"


def test_parse_adult_aq_text_extracts_ordered_items() -> None:
    items = parse_adult_aq_text(ADULT_AQ_SAMPLE)

    assert len(items) == 6
    assert items[0].item_id == 1
    assert items[0].keyed_response == "disagree"
    assert items[1].keyed_response == "agree"
    assert items[2].keyed_response == "disagree"
    assert items[5].text == "I usually notice car number plates or similar strings of information."
