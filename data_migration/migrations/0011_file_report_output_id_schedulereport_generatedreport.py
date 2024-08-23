# Generated by Django 4.2.14 on 2024-07-31 14:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data_migration", "0010_caseemail_closed_by_caseemail_email_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="file",
            name="report_output_id",
            field=models.IntegerField(null=True, unique=True),
        ),
        migrations.CreateModel(
            name="ScheduleReport",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("report_domain", models.CharField(max_length=300)),
                ("title", models.CharField(max_length=400)),
                ("notes", models.TextField(blank=True, null=True)),
                ("parameters_xml", models.TextField(null=True)),
                ("started_at", models.DateTimeField(null=True)),
                ("finished_at", models.DateTimeField(null=True)),
                ("deleted_at", models.DateTimeField(null=True)),
                ("parameters", models.JSONField(null=True)),
                (
                    "deleted_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="data_migration.user",
                    ),
                ),
                (
                    "scheduled_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="data_migration.user",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="GeneratedReport",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "report_output",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="data_migration.file",
                        to_field="report_output_id",
                    ),
                ),
                (
                    "schedule",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="data_migration.schedulereport",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]