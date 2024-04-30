# Generated by Django 4.2.11 on 2024-04-30 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data_migration", "0003_gmp_address_entry_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="exportapplicationcertificate",
            name="revoke_email_sent",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="exportapplicationcertificate",
            name="revoke_reason",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="importapplicationlicence",
            name="revoke_email_sent",
            field=models.BooleanField(),
        ),
        migrations.AddField(
            model_name="importapplicationlicence",
            name="revoke_reason",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="importapplicationlicence",
            name="updated_at",
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name="exportapplication",
            name="last_update_datetime",
            field=models.DateTimeField(),
        ),
    ]
