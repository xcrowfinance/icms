# Generated by Django 4.2.14 on 2024-07-23 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0021_alter_silapplication_verified_section5"),
    ]

    operations = [
        migrations.AlterField(
            model_name="approvalrequest",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("DRAFT", "Draft"),
                    ("OPEN", "Open"),
                    ("CANCELLED", "Cancelled"),
                    ("COMPLETED", "Completed"),
                ],
                default="OPEN",
                max_length=20,
                null=True,
            ),
        ),
    ]