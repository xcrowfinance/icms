# Generated by Django 3.1.8 on 2021-05-25 10:16

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0064_silgoodssections"),
    ]

    operations = [
        migrations.CreateModel(
            name="OutwardProcessingTradeFile",
            fields=[
                (
                    "file_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="web.file",
                    ),
                ),
                (
                    "file_type",
                    models.CharField(
                        choices=[
                            ("supporting_document", "Supporting Documents"),
                            ("fq_employment_decreased", "Statistics"),
                            ("fq_prior_authorisation", "Copy of Prior Authorisation"),
                            ("fq_past_beneficiary", "Justification"),
                            ("fq_new_application", "Justification"),
                            ("fq_further_authorisation", "Evidence/Past Correspondence"),
                            ("fq_subcontract_production", "Declaration from Subcontractor"),
                        ],
                        max_length=32,
                    ),
                ),
            ],
            bases=("web.file",),
        ),
        migrations.CreateModel(
            name="OutwardProcessingTradeApplication",
            fields=[
                (
                    "importapplication_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="web.importapplication",
                    ),
                ),
                (
                    "customs_office_name",
                    models.CharField(
                        max_length=100,
                        null=True,
                        verbose_name="Requested customs supervising office name",
                    ),
                ),
                (
                    "customs_office_address",
                    models.TextField(
                        max_length=4000,
                        null=True,
                        verbose_name="Requested customs supervising office address",
                    ),
                ),
                (
                    "rate_of_yield",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=9,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(limit_value=0.0)],
                        verbose_name="Rate of yield (kg per garment)",
                    ),
                ),
                (
                    "rate_of_yield_calc_method",
                    models.TextField(
                        blank=True,
                        max_length=4000,
                        null=True,
                        verbose_name="Rate of yield calculation method",
                    ),
                ),
                (
                    "last_export_day",
                    models.DateField(
                        help_text="Requested last day of authorised exportation.",
                        null=True,
                        verbose_name="Last Export Day",
                    ),
                ),
                (
                    "reimport_period",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=9,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(limit_value=0.0)],
                        verbose_name="Period for re-importation (months)",
                    ),
                ),
                (
                    "nature_process_ops",
                    models.TextField(
                        max_length=4000, null=True, verbose_name="Nature of processing operations"
                    ),
                ),
                (
                    "suggested_id",
                    models.TextField(
                        help_text="Enter the suggested means of identification of re-imported compensating products.",
                        max_length=4000,
                        null=True,
                        verbose_name="Suggested means of identification",
                    ),
                ),
                (
                    "cp_category",
                    models.CharField(
                        choices=[
                            ("4", "4"),
                            ("5", "5"),
                            ("6", "6"),
                            ("7", "7"),
                            ("8", "8"),
                            ("15", "15"),
                            ("21", "21"),
                            ("24", "24"),
                            ("26", "26"),
                            ("27", "27"),
                            ("29", "29"),
                            ("73", "73"),
                        ],
                        help_text="The category defines what commodities you are applying to import.",
                        max_length=2,
                        null=True,
                        verbose_name="Category",
                    ),
                ),
                (
                    "cp_category_licence_description",
                    models.CharField(
                        help_text="By default, this is the category description. You may need to alter the description to a shorter form in order for it to display correctly on the licence.",
                        max_length=4000,
                        null=True,
                        verbose_name="Category Description",
                    ),
                ),
                (
                    "cp_total_quantity",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Please note that maximum allocations apply. Please check the guidance to ensure that you do not apply for more than is allowable.",
                        max_digits=9,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(limit_value=0.0)],
                        verbose_name="Total Quantity",
                    ),
                ),
                (
                    "cp_total_value",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Value of processing of the fabric/yarn",
                        max_digits=9,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(limit_value=0.0)],
                        verbose_name="Total Value (Euro)",
                    ),
                ),
                (
                    "teg_total_quantity",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=9,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(limit_value=0.0)],
                        verbose_name="Total Quantity",
                    ),
                ),
                (
                    "teg_total_value",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=9,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(limit_value=0.0)],
                        verbose_name="Total Value (Euro)",
                    ),
                ),
                (
                    "teg_goods_description",
                    models.CharField(max_length=4096, null=True, verbose_name="Goods Description"),
                ),
                (
                    "fq_similar_to_own_factory",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No"), ("n/a", "N/A")],
                        help_text="This question only needs to be completed once per year. If you have already completed this question on a previous application this year, you may select 'N/A'.",
                        max_length=3,
                        null=True,
                        verbose_name="Do you manufacture goods which are similar to and at the same stage of processing in your own factory within the EU as the products to be re-imported? (Article 2 (2) (a) of Regulation (EC) No. 3036/94)",
                    ),
                ),
                (
                    "fq_manufacturing_within_eu",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No"), ("n/a", "N/A")],
                        help_text="This question only needs to be completed once per year. If you have already completed this question on a previous application this year, you may select 'N/A'.",
                        max_length=3,
                        null=True,
                        verbose_name="Are the main manufacturing processes of the similar goods performed in your own factory within the EU (i.e. sewing and assembly or knitting in the case of fully-fashioned garments obtained from yarn)? (Article 2 (2) (a) of Regulation (EC) No. 3036/94)",
                    ),
                ),
                (
                    "fq_maintained_in_eu",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No"), ("n/a", "N/A")],
                        help_text="This question only needs to be completed once per year. If you have already completed this question on a previous application this year, you may select 'N/A'.",
                        max_length=3,
                        null=True,
                        verbose_name="Have you maintained your textile manufacturing activity in the EU with respect to the nature of the products and their quantities? (Article 3 (3) of Regulation (EC) No. 3036/94)",
                    ),
                ),
                (
                    "fq_maintained_in_eu_reasons",
                    models.CharField(
                        blank=True,
                        max_length=4000,
                        null=True,
                        verbose_name="If not, please indicate reasons for the above or make reference to past correspondence.",
                    ),
                ),
                (
                    "fq_employment_decreased",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No"), ("n/a", "N/A")],
                        help_text="This question only needs to be completed once per year. If you have already completed this question on a previous application this year, you may select 'N/A'.",
                        max_length=3,
                        null=True,
                        verbose_name="Has your level of employment decreased? (Article 5 (4) of Regulation (EC) No. 3036/94)",
                    ),
                ),
                (
                    "fq_employment_decreased_reasons",
                    models.CharField(
                        blank=True,
                        max_length=4000,
                        null=True,
                        verbose_name="If so, please indicate reasons and attach statistics below if necessary, or make reference to past correspondence.",
                    ),
                ),
                (
                    "fq_prior_authorisation",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No")],
                        max_length=3,
                        null=True,
                        verbose_name="Have you applied for a prior authorisation in another Member State for the same quota period? (Article 3(4) or (5) of Regulation (EC) No. 3036/94)",
                    ),
                ),
                (
                    "fq_prior_authorisation_reasons",
                    models.CharField(
                        blank=True,
                        max_length=4000,
                        null=True,
                        verbose_name="If so, please attach a copy of your authorisation below, or make reference to past correspondence.",
                    ),
                ),
                (
                    "fq_past_beneficiary",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No")],
                        max_length=3,
                        null=True,
                        verbose_name="Are you applying as a past beneficiary with regard to the category and country concerned? (Article 3(4) of Regulation (EC) No. 3036/94)",
                    ),
                ),
                (
                    "fq_past_beneficiary_reasons",
                    models.CharField(
                        blank=True,
                        max_length=4000,
                        null=True,
                        verbose_name="If so, please attach justification below, or make reference to past correspondence.",
                    ),
                ),
                (
                    "fq_new_application",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No")],
                        max_length=3,
                        null=True,
                        verbose_name="Is this a new application with regard to the category and country concerned? (Article 3(5) (2) and (3) of Regulation (EC) No. 3036/94)",
                    ),
                ),
                (
                    "fq_new_application_reasons",
                    models.CharField(
                        blank=True,
                        max_length=4000,
                        null=True,
                        verbose_name="If so, please make reference to past correspondence, or attach justification below, that the value of the third country processing will not exceed 50% of the value of your Community production in the previous year.",
                    ),
                ),
                (
                    "fq_further_authorisation",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No")],
                        max_length=3,
                        null=True,
                        verbose_name="Are you applying for a further authorisation with regard to the category and country concerned? (Article 3(5) (4) of Regulation (EC) No. 3036/94)",
                    ),
                ),
                (
                    "fq_further_authorisation_reasons",
                    models.CharField(
                        blank=True,
                        max_length=4000,
                        null=True,
                        verbose_name="If so, please attach evidence below, or make reference to past correspondence, that 50% of your previous authorisation has been re-imported or that 80% has been exported.",
                    ),
                ),
                (
                    "fq_subcontract_production",
                    models.CharField(
                        choices=[("yes", "Yes"), ("no", "No"), ("n/a", "N/A")],
                        help_text="This question only needs to be completed once per year. If you have already completed this question on a previous application this year, you may select 'N/A'.",
                        max_length=3,
                        null=True,
                        verbose_name="Does the value of your Community production in the previous year include subcontract production? (If so and you have not yet given this information, please attach declarations from subcontractors that they will not apply for the same quantities) (Article 2(2)(a) of Regulation (EC) No. 3036/94)",
                    ),
                ),
                (
                    "cp_commodities",
                    models.ManyToManyField(
                        help_text="It is the responsibility of the applicant to ensure that the commodity code in this box is correct. If you are unsure of the correct commodity code, consult the HM Revenue and Customs Integrated Tariff Book, Volume 2, which is available from the Stationery Office. If you are still in doubt, contact the Classification Advisory Service on (01702) 366077.",
                        related_name="_outwardprocessingtradeapplication_cp_commodities_+",
                        to="web.Commodity",
                        verbose_name="Commodity Code",
                    ),
                ),
                (
                    "cp_origin_country",
                    models.ForeignKey(
                        help_text="Select the country that the compensating products originate from.",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="web.country",
                        verbose_name="Country Of Origin",
                    ),
                ),
                (
                    "cp_processing_country",
                    models.ForeignKey(
                        help_text="Select the country that the compensating products were processed in.",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="web.country",
                        verbose_name="Country Of Processing",
                    ),
                ),
                (
                    "documents",
                    models.ManyToManyField(
                        related_name="_outwardprocessingtradeapplication_documents_+",
                        to="web.OutwardProcessingTradeFile",
                    ),
                ),
                (
                    "teg_commodities",
                    models.ManyToManyField(
                        help_text="It is the responsibility of the applicant to ensure that the commodity code in this box is correct. If you are unsure of the correct commodity code, consult the HM Revenue and Customs Integrated Tariff Book, Volume 2, which is available from the Stationery Office. If you are still in doubt, contact the Classification Advisory Service on (01702) 366077.",
                        related_name="_outwardprocessingtradeapplication_teg_commodities_+",
                        to="web.Commodity",
                        verbose_name="Commodity Code",
                    ),
                ),
                (
                    "teg_origin_country",
                    models.ForeignKey(
                        help_text="Select the country, or group of countries (e.g. Any EU Country) that the temporary exported goods originate from.",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="web.country",
                        verbose_name="Country Of Origin",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("web.importapplication",),
        ),
    ]
