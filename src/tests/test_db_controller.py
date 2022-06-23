import pytest

pytestmark = [pytest.mark.asyncio]


async def test_one_plus_one():
    assert 2 == 2