import datetime
from datetime import date

from django.test import TestCase
from django.utils.timezone import now

from web.models import Commodity, CommodityGroup, CommodityType
from web.tests.domains.commodity.factory import CommodityFactory, CommodityGroupFactory


class TestCommodity(TestCase):
    def create_commodity(
        self,
        is_active=True,
        commodity_code="1234567890",
        validity_start_date=date.today(),
        validity_end_date=date.today() + datetime.timedelta(days=10),
        quantity_threshold=8,
        sigl_product_type="xyz",
    ):
        return CommodityFactory.create(
            is_active=is_active,
            commodity_code=commodity_code,
            validity_start_date=validity_start_date,
            validity_end_date=validity_end_date,
            quantity_threshold=quantity_threshold,
            sigl_product_type=sigl_product_type,
            commodity_type=CommodityType.objects.first(),
        )

    def test_create_commodity(self):
        commodity = self.create_commodity()
        assert isinstance(commodity, Commodity)
        assert commodity.commodity_code == "1234567890"

    def test_archive_commodity(self):
        commodity = self.create_commodity()
        commodity.archive()
        assert commodity.is_active is False

    def test_unarchive_commodity(self):
        commodity = self.create_commodity()
        commodity.unarchive()
        assert commodity.is_active is True


class TestCommodityGroup(TestCase):
    def create_commodity_group(
        self,
        is_active=True,
        group_type=CommodityGroup.AUTO,
        group_code="12",
        group_description="Test group description",
        start_datetime=now(),
        end_datetime=now() + datetime.timedelta(days=20),
    ):
        return CommodityGroupFactory.create(
            is_active=is_active,
            group_type=group_type,
            group_code=group_code,
            group_description=group_description,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )

    def test_create_commodity_group(self):
        commodity_group = self.create_commodity_group()
        assert isinstance(commodity_group, CommodityGroup)
        assert commodity_group.group_code == "12"

    def test_archive_commodity_group(self):
        commodity_group = self.create_commodity_group()
        commodity_group.archive()
        assert commodity_group.is_active is False

    def test_unarchive_commodity_group(self):
        commodity_group = self.create_commodity_group()
        commodity_group.unarchive()
        assert commodity_group.is_active is True
