# Generated by Django 3.1.5 on 2021-02-15 16:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0024_auto_20210215_1613"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChecklistFirearmsOILApplication",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "case_update",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No"), ("n/a", "N/A")],
                        max_length=3,
                        null=True,
                        verbose_name="Case update required from applicant?",
                    ),
                ),
                (
                    "fir_required",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No"), ("n/a", "N/A")],
                        max_length=3,
                        null=True,
                        verbose_name="Further information request required?",
                    ),
                ),
                (
                    "response_preparation",
                    models.BooleanField(
                        default=False,
                        verbose_name="Response Preparation - approve/refuse the request, edit details if necessary",
                    ),
                ),
                (
                    "validity_period_correct",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No"), ("n/a", "N/A")],
                        max_length=3,
                        null=True,
                        verbose_name="Validity period correct?",
                    ),
                ),
                (
                    "endorsements_listed",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No"), ("n/a", "N/A")],
                        max_length=3,
                        null=True,
                        verbose_name="Correct endorsements listed? Add/edit/remove as required (changes are automatically saved)",
                    ),
                ),
                (
                    "authorisation",
                    models.BooleanField(
                        default=False,
                        verbose_name="Authorisation - start authorisation (close case processing) to authorise the licence. Errors logged must be resolved.",
                    ),
                ),
                (
                    "authority_required",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No"), ("n/a", "N/A")],
                        max_length=10,
                        null=True,
                        verbose_name="Authority to possess required?",
                    ),
                ),
                (
                    "authority_received",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No"), ("n/a", "N/A")],
                        max_length=10,
                        null=True,
                        verbose_name="Authority to possess received?",
                    ),
                ),
                (
                    "authority_police",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No"), ("n/a", "N/A")],
                        max_length=10,
                        null=True,
                        verbose_name="Authority to possess checked with police?",
                    ),
                ),
                (
                    "import_application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="checklists",
                        to="web.openindividuallicenceapplication",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
