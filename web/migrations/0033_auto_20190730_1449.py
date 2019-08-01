# Generated by Django 2.2.2 on 2019-07-30 14:49

from django.db import migrations, models
import django.db.models.deletion
import web.models.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0032_auto_20190701_0856'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='entry_type',
            field=models.CharField(default='EMPTY', max_length=10),
        ),
        migrations.AlterField(
            model_name='address',
            name='address',
            field=models.CharField(max_length=4000, null=True),
        ),
        migrations.CreateModel(
            name='Importer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('type', models.CharField(choices=[('INDIVIDUAL', 'Individual'), ('ORGANISATION', 'Organisation')], max_length=20)),
                ('title', models.CharField(blank=True, max_length=20, null=True)),
                ('name', models.CharField(max_length=4000)),
                ('last_name', models.CharField(max_length=4000)),
                ('registered_number', models.CharField(blank=True, max_length=15, null=True)),
                ('eori_number', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=60)),
                ('region_origin', models.CharField(blank=True, choices=[(None, 'UK'), ('E', 'Europe'), ('O', 'Non-European')], max_length=1, null=True)),
                ('comments', models.CharField(blank=True, max_length=4000, null=True)),
                ('addresses', models.ManyToManyField(to='web.Address')),
                ('main_importer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='agents', to='web.Importer')),
                ('members', models.ManyToManyField(to='web.User')),
                ('offices', models.ManyToManyField(related_name='importers', to='web.Address')),
                ('roles', models.ManyToManyField(to='web.Role')),
            ],
            options={
                'abstract': False,
            },
            bases=(web.models.mixins.Archivable, models.Model),
        ),
        migrations.CreateModel(
            name='Exporter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=4000)),
                ('registered_number', models.CharField(blank=True, max_length=15, null=True)),
                ('comments', models.CharField(blank=True, max_length=4000, null=True)),
                ('addresses', models.ManyToManyField(to='web.Address')),
                ('main_exporter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='agents', to='web.Exporter')),
                ('members', models.ManyToManyField(to='web.User')),
                ('offices', models.ManyToManyField(related_name='exporters', to='web.Address')),
                ('roles', models.ManyToManyField(to='web.Role')),
            ],
            options={
                'abstract': False,
            },
            bases=(web.models.mixins.Archivable, models.Model),
        ),
    ]
