# Generated by Django 4.1.2 on 2023-01-13 10:20

from django.db import migrations

FIREARMS_ACT_DATA = [
    {
        "act": "Section 1 Firearms",
        "id": 1,
    },
    {
        "act": "Section 1 Shotguns",
        "id": 2,
    },
    {
        "act": "Section 2 Shotguns",
        "id": 3,
    },
    {
        "act": "Section 1 Component Parts",
        "id": 4,
    },
    {
        "act": "Section 1 Ammunition",
        "id": 5,
    },
    {
        "act": "Expanding Ammunition 5(1A)(f)",
        "id": 6,
    },
    {
        "act": "Suppressors",
        "id": 7,
    },
]


def load_firearms_act_data(apps, schema_editor):
    FirearmsAct = apps.get_model("data_migration", "FirearmsAct")

    FirearmsAct.objects.bulk_create(
        [FirearmsAct(created_by_id=0, **row) for row in FIREARMS_ACT_DATA]
    )


class Migration(migrations.Migration):

    dependencies = [
        ("data_migration", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_firearms_act_data),
    ]
