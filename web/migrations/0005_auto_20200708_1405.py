# Generated by Django 2.2.13 on 2020-07-08 14:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("viewflow", "0009_merge"),
        ("web", "0004_accessrequestprocess_re_link"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="AccessRequestProcess", new_name="ExporterAccessRequestProcess",
        ),
        migrations.CreateModel(
            name="ImporterAccessRequestProcess",
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
                ("approval_required", models.BooleanField(default=False)),
                ("restart_approval", models.BooleanField(default=False)),
                ("re_link", models.BooleanField(default=False)),
                (
                    "access_request",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="web.AccessRequest",
                    ),
                ),
            ],
            options={"abstract": False,},
            bases=("viewflow.process",),
        ),
    ]
