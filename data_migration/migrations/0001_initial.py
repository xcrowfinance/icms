# Generated by Django 3.2.12 on 2022-03-25 16:48

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Commodity",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("status", models.CharField(max_length=10)),
                ("commodity_code", models.CharField(max_length=10)),
                ("validity_start_date", models.DateField()),
                ("validity_end_date", models.DateField(null=True)),
                ("quantity_threshold", models.IntegerField(null=True)),
                ("sigl_product_type", models.CharField(max_length=3, null=True)),
                ("start_datetime", models.DateTimeField(null=True)),
                ("end_datetime", models.DateTimeField(null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CommodityGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("status", models.CharField(max_length=10)),
                ("group_type", models.CharField(max_length=20)),
                ("group_code", models.CharField(max_length=25, unique=True)),
                ("group_name", models.CharField(max_length=100, null=True)),
                ("group_description", models.CharField(max_length=4000, null=True)),
                ("start_datetime", models.DateTimeField(null=True)),
                ("end_datetime", models.DateTimeField(null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CommodityType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("type_code", models.CharField(max_length=20, unique=True)),
                ("type", models.CharField(max_length=50)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Constabulary",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=50)),
                ("region", models.CharField(max_length=3)),
                ("email", models.EmailField(max_length=254)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Country",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=4000)),
                ("status", models.CharField(max_length=10)),
                ("type", models.CharField(max_length=30)),
                ("commission_code", models.CharField(max_length=20)),
                ("hmrc_code", models.CharField(max_length=20)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CountryGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("country_group_id", models.CharField(max_length=15, unique=True)),
                ("name", models.CharField(max_length=4000, unique=True)),
                ("comments", models.CharField(max_length=4000, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CountryTranslationSet",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("status", models.CharField(max_length=10)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ImportApplication",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("imad_id", models.IntegerField(unique=True)),
                ("status", models.CharField(max_length=30)),
                ("submit_datetime", models.DateTimeField(null=True)),
                ("reference", models.CharField(max_length=100, null=True, unique=True)),
                ("decision", models.CharField(max_length=10, null=True)),
                ("refuse_reason", models.CharField(max_length=4000, null=True)),
                ("acknowledged_datetime", models.DateTimeField(null=True)),
                ("applicant_reference", models.CharField(max_length=500, null=True)),
                ("create_datetime", models.DateTimeField()),
                ("variation_no", models.IntegerField(default=0)),
                ("legacy_case_flag", models.CharField(max_length=5, null=True)),
                ("chief_usage_status", models.CharField(max_length=1, null=True)),
                ("under_appeal_flag", models.CharField(max_length=5, null=True)),
                ("variation_decision", models.CharField(max_length=10, null=True)),
                ("variation_refuse_reason", models.CharField(max_length=4000, null=True)),
                ("issue_date", models.DateField(null=True)),
                ("licence_extended_flag", models.CharField(max_length=5, null=True)),
                ("licence_reference", models.CharField(max_length=100, null=True, unique=True)),
                ("last_update_datetime", models.DateTimeField(auto_now=True)),
                ("cover_letter", models.TextField(null=True)),
                ("imi_submit_datetime", models.DateTimeField(null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ImportApplicationType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("status", models.CharField(max_length=10)),
                ("type", models.CharField(max_length=70)),
                ("sub_type", models.CharField(max_length=70, null=True)),
                ("licence_type_code", models.CharField(max_length=20)),
                ("sigl_flag", models.CharField(max_length=5)),
                ("chief_flag", models.CharField(max_length=5)),
                ("chief_licence_prefix", models.CharField(max_length=10, null=True)),
                ("paper_licence_flag", models.CharField(max_length=5)),
                ("electronic_licence_flag", models.CharField(max_length=5)),
                ("cover_letter_flag", models.CharField(max_length=5)),
                ("cover_letter_schedule_flag", models.CharField(max_length=5)),
                ("category_flag", models.CharField(max_length=5)),
                ("sigl_category_prefix", models.CharField(max_length=100, null=True)),
                ("chief_category_prefix", models.CharField(max_length=10, null=True)),
                ("default_licence_length_months", models.IntegerField(null=True)),
                ("endorsements_flag", models.CharField(max_length=5)),
                ("default_commodity_desc", models.CharField(max_length=200, null=True)),
                ("quantity_unlimited_flag", models.CharField(max_length=5)),
                ("unit_list_csv", models.CharField(max_length=200, null=True)),
                ("exp_cert_upload_flag", models.CharField(max_length=5)),
                ("supporting_docs_upload_flag", models.CharField(max_length=5)),
                ("multiple_commodities_flag", models.CharField(max_length=5)),
                ("guidance_file_url", models.CharField(max_length=4000, null=True)),
                ("licence_category_description", models.CharField(max_length=1000, null=True)),
                ("usage_auto_category_desc_flag", models.CharField(max_length=5)),
                ("case_checklist_flag", models.CharField(max_length=5)),
                ("importer_printable", models.CharField(max_length=5)),
                ("declaration_template_mnem", models.CharField(max_length=50)),
                (
                    "commodity_type",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="data_migration.commoditytype",
                        to_field="type_code",
                    ),
                ),
                (
                    "consignment_country_group",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="data_migration.countrygroup",
                        to_field="country_group_id",
                    ),
                ),
                (
                    "default_commodity_group",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="data_migration.commoditygroup",
                        to_field="group_code",
                    ),
                ),
                (
                    "master_country_group",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="data_migration.countrygroup",
                        to_field="country_group_id",
                    ),
                ),
                (
                    "origin_country_group",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="data_migration.countrygroup",
                        to_field="country_group_id",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Office",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("postcode", models.CharField(max_length=30, null=True)),
                ("address", models.CharField(max_length=4000, null=True)),
                ("eori_number", models.CharField(max_length=20, null=True)),
                ("address_entry_type", models.CharField(default="EMPTY", max_length=10)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Process",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("process_type", models.CharField(default=None, max_length=50)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("finished", models.DateTimeField(null=True)),
                ("ima_id", models.IntegerField(null=True, unique=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Unit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("unit_type", models.CharField(max_length=20, unique=True)),
                ("description", models.CharField(max_length=100)),
                ("short_description", models.CharField(max_length=30)),
                ("hmrc_code", models.IntegerField()),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("is_superuser", models.BooleanField(default=False)),
                ("username", models.CharField(max_length=150, unique=True)),
                ("first_name", models.CharField(max_length=150)),
                ("last_name", models.CharField(max_length=150)),
                ("email", models.EmailField(max_length=254)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("password", models.CharField(max_length=128)),
                ("last_login", models.DateTimeField(null=True)),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now)),
                ("title", models.CharField(max_length=20, null=True)),
                ("preferred_first_name", models.CharField(max_length=4000, null=True)),
                ("middle_initials", models.CharField(max_length=40, null=True)),
                ("organisation", models.CharField(max_length=4000, null=True)),
                ("department", models.CharField(max_length=4000, null=True)),
                ("job_title", models.CharField(max_length=320, null=True)),
                ("location_at_address", models.CharField(max_length=4000, null=True)),
                ("work_address", models.CharField(max_length=300, null=True)),
                ("date_of_birth", models.DateField(null=True)),
                ("security_question", models.CharField(max_length=4000, null=True)),
                ("security_answer", models.CharField(max_length=4000, null=True)),
                ("share_contact_details", models.BooleanField(default=False)),
                ("account_status", models.CharField(max_length=20)),
                ("account_status_date", models.DateField(null=True)),
                ("password_disposition", models.CharField(max_length=20, null=True)),
                (
                    "account_status_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="data_migration.user",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Usage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("start_date", models.DateField()),
                ("end_date", models.DateField(null=True)),
                ("maximum_allocation", models.IntegerField(null=True)),
                (
                    "application_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="data_migration.importapplicationtype",
                    ),
                ),
                (
                    "commodity_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="data_migration.commoditygroup",
                    ),
                ),
                (
                    "country",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="data_migration.country",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Importer",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("type", models.CharField(max_length=20)),
                ("name", models.TextField(default="")),
                ("registered_number", models.CharField(max_length=15, null=True)),
                ("eori_number", models.CharField(max_length=20, null=True)),
                ("eori_number_ni", models.CharField(max_length=20, null=True)),
                ("region_origin", models.CharField(max_length=1, null=True)),
                ("comments", models.TextField(null=True)),
                (
                    "main_importer",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="data_migration.importer",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="data_migration.user",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ImportApplicationLicence",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("status", models.TextField(default="DR", max_length=2)),
                ("issue_paper_licence_only", models.BooleanField(null=True)),
                ("licence_start_date", models.DateField(null=True)),
                ("licence_end_date", models.DateField(null=True)),
                ("case_completion_date", models.DateField(null=True)),
                ("created_datetime", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "import_application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="licences",
                        to="data_migration.importapplication",
                        to_field="imad_id",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="importapplication",
            name="acknowledged_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="data_migration.user",
            ),
        ),
        migrations.AddField(
            model_name="importapplication",
            name="agent",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="data_migration.importer",
            ),
        ),
        migrations.AddField(
            model_name="importapplication",
            name="agent_office",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="data_migration.office",
            ),
        ),
        migrations.AddField(
            model_name="importapplication",
            name="application_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="data_migration.importapplicationtype",
            ),
        ),
        migrations.AddField(
            model_name="importapplication",
            name="case_owner",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="data_migration.user",
            ),
        ),
        migrations.AddField(
            model_name="importapplication",
            name="commodity_group",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="data_migration.commoditygroup",
            ),
        ),
        migrations.AddField(
            model_name="importapplication",
            name="consignment_country",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="data_migration.country",
            ),
        ),
        migrations.AddField(
            model_name="importapplication",
            name="contact",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="data_migration.user",
            ),
        ),
        migrations.AddField(
            model_name="importapplication",
            name="created_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="data_migration.user",
            ),
        ),
        migrations.AddField(
            model_name="importapplication",
            name="ima",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT,
                to="data_migration.process",
                to_field="ima_id",
            ),
        ),
        migrations.AddField(
            model_name="importapplication",
            name="imi_submitted_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="data_migration.user",
            ),
        ),
        migrations.AddField(
            model_name="importapplication",
            name="importer",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="data_migration.importer",
            ),
        ),
        migrations.AddField(
            model_name="importapplication",
            name="importer_office",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="data_migration.office",
            ),
        ),
        migrations.AddField(
            model_name="importapplication",
            name="last_updated_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="data_migration.user",
            ),
        ),
        migrations.AddField(
            model_name="importapplication",
            name="origin_country",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="data_migration.country",
            ),
        ),
        migrations.AddField(
            model_name="importapplication",
            name="submitted_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="data_migration.user",
            ),
        ),
        migrations.CreateModel(
            name="CountryTranslation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("translation", models.CharField(max_length=150)),
                (
                    "country",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="data_migration.country"
                    ),
                ),
                (
                    "translation_set",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="data_migration.countrytranslationset",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CountryGroupCountry",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "country",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="data_migration.country"
                    ),
                ),
                (
                    "countrygroup",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="data_migration.countrygroup",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CommodityGroupCommodity",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "commodity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="data_migration.commodity"
                    ),
                ),
                (
                    "commoditygroup",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="data_migration.commoditygroup",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="commoditygroup",
            name="commodity_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="data_migration.commoditytype",
                to_field="type_code",
            ),
        ),
        migrations.AddField(
            model_name="commoditygroup",
            name="unit",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="data_migration.unit",
                to_field="unit_type",
            ),
        ),
        migrations.AddField(
            model_name="commodity",
            name="commodity_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="data_migration.commoditytype",
                to_field="type_code",
            ),
        ),
    ]
