# Generated by Django 3.1.8 on 2021-04-20 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0049_sanctionemail"),
    ]

    operations = [
        migrations.AddField(
            model_name="derogationsapplication",
            name="supporting_documents",
            field=models.ManyToManyField(
                related_name="_derogationsapplication_supporting_documents_+", to="web.File"
            ),
        ),
    ]
