"""`M7-003b`/`AE-28`: the token-bucket rate limiter."""

import pytest

from p2p_thief_agent.services.token_bucket import TokenBucket, TokenBucketError


def test_a_fresh_bucket_permits_a_full_burst_then_refuses() -> None:
    bucket = TokenBucket(capacity=3, refill_per_second=0.05)  # 3 per minute
    assert [bucket.allow(now=10.0) for _ in range(3)] == [True, True, True]
    assert bucket.allow(now=10.0) is False  # burst spent, no time has passed


def test_it_refills_at_the_configured_rate() -> None:
    bucket = TokenBucket(capacity=3, refill_per_second=0.05)
    for _ in range(3):
        bucket.allow(now=10.0)
    assert bucket.allow(now=30.0) is True  # 20 s * 0.05 = 1 token back
    assert bucket.allow(now=30.0) is False


def test_refill_is_capped_at_capacity() -> None:
    bucket = TokenBucket(capacity=3, refill_per_second=0.05)
    bucket.allow(now=0.0)  # spend one, then wait a long time
    assert bucket.available(now=100_000.0) == 3.0  # never exceeds the burst capacity


def test_backwards_time_neither_drains_nor_refills() -> None:
    bucket = TokenBucket(capacity=3, refill_per_second=0.05)
    bucket.allow(now=100.0)  # tokens -> 2, last -> 100
    assert bucket.available(now=50.0) == 2.0  # a clock that jumps back adds nothing


@pytest.mark.parametrize("bad", [(0, 1), (-1, 1), (1, 0), (1, -1)])
def test_a_non_positive_configuration_is_rejected(bad: tuple) -> None:
    with pytest.raises(TokenBucketError):
        TokenBucket(capacity=bad[0], refill_per_second=bad[1])
