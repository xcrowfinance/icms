# Generated by Django 2.2.10 on 2020-02-10 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0077_default_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accessrequest',
            name='agent_address',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='accessrequest',
            name='agent_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='accessrequest',
            name='request_reason',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='template',
            name='template_type',
            field=models.CharField(choices=[('ENDORSEMENT', 'Endorsement'), ('LETTER_TEMPLATE', 'Letter template'), ('EMAIL_TEMPLATE', 'Email template'), ('CFS_TRANSLATION', 'CFS translation'), ('DECLARATION', 'Declaration')], max_length=50),
        ),
    ]