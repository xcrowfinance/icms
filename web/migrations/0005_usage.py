# Generated by Django 3.1.3 on 2020-12-01 14:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0004_alter_commodity"),
    ]

    operations = [
        migrations.CreateModel(
            name="Usage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("application_subtype", models.CharField(max_length=50)),
                ("start_datetime", models.DateTimeField()),
                ("end_datetime", models.DateTimeField(blank=True, null=True)),
                ("maximum_allocation", models.IntegerField(blank=True, null=True)),
                (
                    "application_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="web.importapplicationtype"
                    ),
                ),
                (
                    "commodity_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="usages",
                        to="web.commoditygroup",
                    ),
                ),
                (
                    "country",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="web.country"
                    ),
                ),
            ],
            options={
                "ordering": ("-start_datetime",),
            },
        ),
    ]
