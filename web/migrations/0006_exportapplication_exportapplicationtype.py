# Generated by Django 2.2.13 on 2020-07-21 14:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0005_auto_20200708_1405"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExportApplicationType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("type_code", models.CharField(max_length=30)),
                ("type", models.CharField(max_length=70)),
                ("allow_multiple_products", models.BooleanField()),
                ("generate_cover_letter", models.BooleanField()),
                ("allow_hse_authorization", models.BooleanField()),
                (
                    "country_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="web.CountryGroup"
                    ),
                ),
                (
                    "country_group_for_manufacture",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="manufacture_export_application_types",
                        to="web.CountryGroup",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ExportApplication",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("IN_PROGRESS", "In Progress"),
                            ("SUBMITTED", "Submitted"),
                            ("PROCESSING", "Processing"),
                            ("COMPLETED", "Completed"),
                            ("WITHDRAWN", "Withdrawn"),
                            ("STOPPED", "Stopped"),
                            ("REVOKED", "Revoked"),
                            ("VARIATION", "Case Variation"),
                            ("DELETED", "Deleted"),
                        ],
                        max_length=30,
                    ),
                ),
                ("reference", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "decision",
                    models.CharField(
                        blank=True,
                        choices=[("REFUSE", "Refuse"), ("APPROVE", "Approve")],
                        max_length=10,
                        null=True,
                    ),
                ),
                ("refuse_reason", models.CharField(blank=True, max_length=4000, null=True)),
                ("last_update_datetime", models.DateTimeField(auto_now=True)),
                ("variation_no", models.IntegerField(default=0)),
                ("submit_datetime", models.DateTimeField(blank=True, null=True)),
                (
                    "application_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="web.ExportApplicationType"
                    ),
                ),
                ("case_notes", models.ManyToManyField(to="web.CaseNote")),
                (
                    "contact",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="contact_export_applications",
                        to="web.User",
                    ),
                ),
                ("countries", models.ManyToManyField(to="web.Country")),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="created_export_applications",
                        to="web.User",
                    ),
                ),
                (
                    "exporter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="export_applications",
                        to="web.Exporter",
                    ),
                ),
                (
                    "exporter_office",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="office_export_applications",
                        to="web.Office",
                    ),
                ),
                (
                    "further_information_requests",
                    models.ManyToManyField(to="web.FurtherInformationRequest"),
                ),
                (
                    "last_updated_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="updated_export_cases",
                        to="web.User",
                    ),
                ),
                (
                    "submitted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="submitted_export_application",
                        to="web.User",
                    ),
                ),
                ("update_requests", models.ManyToManyField(to="web.UpdateRequest")),
                ("variation_requests", models.ManyToManyField(to="web.VariationRequest")),
            ],
        ),
    ]
