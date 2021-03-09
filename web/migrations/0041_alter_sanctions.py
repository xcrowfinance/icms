# Generated by Django 3.1.5 on 2021-03-05 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0040_sanctionsandadhocapplicationgoods"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sanctionsandadhocapplication",
            name="exporter_address",
            field=models.CharField(blank=True, max_length=4096, null=True),
        ),
        migrations.AlterField(
            model_name="sanctionsandadhocapplication",
            name="exporter_name",
            field=models.CharField(blank=True, max_length=4096, null=True),
        ),
        migrations.AlterField(
            model_name="sanctionsandadhocapplicationgoods",
            name="goods_description",
            field=models.CharField(max_length=4096),
        ),
        migrations.AlterField(
            model_name="sanctionsandadhocapplicationgoods",
            name="quantity_amount",
            field=models.DecimalField(decimal_places=2, max_digits=9),
        ),
        migrations.AlterField(
            model_name="sanctionsandadhocapplicationgoods",
            name="value",
            field=models.DecimalField(decimal_places=2, max_digits=9),
        ),
    ]
