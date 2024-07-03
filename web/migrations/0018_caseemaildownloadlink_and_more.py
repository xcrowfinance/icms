# Generated by Django 4.2.13 on 2024-06-25 13:43

import uuid

import django.db.models.deletion
from django.db import migrations, models

import web.domains.case.models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0017_alter_derogationsapplication_commodity_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CaseEmailDownloadLink",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("code", models.UUIDField(default=uuid.uuid4, editable=False)),
                (
                    "check_code",
                    models.CharField(
                        default=web.domains.case.models.create_check_code,
                        editable=False,
                        max_length=8,
                    ),
                ),
                ("email", models.EmailField(max_length=254)),
                ("failure_count", models.IntegerField(default=0)),
                ("expired", models.BooleanField(default=False)),
                ("sent_at_datetime", models.DateTimeField(auto_now_add=True)),
                (
                    "case_email",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="web.caseemail"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ConstabularyLicenceDownloadLink",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("code", models.UUIDField(default=uuid.uuid4, editable=False)),
                (
                    "check_code",
                    models.CharField(
                        default=web.domains.case.models.create_check_code,
                        editable=False,
                        max_length=8,
                    ),
                ),
                ("email", models.EmailField(max_length=254)),
                ("failure_count", models.IntegerField(default=0)),
                ("expired", models.BooleanField(default=False)),
                ("sent_at_datetime", models.DateTimeField(auto_now_add=True)),
                (
                    "constabulary",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="web.constabulary",
                    ),
                ),
                (
                    "licence",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="web.importapplicationlicence",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AlterField(
            model_name="casedocumentreference",
            name="check_code",
            field=models.CharField(
                default=web.domains.case.models.create_check_code, max_length=16, null=True
            ),
        ),
        migrations.AlterField(
            model_name="emailtemplate",
            name="name",
            field=models.CharField(
                choices=[
                    ("ACCESS_REQUEST", "Access Request"),
                    ("ACCESS_REQUEST_CLOSED", "Access Request Closed"),
                    ("ACCESS_REQUEST_APPROVAL_COMPLETE", "Access Request Approval Complete"),
                    ("APPLICATION_COMPLETE", "Application Complete"),
                    (
                        "APPLICATION_VARIATION_REQUEST_COMPLETE",
                        "Application Variation Request Complete",
                    ),
                    ("APPLICATION_EXTENSION_COMPLETE", "Application Extension Complete"),
                    ("APPLICATION_STOPPED", "Application Stopped"),
                    ("APPLICATION_REFUSED", "Application Refused"),
                    ("APPLICATION_REASSIGNED", "Application Reassigned"),
                    ("APPLICATION_REOPENED", "Application Reopened"),
                    ("APPLICATION_UPDATE", "Application Update"),
                    ("APPLICATION_UPDATE_RESPONSE", "Application Update Response"),
                    (
                        "EXPORTER_ACCESS_REQUEST_APPROVAL_OPENED",
                        "Exporter Access Request Approval Opened",
                    ),
                    (
                        "IMPORTER_ACCESS_REQUEST_APPROVAL_OPENED",
                        "Importer Access Request Approval Opened",
                    ),
                    ("FIREARMS_SUPPLEMENTARY_REPORT", "Firearms Supplementary Report"),
                    ("CONSTABULARY_DEACTIVATED_FIREARMS", "Constabulary Deactivated Firearms"),
                    ("WITHDRAWAL_ACCEPTED", "Withdrawal Accepted"),
                    ("WITHDRAWAL_CANCELLED", "Withdrawal Cancelled"),
                    ("WITHDRAWAL_OPENED", "Withdrawal Opened"),
                    ("WITHDRAWAL_REJECTED", "Withdrawal Rejected"),
                    (
                        "APPLICATION_VARIATION_REQUEST_CANCELLED",
                        "Application Variation Request Cancelled",
                    ),
                    (
                        "APPLICATION_VARIATION_REQUEST_UPDATE_REQUIRED",
                        "Application Variation Request Update Required",
                    ),
                    (
                        "APPLICATION_VARIATION_REQUEST_UPDATE_CANCELLED",
                        "Application Variation Request Update Cancelled",
                    ),
                    (
                        "APPLICATION_VARIATION_REQUEST_UPDATE_RECEIVED",
                        "Application Variation Request Update Received",
                    ),
                    (
                        "APPLICATION_VARIATION_REQUEST_REFUSED",
                        "Application Variation Request Refused",
                    ),
                    ("CASE_EMAIL", "Case Email"),
                    ("CASE_EMAIL_WITH_DOCUMENTS", "Case Email With Documents"),
                    (
                        "APPLICATION_FURTHER_INFORMATION_REQUEST",
                        "Application Further Information Request",
                    ),
                    (
                        "APPLICATION_FURTHER_INFORMATION_REQUEST_RESPONDED",
                        "Application Further Information Request Responded",
                    ),
                    (
                        "APPLICATION_FURTHER_INFORMATION_REQUEST_WITHDRAWN",
                        "Application Further Information Request Withdrawn",
                    ),
                    (
                        "ACCESS_REQUEST_FURTHER_INFORMATION_REQUEST",
                        "Application Further Information Request",
                    ),
                    (
                        "ACCESS_REQUEST_FURTHER_INFORMATION_REQUEST_RESPONDED",
                        "Access Request Further Information Request Responded",
                    ),
                    (
                        "ACCESS_REQUEST_FURTHER_INFORMATION_REQUEST_WITHDRAWN",
                        "Access Request Further Information Request Withdrawn",
                    ),
                    ("LICENCE_REVOKED", "Licence Revoked"),
                    ("CERTIFICATE_REVOKED", "Certificate Revoked"),
                    ("AUTHORITY_ARCHIVED", "Authority Archived"),
                    ("AUTHORITY_EXPIRING_SECTION_5", "Authority Expiring Section 5"),
                    ("AUTHORITY_EXPIRING_FIREARMS", "Authority Expiring Firearms"),
                    ("MAILSHOT", "Mailshot"),
                    ("RETRACT_MAILSHOT", "Retract Mailshot"),
                    ("NEW_USER_WELCOME", "New User Welcome"),
                    ("ORG_CONTACT_INVITE", "New Organisation Contact Invite"),
                    ("IMA_CONSTAB_EMAIL", "Constabulary Email"),
                    ("IMA_SANCTIONS_EMAIL", "Sanctions Email"),
                    ("CA_HSE_EMAIL", "Health and Safety Email"),
                    ("CA_BEIS_EMAIL", "Business, Energy & Industrial Strategy Email"),
                    ("DEACTIVATE_USER", "Deactivate User Email"),
                    ("REACTIVATE_USER", "Reactivate User Email"),
                ],
                max_length=255,
                unique=True,
            ),
        ),
        migrations.DeleteModel(
            name="ImportApplicationDownloadLink",
        ),
    ]
