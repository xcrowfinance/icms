# Generated by Django 4.2.16 on 2024-09-11 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data_migration", "0011_file_report_output_id_schedulereport_generatedreport"),
    ]

    operations = [
        migrations.AddField(
            model_name="importapplicationlicence",
            name="issue_datetime",
            field=models.DateTimeField(null=True),
        ),
    ]