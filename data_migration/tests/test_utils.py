from datetime import datetime

import pytest
from django.forms import ValidationError
from django.utils import timezone
from lxml import etree

from data_migration.management.commands.utils.db import bulk_create, new_process_pk
from data_migration.management.commands.utils.format import format_name, format_row
from data_migration.models import Process
from data_migration.utils.format import (
    date_or_none,
    datetime_or_none,
    float_or_none,
    get_xml_val,
    int_or_none,
    str_to_bool,
    str_to_yes_no,
    validate_decimal,
    validate_int,
    xml_str_or_none,
)


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


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, None),
        ("", None),
        (datetime(2014, 10, 1).date(), datetime(2014, 10, 1).date()),
        (datetime(2014, 10, 1), datetime(2014, 10, 1).date()),
        ("2014-10-01", datetime(2014, 10, 1).date()),
        ("01-10-2014", datetime(2014, 10, 1).date()),
        ("01-10-14", datetime(2014, 10, 1).date()),
        ("01/10/2014", datetime(2014, 10, 1).date()),
        ("01/10/14", datetime(2014, 10, 1).date()),
        ("01 October 2014", datetime(2014, 10, 1).date()),
        ("01.10.2014", datetime(2014, 10, 1).date()),
        ("01.10.14", datetime(2014, 10, 1).date()),
    ],
)
def test_date_or_none(test_input, expected):
    assert date_or_none(test_input) == expected


def test_date_or_none_exception():
    with pytest.raises(ValidationError) as excinfo:
        date_or_none("2014-10-01T00:00:00")
    assert "Date 2014-10-01T00:00:00 not in parsable format" in str(excinfo.value)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, None),
        ("", None),
        ("2014-10-01T01:02:03", datetime(2014, 10, 1, 1, 2, 3)),
    ],
)
def test_datetime_or_none(test_input, expected):
    assert datetime_or_none(test_input) == expected


@pytest.mark.parametrize(
    "test,expected",
    [
        (None, None),
        ("", None),
        ("nan", None),
        ("1", 1),
        ("1.0", 1.0),
        ("1.1", 1.1),
        ("1.11", 1.11),
    ],
)
def test_float_or_none(test, expected):
    assert float_or_none(test) == expected


@pytest.mark.parametrize(
    "int_str,expected",
    [
        (None, None),
        ("", None),
        ("1", 1),
    ],
)
def test_int_or_none(int_str, expected):
    assert int_or_none(int_str) == expected


@pytest.mark.parametrize(
    "xml_str,xpath,expected",
    [
        ("<ROOT><A>a</A><B>b</B></ROOT>", "/ROOT/A/text()", "a"),
        ("<ROOT><A>a</A><B>b</B></ROOT>", "//A", "a"),
        ("<ROOT><A>a</A><B>b</B></ROOT>", "./A/text()", "a"),
        ("<ROOT><A>a</A><B> b\n</B></ROOT>", "/ROOT/B", "b"),
        ("<ROOT><A>a</A><B> b </B></ROOT>", "ROOT/C/text()", None),
    ],
)
def test_get_xml_val(xml_str, xpath, expected):
    xml = etree.fromstring(xml_str)
    assert expected == get_xml_val(xml, xpath)


@pytest.mark.parametrize(
    "xml_str",
    [
        ("<ROOT><A>a</A><B>b</B></ROOT>"),
        ("\n<ROOT><A>a</A><B>b</B></ROOT> "),
        (None),
    ],
)
def test_xml_str_or_none(xml_str):
    if xml_str:
        xml = etree.fromstring(xml_str)
        assert xml_str.strip() == xml_str_or_none(xml)
    else:
        assert xml_str_or_none(xml_str) is None


@pytest.mark.parametrize(
    "bool_str,expected",
    [
        ("Y", True),
        ("N", False),
        ("y", True),
        ("n", False),
        ("TRUE", True),
        ("true", True),
        ("FALSE", False),
        ("false", False),
        ("", None),
        (None, None),
    ],
)
def test_str_to_bool(bool_str, expected):
    assert str_to_bool(bool_str) is expected


@pytest.mark.parametrize(
    "y_n_str,expected",
    [
        ("Y", "yes"),
        ("N", "no"),
        ("y", "yes"),
        ("n", "no"),
        ("TRUE", "yes"),
        ("true", "yes"),
        ("FALSE", "no"),
        ("false", "no"),
        ("N/A", "n/a"),
        ("NA", "n/a"),
        ("n/a", "n/a"),
        ("na", "n/a"),
        ("", None),
        (None, None),
    ],
)
def test_str_to_yes_no(y_n_str, expected):
    assert str_to_yes_no(y_n_str) == expected


@pytest.mark.parametrize(
    "fields,data,expected",
    [
        (["a"], {"a": "1.2", "b": "1.2a"}, {"a": "1.2", "b": "1.2a"}),
        (["b"], {"a": "1.2", "b": "1.2a"}, {"a": "1.2"}),
        (["a", "b"], {"a": "1", "b": "1.2a"}, {"a": "1"}),
        (["a", "b"], {"a": "11111111111", "b": "1.23412"}, {}),
        (["a"], {"a": None, "b": "1.2a"}, {"a": None, "b": "1.2a"}),
    ],
)
def test_validate_decimal(fields, data, expected):
    validate_decimal(fields, data)
    assert data == expected


@pytest.mark.parametrize(
    "fields,data,expected",
    [
        (["a"], {"a": "12", "b": "1.2a"}, {"a": "12", "b": "1.2a"}),
        (["b"], {"a": "1.2", "b": "1.2a"}, {"a": "1.2"}),
        (["a", "b"], {"a": "1", "b": "1.2a"}, {"a": "1"}),
        (["a", "b"], {"a": "11111111111", "b": "1.23412"}, {"a": "11111111111"}),
        (["a"], {"a": None, "b": "1.2a"}, {"a": None, "b": "1.2a"}),
    ],
)
def test_validate_int(fields, data, expected):
    validate_int(fields, data)
    assert data == expected
