# Generated by Django 2.2.2 on 2019-06-19 10:55

import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import web.models.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('web', '0014_auto_20190529_1454'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commodity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False)),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField(blank=True, null=True)),
                ('commodity_code', models.CharField(max_length=10)),
                ('commodity_type', models.CharField(choices=[('TEXTILES', 'Textiles'), ('IRON_STEEL', 'Iron, Steel and Aluminium'), ('FIREARMS_AMMO', 'Firearms and Ammunition'), ('WOOD', 'Wood'), ('VEHICLES', 'Vehicles'), ('WOOD_CHARCOAL', 'Wood Charcoal'), ('PRECIOUS_METAL_STONE', 'Precious Metals and Stones'), ('OIL_PETROCHEMICALS', 'Oil and Petrochemicals')], max_length=20)),
                ('validity_start_date', models.DateField(null=True)),
                ('validity_end_date', models.DateField(blank=True, null=True)),
                ('quantity_threshold', models.IntegerField(blank=True, null=True)),
                ('sigl_product_type', models.CharField(blank=True, max_length=3, null=True)),
            ],
            options={
                'ordering': ('commodity_code',),
            },
            bases=(web.models.mixins.Archivable, models.Model),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=4000)),
                ('is_active', models.BooleanField(default=False)),
                ('type', models.CharField(choices=[('SOVEREIGN_TERRITORY', 'Sovereign Territory'), ('SYSTEM', 'System')], max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('group', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='roles', serialize=False, to='auth.Group')),
                ('description', models.CharField(blank=True, max_length=4000, null=True)),
                ('role_order', models.IntegerField()),
            ],
            options={
                'ordering': ('role_order',),
            },
            bases=('auth.group',),
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_type', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=100)),
                ('short_description', models.CharField(max_length=30)),
                ('hmrc_code', models.IntegerField()),
            ],
        ),
        migrations.AlterModelOptions(
            name='template',
            options={'ordering': ('-is_active',)},
        ),
        migrations.AlterField(
            model_name='alternativeemail',
            name='type',
            field=models.CharField(choices=[('WORK', 'Work'), ('HOME', 'Home')], default='WORK', max_length=30),
        ),
        migrations.AlterField(
            model_name='personalemail',
            name='type',
            field=models.CharField(choices=[('WORK', 'Work'), ('HOME', 'Home')], default='WORK', max_length=30),
        ),
        migrations.AlterField(
            model_name='phonenumber',
            name='type',
            field=models.CharField(choices=[('WORK', 'Work'), ('FAX', 'Fax'), ('MOBILE', 'Mobile'), ('HOME', 'Home'), ('MINICOM', 'Minicom')], default='WORK', max_length=30),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('description', models.CharField(blank=True, max_length=4000, null=True)),
                ('addresses', models.ManyToManyField(to='web.Address')),
                ('members', models.ManyToManyField(to='web.User')),
                ('roles', models.ManyToManyField(to='web.Role')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Constabulary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('region', models.CharField(choices=[('EM', 'East Midlands'), ('ER', 'Eastern'), ('IM', 'Isle of Man'), ('LO', 'London'), ('NE', 'North East'), ('NW', 'North WEST'), ('RU', 'Royal Ulster'), ('SC', 'Scotland'), ('SE', 'South East'), ('SW', 'South West'), ('WM', 'West Midlands')], max_length=3)),
                ('email', models.EmailField(max_length=254)),
                ('is_active', models.BooleanField(default=False)),
                ('contacts', models.ManyToManyField(blank=True, to='web.User')),
            ],
            bases=(web.models.mixins.Archivable, models.Model),
        ),
        migrations.CreateModel(
            name='CommodityGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False)),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField(blank=True, null=True)),
                ('group_type', models.CharField(choices=[('AUTO', 'Auto'), ('CATEGORY', 'Category')], default='AUTO', max_length=20)),
                ('group_code', models.CharField(max_length=25)),
                ('group_name', models.CharField(blank=True, max_length=100, null=True)),
                ('group_description', models.CharField(blank=True, max_length=4000, null=True)),
                ('commodity_type', models.CharField(blank=True, choices=[('TEXTILES', 'Textiles'), ('IRON_STEEL', 'Iron, Steel and Aluminium'), ('FIREARMS_AMMO', 'Firearms and Ammunition'), ('WOOD', 'Wood'), ('VEHICLES', 'Vehicles'), ('WOOD_CHARCOAL', 'Wood Charcoal'), ('PRECIOUS_METAL_STONE', 'Precious Metals and Stones'), ('OIL_PETROCHEMICALS', 'Oil and Petrochemicals')], max_length=20, null=True)),
                ('commodities', models.ManyToManyField(blank=True, to='web.Commodity')),
                ('unit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='web.Unit')),
            ],
            bases=(web.models.mixins.Archivable, models.Model),
        ),
    ]
