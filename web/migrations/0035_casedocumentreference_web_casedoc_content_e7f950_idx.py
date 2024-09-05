# Generated by Django 4.2.15 on 2024-09-03 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0034_alter_caseemail_template_code_and_more"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="casedocumentreference",
            index=models.Index(
                fields=["content_type", "object_id"], name="web_casedoc_content_e7f950_idx"
            ),
        ),
    ]