from __future__ import annotations

from procrastinate import jobs
from procrastinate.contrib.django import admin


def test_emoji_mapping():
    assert set(admin.JOB_STATUS_EMOJI_MAPPING) == {e.value for e in jobs.Status}
