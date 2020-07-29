# Generated by Django 2.2.13 on 2020-07-25 16:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("viewflow", "0009_merge"),
        ("web", "0006_exportapplication_exportapplicationtype"),
    ]

    operations = [
        migrations.CreateModel(
            name="FurtherInformationRequestProcess",
            fields=[
                (
                    "process_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="viewflow.Process",
                    ),
                ),
                ("object_id", models.PositiveIntegerField()),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="contenttypes.ContentType"
                    ),
                ),
                (
                    "fir",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="web.FurtherInformationRequest",
                    ),
                ),
            ],
            options={"abstract": False,},
            bases=("viewflow.process",),
        ),
    ]