# Generated by Django 3.1.12 on 2021-06-14 15:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0067_importapplication_issue_paper_licence_only"),
    ]

    operations = [
        migrations.CreateModel(
            name="SILChecklist",
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
                        max_length=3,
                        null=True,
                        verbose_name="Authority to possess required?",
                    ),
                ),
                (
                    "authority_received",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No"), ("n/a", "N/A")],
                        max_length=3,
                        null=True,
                        verbose_name="Authority to possess received?",
                    ),
                ),
                (
                    "authority_cover_items_listed",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No"), ("n/a", "N/A")],
                        max_length=3,
                        null=True,
                        verbose_name="Authority to possess covers items listed?",
                    ),
                ),
                (
                    "quantities_within_authority_restrictions",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No"), ("n/a", "N/A")],
                        max_length=3,
                        null=True,
                        verbose_name="Quantities listed within authority to possess restrictions?",
                    ),
                ),
                (
                    "authority_police",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No"), ("n/a", "N/A")],
                        max_length=3,
                        null=True,
                        verbose_name="Authority to possess checked with police?",
                    ),
                ),
                (
                    "import_application",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="checklist",
                        to="web.silapplication",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]