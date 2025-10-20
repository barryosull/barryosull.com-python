
from backend.domain.value_objects.vote import Vote, VoteChoice


def test_vote_ja_creation():
    vote = Vote.ja()
    assert vote.choice == VoteChoice.JA
    assert vote.is_ja()
    assert not vote.is_nein()


def test_vote_nein_creation():
    vote = Vote.nein()
    assert vote.choice == VoteChoice.NEIN
    assert vote.is_nein()
    assert not vote.is_ja()


def test_vote_equality():
    ja1 = Vote.ja()
    ja2 = Vote.ja()
    nein = Vote.nein()

    assert ja1 == ja2
    assert ja1 != nein


def test_vote_hash():
    ja1 = Vote.ja()
    ja2 = Vote.ja()
    nein = Vote.nein()

    vote_set = {ja1, ja2, nein}
    assert len(vote_set) == 2  # Only 2 unique votes


def test_vote_repr():
    ja = Vote.ja()
    nein = Vote.nein()

    assert repr(ja) == "Vote(JA)"
    assert repr(nein) == "Vote(NEIN)"
