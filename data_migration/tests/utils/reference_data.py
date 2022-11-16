from datetime import datetime

from data_migration.queries import reference

ref_query_result = {
    reference.country: (
        [("id",), ("name",), ("is_active",), ("type",), ("commission_code",), ("hmrc_code",)],
        [
            (1, "CA", 1, "A", 100, "CA"),
            (2, "CB", 1, "A", 101, "CB"),
            (3, "CC", 1, "B", 102, "CC"),
            (4, "CD", 0, "A", 103, "CD"),
        ],
    ),
    reference.country_group: (
        [("country_group_id",), ("name",), ("comments",)],
        [
            ("A", "TEST GROUP A", None),
            ("B", "TEST GROUP B", "Comment B"),
            ("C", "TEST GROUP C", "Comment C"),
        ],
    ),
    reference.unit: (
        [("unit_type",), ("description",), ("short_description",), ("hmrc_code",)],
        [
            ("GS", "grams", "gs", 100),
            ("KGS", "kilos", "Kgs", 101),
            ("TBS", "terrabytes", "Tbs", 102),
        ],
    ),
    reference.constabularies: (
        [("id",), ("is_active",), ("name",), ("region",), ("email",)],
        [
            (1, 1, "A", "A", "a@example.com"),  # /PS-IGNORE
            (2, 1, "B", "B", "b@example.com"),  # /PS-IGNORE
            (3, 1, "C", "C", "c@example.com"),  # /PS-IGNORE
        ],
    ),
    reference.commodity_type: (
        [("type_code",), ("com_type_title",)],
        [("TYPE_A", "Type A"), ("TYPE_B", "Type B"), ("TYPE_C", "Type C")],
    ),
    reference.commodity_group: (
        [
            ("id",),
            ("is_active",),
            ("group_type",),
            ("group_code",),
            ("group_name",),
            ("group_description",),
            ("start_datetime",),
            ("end_datetime",),
            ("commodity_type_id",),
            ("unit_id",),
        ],
        [
            (1, 1, "AT", "AC", "AN", "AD", datetime.now(), None, "TYPE_A", "KGS"),
            (2, 1, "BT", "BC", "BN", "BD", datetime.now(), None, "TYPE_B", "KGS"),
        ],
    ),
    reference.commodity: (
        [
            ("id",),
            ("is_active",),
            ("commodity_code",),
            ("commodity_type_id",),
            ("validity_start_date",),
            ("validity_end_date",),
            ("quantity_threshold",),
            ("sigl_product_type",),
            ("start_datetime",),
            ("end_datetime",),
        ],
        [
            (1, 1, 1000, "TYPE_A", datetime.now(), None, None, "TEX", datetime.now(), None),
            (2, 1, 1001, "TYPE_A", datetime.now(), None, None, "TEX", datetime.now(), None),
            (3, 1, 1002, "TYPE_B", datetime.now(), None, None, None, datetime.now(), None),
            (4, 1, 1003, "TYPE_B", datetime.now(), None, None, None, datetime.now(), None),
            (5, 1, 1004, "TYPE_C", datetime.now(), None, None, None, datetime.now(), None),
        ],
    ),
    reference.obsolete_calibre_group: (
        [("id",), ("legacy_id",), ("name",), ("is_active",), ("order",)],
        [(1, 1, "Test OC Group", 1, 1), (2, 2, "Another OC Group", 1, 2), (3, 123, "C", 1, 3)],
    ),
    reference.obsolete_calibre: (
        [("id",), ("legacy_id",), ("name",), ("is_active",), ("order",), ("calibre_group_id",)],
        [(1, 3, "Inactive Test OC", 0, 2, 2), (2, 444, "Test OC", 1, 1, 1)],
    ),
}
