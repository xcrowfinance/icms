# Generated by Django 2.2.13 on 2020-07-30 11:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0008_constabularyemail_importapplication_importapplicationtype"),
    ]

    operations = [
        migrations.AddField(
            model_name="exportapplication",
            name="agent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="agent_export_applications",
                to="web.Exporter",
            ),
        ),
        migrations.AddField(
            model_name="exportapplication",
            name="agent_office",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="agent_office_export_applications",
                to="web.Office",
            ),
        ),
    ]
