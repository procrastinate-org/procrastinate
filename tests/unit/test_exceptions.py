from __future__ import annotations

import pytest

from procrastinate import exceptions


@pytest.mark.parametrize(
    "detail, queueing_lock",
    [
        ("Key (queueing_lock)=(foo) already exists.", "foo"),
        ("Schlüssel »(queueing_lock)=(foo)« existiert bereits.", "foo"),
        ('Ключ "(queueing_lock)=(foo)" уже существует.', "foo"),
        ("キー (queueing_lock)=(foo) はすでに存在します。", "foo"),
        ("Key (queueing_lock)=(L)ock=(x) already exists.", "L)ock=(x"),
        ("Key (lock)=(foo) already exists.", None),
        ("unexpected", None),
        (None, None),
    ],
)
def test_unique_violation_from_detail(detail, queueing_lock):
    exc = exceptions.UniqueViolation.from_detail(detail, constraint_name="constraint")

    assert exc.constraint_name == "constraint"
    assert exc.queueing_lock == queueing_lock
