# Generated by Django 2.2.4 on 2019-08-28 14:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0050_auto_20190827_1101'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('applicant_reference', models.CharField(blank=True, max_length=500, null=True)),
                ('submit_datetime', models.DateTimeField(blank=True, null=True)),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RenameField(
            model_name='importapplicationtype',
            old_name='chief_license_prefix',
            new_name='chief_licence_prefix',
        ),
        migrations.RenameField(
            model_name='importapplicationtype',
            old_name='default_license_length_months',
            new_name='default_licence_length_months',
        ),
        migrations.RenameField(
            model_name='importapplicationtype',
            old_name='electronic_license_flag',
            new_name='electronic_licence_flag',
        ),
        migrations.RenameField(
            model_name='importapplicationtype',
            old_name='license_category_description',
            new_name='licence_category_description',
        ),
        migrations.RenameField(
            model_name='importapplicationtype',
            old_name='paper_license_flag',
            new_name='paper_licence_flag',
        ),
        migrations.RemoveField(
            model_name='commodity',
            name='commodity_type',
        ),
        migrations.CreateModel(
            name='ImportCase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('IN_PROGRESS', 'In Progress'), ('SUBMITTED', 'Submitted'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('WITHDRAWN', 'Withdrawn'), ('STOPPED', 'Stopped'), ('REVOKED', 'Revoked'), ('VARIATION_REQUESTED', 'Variation Requested'), ('DELETED', 'Deleted')], max_length=30)),
                ('reference', models.CharField(blank=True, max_length=50, null=True)),
                ('variation_no', models.IntegerField(default=0)),
                ('legacy_case_flag', models.BooleanField(default=False)),
                ('chief_usage_status', models.CharField(blank=True, choices=[('C', 'Cancelled'), ('E', 'Exhausted'), ('D', 'Expired'), ('S', 'S')], max_length=1, null=True)),
                ('under_appeal_flag', models.BooleanField(default=False)),
                ('decision', models.CharField(blank=True, choices=[('REFUSE', 'Refuse'), ('APPROVE', 'Approve')], max_length=10, null=True)),
                ('variation_decision', models.CharField(blank=True, choices=[('REFUSE', 'Refuse'), ('APPROVE', 'Approve')], max_length=10, null=True)),
                ('refuse_reason', models.CharField(blank=True, max_length=4000, null=True)),
                ('variation_refuse_reason', models.CharField(blank=True, max_length=4000, null=True)),
                ('issue_date', models.DateField(blank=True, null=True)),
                ('licence_start_date', models.DateField(blank=True, null=True)),
                ('licence_end_date', models.DateField(blank=True, null=True)),
                ('licence_extended_flag', models.BooleanField(default=False)),
                ('last_update_datetime', models.DateTimeField(auto_now=True)),
                ('application', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='case', to='web.ImportApplication')),
                ('last_updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='updated_import_cases', to='web.User')),
            ],
        ),
        migrations.AddField(
            model_name='importapplication',
            name='application_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='web.ImportApplicationType'),
        ),
        migrations.AddField(
            model_name='importapplication',
            name='consignment_country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='import_applications_to', to='web.Country'),
        ),
        migrations.AddField(
            model_name='importapplication',
            name='contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='contact_import_applications', to='web.User'),
        ),
        migrations.AddField(
            model_name='importapplication',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_import_applications', to='web.User'),
        ),
        migrations.AddField(
            model_name='importapplication',
            name='importer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='import_applications', to='web.Importer'),
        ),
        migrations.AddField(
            model_name='importapplication',
            name='origin_country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='import_applications_from', to='web.Country'),
        ),
        migrations.AddField(
            model_name='importapplication',
            name='submitted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='submitted_import_applications', to='web.User'),
        ),
        migrations.CreateModel(
            name='CaseConstabularyEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('status', models.CharField(default='DRAFT', max_length=30)),
                ('email_cc_address_list', models.CharField(blank=True, max_length=4000, null=True)),
                ('email_subject', models.CharField(blank=True, max_length=100, null=True)),
                ('email_body', models.CharField(blank=True, max_length=4000, null=True)),
                ('email_sent_datetime', models.DateTimeField(blank=True, null=True)),
                ('email_closed_datetime', models.DateTimeField(blank=True, null=True)),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='web.ImportCase')),
            ],
        ),
    ]
