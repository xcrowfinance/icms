from datetime import datetime

import pytest
from django.utils import timezone

from data_migration.management.commands.utils.db import bulk_create, new_process_pk
from data_migration.management.commands.utils.format import format_name, format_row
from data_migration.models import Process


@pytest.mark.parametrize(
    "name,expected", [("a_name", "A Name"), ("a name", "A name"), ("A Name", "A name")]
)
def test_format_name(name, expected):
    assert format_name(name) == expected


@pytest.mark.parametrize(
    "columns,row,includes,pk,expected",
    [
        (("a", "b", "c"), (1, 2, 3), None, None, {"a": 1, "b": 2, "c": 3}),
        (("a", "b", "c"), (1, 2, 3), ["b", "c"], None, {"b": 2, "c": 3}),
        (("a", "b", "c"), (1, 2, 3), None, 123, {"a": 1, "b": 2, "c": 3, "id": 123}),
    ],
)
def test_format_row(columns, row, includes, pk, expected):
    assert format_row(columns, row, includes, pk) == expected


def test_format_row_datetime():
    dt = datetime.now()
    tz = timezone.utc.localize(dt)
    columns = ("a_datetime",)
    row = (dt,)

    assert format_row(columns, row) == {"a_datetime": tz}


@pytest.mark.django_db
def test_new_process_pk():
    assert new_process_pk() == 1
    obj = Process.objects.create(process_type="ABC")
    assert new_process_pk() == obj.pk + 1


@pytest.mark.django_db
def test_bulk_create():
    Process.objects.create(process_type="New")
    pk = new_process_pk()
    bulk_create(
        Process, [Process(process_type="ATest", id=pk), Process(process_type="BTest", id=pk + 1)]
    )
    assert Process.objects.filter(id=pk, process_type="ATest").count() == 1
    assert Process.objects.filter(id=pk + 1, process_type="BTest").count() == 1
    obj = Process.objects.create(process_type="CTest")
    assert obj.pk == pk + 2