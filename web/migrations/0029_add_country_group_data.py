# Generated by Django 3.1.5 on 2021-02-18 14:42
import textwrap

from django.db import migrations


def add_countries_to_group(group, countries, apps):
    Country = apps.get_model("web", "Country")
    for country_name in countries:
        country = Country.objects.get(name=country_name)
        group.countries.add(country)


def load_country_group_data_iron_and_steel(apps, schema_editor):
    CountryGroup = apps.get_model("web", "CountryGroup")
    group = CountryGroup.objects.create(name="Iron and Steel (Quota) COOs")
    countries = ["Kazakhstan"]
    add_countries_to_group(group, countries, apps)
    group.save()


def load_country_group_data_opt_coos(apps, schema_editor):
    CountryGroup = apps.get_model("web", "CountryGroup")
    group = CountryGroup.objects.create(name="OPT COOs")
    countries = ["Belarus"]
    add_countries_to_group(group, countries, apps)
    group.save()


def load_country_group_data_opt_temp_export_coo(apps, schema_editor):
    CountryGroup = apps.get_model("web", "CountryGroup")
    group = CountryGroup.objects.create(name="OPT Temp Export COOs")
    countries = ["Any EU Country"]
    add_countries_to_group(group, countries, apps)
    group.save()


def load_country_group_data_fireams_ammunition_issuing_countries(apps, schema_editor):
    CountryGroup = apps.get_model("web", "CountryGroup")
    group = CountryGroup.objects.create(
        name="Firearms and Ammunition (Deactivated) Issuing Countries"
    )
    countries = [
        "Austria",
        "Belgium",
        "Bulgaria",
        "Croatia",
        "Cyprus",
        "Denmark",
        "Estonia",
        "Finland",
        "France",
        "Germany",
        "Greece",
        "Hungary",
        "Irish Republic",
        "Italy",
        "Latvia",
        "Lithuania",
        "Luxembourg",
        "Malta",
        "Netherlands",
        "Poland",
        "Portugal",
        "Romania",
        "Slovenia",
        "Spain",
        "Sweden",
        "the Czech Republic",
        "the Slovak Republic",
        "United Kingdom",
    ]
    add_countries_to_group(group, countries, apps)
    group.save()


def load_country_group_data_ceriticate_of_manufacture_countries(apps, schema_editor):
    CountryGroup = apps.get_model("web", "CountryGroup")
    group = CountryGroup.objects.create(name="Certificate of Manufacture Countries")
    countries = [
        "Afghanistan",
        "Albania",
        "Algeria",
        "Angola",
        "Argentina",
        "Armenia",
        "Australia",
        "Azerbaijan",
        "Bahamas",
        "Bahrain",
        "Bangladesh",
        "Barbados",
        "Belarus",
        "Benin",
        "Bermuda",
        "Bhutan",
        "Bolivia",
        "Bosnia and Herzegovina",
        "Botswana",
        "Brazil",
        "British Virgin Islands",
        "Brunei",
        "Burma",
        "Cambodia",
        "Canada",
        "Chile",
        "China",
        "Colombia",
        "Congo",
        "Congo (Dem. Republic)",
        "Costa Rica",
        "Cote d'Ivoire",
        "Cuba",
        "Dominica",
        "Dominican Republic",
        "Ecuador",
        "Egypt",
        "El Salvador",
        "Equatorial Guinea",
        "Ethiopia",
        "Falkland Islands",
        "Faroe Islands",
        "Gabon",
        "Gambia",
        "Georgia",
        "Ghana",
        "Gibraltar",
        "Greenland",
        "Guatemala",
        "Guernsey",
        "Guinea",
        "Haiti",
        "Honduras",
        "Hong Kong",
        "Iceland",
        "India",
        "Indonesia",
        "Iran",
        "Iraq",
        "Israel",
        "Jamaica",
        "Japan",
        "Jersey",
        "Jordan",
        "Kazakhstan",
        "Kenya",
        "Korea (North)",
        "Korea (South)",
        "Kosovo",
        "Kuwait",
        "Kyrgyzstan",
        "Laos",
        "Lebanon",
        "Libya",
        "Liechtenstein",
        "Macao",
        "Macedonia  Former Yugoslav Republic of",
        "Madagascar",
        "Malaysia",
        "Mauritania",
        "Mauritius",
        "Mexico",
        "Micronesia",
        "Moldova",
        "Mongolia",
        "Montenegro",
        "Morocco",
        "Mozambique",
        "Namibia",
        "Nauru",
        "Nepal",
        "New Zealand",
        "Nicaragua",
        "Nigeria",
        "Norway",
        "Occupied Palestinian Territories",
        "Oman",
        "Pakistan",
        "Panama",
        "Paraguay",
        "Peru",
        "Philippines",
        "Puerto Rico",
        "Qatar",
        "Russian Federation",
        "Saint Helena",
        "Saudi Arabia",
        "Serbia",
        "Singapore",
        "Soloman Islands",
        "Somalia",
        "South Africa",
        "Sri Lanka",
        "Swaziland",
        "Switzerland",
        "Syria",
        "Taiwan",
        "Tajikistan",
        "Tanzania",
        "Thailand",
        "the Channel Islands",
        "Trinidad & Tobago",
        "Tunisia",
        "Turkey",
        "Turkmenistan",
        "Ukraine",
        "United Arab Emirates",
        "Uruguay",
        "USA",
        "Uzbekistan",
        "Venezuela",
        "Vietnam",
        "Yemen",
        "Zimbabwe",
    ]
    add_countries_to_group(group, countries, apps)
    group.save()


def load_country_group_data_textile_coos(apps, schema_editor):
    CountryGroup = apps.get_model("web", "CountryGroup")
    group = CountryGroup.objects.create(name="Textile COOs")
    group.comments = "Belarus removed 03/07/17"
    countries = ["Korea (North)"]
    add_countries_to_group(group, countries, apps)
    group.save()


def load_country_group_data_certificate_of_free_sale_countries(apps, schema_editor):
    CountryGroup = apps.get_model("web", "CountryGroup")
    group = CountryGroup.objects.create(name="Certificate of Free Sale Countries")
    group.comments = textwrap.dedent(
        """\
            Added Maldives 22/11/16
            Added Zambia 14/03/2017
            Added Aruba 10/05/2017
            Added Mali 21/09/2018
            Added Rwanda 27/09/18
            Added Uganda 26/02/19
            """
    )

    countries = [
        "Afghanistan",
        "Albania",
        "Algeria",
        "Angola",
        "Argentina",
        "Armenia",
        "Aruba",
        "Azerbaijan",
        "Bahamas",
        "Bahrain",
        "Bangladesh",
        "Barbados",
        "Belarus",
        "Belize",
        "Benin",
        "Bermuda",
        "Bhutan",
        "Bolivia",
        "Bosnia and Herzegovina",
        "Botswana",
        "Brazil",
        "British Virgin Islands",
        "Brunei",
        "Burma",
        "Cambodia",
        "Canada",
        "Chile",
        "China",
        "Colombia",
        "Congo",
        "Congo (Dem. Republic)",
        "Costa Rica",
        "Cote d'Ivoire",
        "Cuba",
        "Dominica",
        "Dominican Republic",
        "Ecuador",
        "Egypt",
        "El Salvador",
        "Equatorial Guinea",
        "Ethiopia",
        "Falkland Islands",
        "Faroe Islands",
        "Gabon",
        "Gambia",
        "Georgia",
        "Ghana",
        "Greenland",
        "Guatemala",
        "Guinea",
        "Guyana",
        "Haiti",
        "Honduras",
        "Hong Kong",
        "India",
        "Indonesia",
        "Iran",
        "Iraq",
        "Israel",
        "Jamaica",
        "Japan",
        "Jordan",
        "Kazakhstan",
        "Kenya",
        "Korea (North)",
        "Korea (South)",
        "Kosovo",
        "Kuwait",
        "Kyrgyzstan",
        "Laos",
        "Lebanon",
        "Liberia",
        "Libya",
        "Macao",
        "Macedonia  Former Yugoslav Republic of",
        "Madagascar",
        "Malaysia",
        "Maldives",
        "Mali",
        "Mauritania",
        "Mauritius",
        "Mexico",
        "Micronesia",
        "Moldova",
        "Mongolia",
        "Montenegro",
        "Morocco",
        "Mozambique",
        "Namibia",
        "Nauru",
        "Nepal",
        "Nicaragua",
        "Nigeria",
        "Occupied Palestinian Territories",
        "Oman",
        "Pakistan",
        "Panama",
        "Paraguay",
        "Peru",
        "Philippines",
        "Puerto Rico",
        "Qatar",
        "Russian Federation",
        "Rwanda",
        "Saint Helena",
        "Saudi Arabia",
        "Senegal",
        "Serbia",
        "Seychelles",
        "Singapore",
        "Soloman Islands",
        "Somalia",
        "South Africa",
        "Sri Lanka",
        "Sudan",
        "Suriname",
        "Swaziland",
        "Switzerland",
        "Syria",
        "Taiwan",
        "Tajikistan",
        "Tanzania",
        "Thailand",
        "Trinidad & Tobago",
        "Tunisia",
        "Turkey",
        "Turkmenistan",
        "Uganda",
        "Ukraine",
        "United Arab Emirates",
        "Uruguay",
        "USA",
        "Uzbekistan",
        "Venezuela",
        "Vietnam",
        "Yemen",
        "Zambia",
        "Zimbabwe",
    ]
    add_countries_to_group(group, countries, apps)
    group.save()


def load_country_group_data_certificate_of_free_sale_country_of_manufacture_countries(
    apps, schema_editor
):
    CountryGroup = apps.get_model("web", "CountryGroup")
    group = CountryGroup.objects.create(
        name="Certificate of Free Sale Country of Manufacture Countries"
    )
    countries = [
        "Afghanistan",
        "Albania",
        "Algeria",
        "Angola",
        "Argentina",
        "Armenia",
        "Aruba",
        "Australia",
        "Austria",
        "Azerbaijan",
        "Bahamas",
        "Bahrain",
        "Bangladesh",
        "Barbados",
        "Belarus",
        "Belgium",
        "Belize",
        "Benin",
        "Bermuda",
        "Bhutan",
        "Bolivia",
        "Bosnia and Herzegovina",
        "Botswana",
        "Brazil",
        "British Virgin Islands",
        "Brunei",
        "Bulgaria",
        "Burma",
        "Cambodia",
        "Canada",
        "Chile",
        "China",
        "Colombia",
        "Congo",
        "Congo (Dem. Republic)",
        "Costa Rica",
        "Cote d'Ivoire",
        "Croatia",
        "Cuba",
        "Cyprus",
        "Denmark",
        "Dominica",
        "Dominican Republic",
        "Ecuador",
        "Egypt",
        "El Salvador",
        "Equatorial Guinea",
        "Estonia",
        "Ethiopia",
        "European Union",
        "Falkland Islands",
        "Faroe Islands",
        "Finland",
        "France",
        "Gabon",
        "Gambia",
        "Georgia",
        "Germany",
        "Ghana",
        "Gibraltar",
        "Greece",
        "Greenland",
        "Guatemala",
        "Guernsey",
        "Guinea",
        "Guyana",
        "Haiti",
        "Honduras",
        "Hong Kong",
        "Hungary",
        "Iceland",
        "India",
        "Indonesia",
        "Iran",
        "Iraq",
        "Irish Republic",
        "Israel",
        "Italy",
        "Jamaica",
        "Japan",
        "Jersey",
        "Jordan",
        "Kazakhstan",
        "Kenya",
        "Korea (North)",
        "Korea (South)",
        "Kosovo",
        "Kuwait",
        "Kyrgyzstan",
        "Laos",
        "Latvia",
        "Lebanon",
        "Liberia",
        "Libya",
        "Liechtenstein",
        "Lithuania",
        "Luxembourg",
        "Macao",
        "Macedonia  Former Yugoslav Republic of",
        "Madagascar",
        "Malaysia",
        "Maldives",
        "Mali",
        "Malta",
        "Mauritania",
        "Mauritius",
        "Mexico",
        "Micronesia",
        "Moldova",
        "Mongolia",
        "Montenegro",
        "Morocco",
        "Mozambique",
        "Namibia",
        "Nauru",
        "Nepal",
        "Netherlands",
        "New Zealand",
        "Nicaragua",
        "Nigeria",
        "Norway",
        "Occupied Palestinian Territories",
        "Oman",
        "Pakistan",
        "Panama",
        "Papua New Guinea",
        "Paraguay",
        "Peru",
        "Philippines",
        "Poland",
        "Portugal",
        "Puerto Rico",
        "Qatar",
        "Romania",
        "Russian Federation",
        "Rwanda",
        "Saint Helena",
        "Saudi Arabia",
        "Senegal",
        "Serbia",
        "Seychelles",
        "Singapore",
        "Slovenia",
        "Soloman Islands",
        "Somalia",
        "South Africa",
        "Spain",
        "Sri Lanka",
        "Sudan",
        "Suriname",
        "Swaziland",
        "Sweden",
        "Switzerland",
        "Syria",
        "Taiwan",
        "Tajikistan",
        "Tanzania",
        "Thailand",
        "the Czech Republic",
        "the Slovak Republic",
        "Trinidad & Tobago",
        "Tunisia",
        "Turkey",
        "Turkmenistan",
        "Uganda",
        "Ukraine",
        "United Arab Emirates",
        "United Kingdom",
        "Uruguay",
        "USA",
        "Uzbekistan",
        "Venezuela",
        "Vietnam",
        "Yemen",
        "Zambia",
        "Zimbabwe",
    ]
    add_countries_to_group(group, countries, apps)
    group.save()


def load_country_group_data_firearms_and_ammunition_SIL_COCs(apps, schema_editor):
    CountryGroup = apps.get_model("web", "CountryGroup")
    group = CountryGroup.objects.create(name="Firearms and Ammunition (SIL) COCs")
    group.comments = textwrap.dedent(
        """\
        Removed 'any EU country' 29/08/19
        Potential for breach of sanctions - removed Any Country and Any non-EU Country. 14/12/15
        Sanctions - Removed Iran, North Korea, Libya and Syria.
        Removed UK.
        Removed Russian Federation. 01/08/14
        Added Bolivia, Costa Rica, El Salvador, Nicaragua, Occupied Palestinian Territories, Paraguay - 28/04/15"""
    )
    countries = [
        "Afghanistan",
        "Albania",
        "Algeria",
        "Angola",
        "Argentina",
        "Armenia",
        "Australia",
        "Austria",
        "Azerbaijan",
        "Bahamas",
        "Bahrain",
        "Bangladesh",
        "Barbados",
        "Belarus",
        "Belgium",
        "Bermuda",
        "Bhutan",
        "Bolivia",
        "Bosnia and Herzegovina",
        "Botswana",
        "Brazil",
        "British Virgin Islands",
        "Brunei",
        "Bulgaria",
        "Burma",
        "Cambodia",
        "Canada",
        "Chile",
        "China",
        "Colombia",
        "Congo",
        "Congo (Dem. Republic)",
        "Costa Rica",
        "Cote d'Ivoire",
        "Croatia",
        "Cuba",
        "Cyprus",
        "Denmark",
        "Dominica",
        "Dominican Republic",
        "Ecuador",
        "Egypt",
        "El Salvador",
        "Equatorial Guinea",
        "Estonia",
        "Ethiopia",
        "Falkland Islands",
        "Faroe Islands",
        "Finland",
        "France",
        "Gabon",
        "Gambia",
        "Georgia",
        "Germany",
        "Ghana",
        "Gibraltar",
        "Greece",
        "Greenland",
        "Guatemala",
        "Guernsey",
        "Guinea",
        "Haiti",
        "Honduras",
        "Hong Kong",
        "Hungary",
        "Iceland",
        "India",
        "Indonesia",
        "Iraq",
        "Irish Republic",
        "Israel",
        "Italy",
        "Jamaica",
        "Japan",
        "Jersey",
        "Jordan",
        "Kazakhstan",
        "Kenya",
        "Korea (South)",
        "Kosovo",
        "Kuwait",
        "Kyrgyzstan",
        "Laos",
        "Latvia",
        "Lebanon",
        "Liechtenstein",
        "Lithuania",
        "Luxembourg",
        "Macao",
        "Macedonia  Former Yugoslav Republic of",
        "Madagascar",
        "Malaysia",
        "Malta",
        "Mauritania",
        "Mauritius",
        "Mexico",
        "Micronesia",
        "Moldova",
        "Mongolia",
        "Montenegro",
        "Morocco",
        "Mozambique",
        "Namibia",
        "Nauru",
        "Nepal",
        "Netherlands",
        "New Zealand",
        "Nicaragua",
        "Nigeria",
        "Norway",
        "Occupied Palestinian Territories",
        "Oman",
        "Pakistan",
        "Panama",
        "Paraguay",
        "Peru",
        "Philippines",
        "Poland",
        "Portugal",
        "Puerto Rico",
        "Qatar",
        "Romania",
        "Saint Helena",
        "Saudi Arabia",
        "Serbia",
        "Singapore",
        "Slovenia",
        "Soloman Islands",
        "Somalia",
        "South Africa",
        "Spain",
        "Sri Lanka",
        "Swaziland",
        "Sweden",
        "Switzerland",
        "Taiwan",
        "Tajikistan",
        "Tanzania",
        "Thailand",
        "the Czech Republic",
        "the Slovak Republic",
        "Trinidad & Tobago",
        "Tunisia",
        "Turkey",
        "Turkmenistan",
        "Ukraine",
        "United Arab Emirates",
        "Uruguay",
        "USA",
        "Uzbekistan",
        "Venezuela",
        "Vietnam",
        "Yemen",
        "Zimbabwe",
    ]
    add_countries_to_group(group, countries, apps)
    group.save()


def load_country_group_data_firearms_and_ammunition_SIL_COOs(apps, schema_editor):
    CountryGroup = apps.get_model("web", "CountryGroup")
    group = CountryGroup.objects.create(name="Firearms and Ammunition (SIL) COOs")
    group.comments = textwrap.dedent(
        """\
        Removed 'any EU country' 29/08/19
        Potential for breach of sanctions - removed Any Country and Any non-EU Country. 15/12/15
        Sanctions - Removed Iran, North Korea, Libya and Syria.
        Removed Russian Federation 01/08/14.
        Added Bolivia, Costa Rica, El Salvador, Nicaragua, Occupied Palestinian Territories, Paraguay - 28/04/15
        """
    )
    countries = [
        "Afghanistan",
        "Albania",
        "Algeria",
        "Angola",
        "Argentina",
        "Armenia",
        "Australia",
        "Austria",
        "Azerbaijan",
        "Bahamas",
        "Bahrain",
        "Bangladesh",
        "Barbados",
        "Belarus",
        "Belgium",
        "Bermuda",
        "Bhutan",
        "Bolivia",
        "Bosnia and Herzegovina",
        "Botswana",
        "Brazil",
        "British Virgin Islands",
        "Brunei",
        "Bulgaria",
        "Burma",
        "Cambodia",
        "Canada",
        "Chile",
        "China",
        "Colombia",
        "Congo",
        "Congo (Dem. Republic)",
        "Costa Rica",
        "Cote d'Ivoire",
        "Croatia",
        "Cuba",
        "Cyprus",
        "Denmark",
        "Dominica",
        "Dominican Republic",
        "Ecuador",
        "Egypt",
        "El Salvador",
        "Equatorial Guinea",
        "Estonia",
        "Ethiopia",
        "Falkland Islands",
        "Faroe Islands",
        "Finland",
        "France",
        "Gabon",
        "Gambia",
        "Georgia",
        "Germany",
        "Ghana",
        "Gibraltar",
        "Greece",
        "Greenland",
        "Guatemala",
        "Guernsey",
        "Guinea",
        "Haiti",
        "Honduras",
        "Hong Kong",
        "Hungary",
        "Iceland",
        "India",
        "Indonesia",
        "Iraq",
        "Irish Republic",
        "Israel",
        "Italy",
        "Jamaica",
        "Japan",
        "Jersey",
        "Jordan",
        "Kazakhstan",
        "Kenya",
        "Korea (South)",
        "Kosovo",
        "Kuwait",
        "Kyrgyzstan",
        "Laos",
        "Latvia",
        "Lebanon",
        "Liechtenstein",
        "Lithuania",
        "Luxembourg",
        "Macao",
        "Macedonia  Former Yugoslav Republic of",
        "Madagascar",
        "Malaysia",
        "Malta",
        "Mauritania",
        "Mauritius",
        "Mexico",
        "Micronesia",
        "Moldova",
        "Mongolia",
        "Montenegro",
        "Morocco",
        "Mozambique",
        "Namibia",
        "Nauru",
        "Nepal",
        "Netherlands",
        "New Zealand",
        "Nicaragua",
        "Nigeria",
        "Norway",
        "Occupied Palestinian Territories",
        "Oman",
        "Pakistan",
        "Panama",
        "Paraguay",
        "Peru",
        "Philippines",
        "Poland",
        "Portugal",
        "Puerto Rico",
        "Qatar",
        "Romania",
        "Saint Helena",
        "Saudi Arabia",
        "Serbia",
        "Singapore",
        "Slovenia",
        "Soloman Islands",
        "Somalia",
        "South Africa",
        "Spain",
        "Sri Lanka",
        "Swaziland",
        "Sweden",
        "Switzerland",
        "Taiwan",
        "Tajikistan",
        "Tanzania",
        "Thailand",
        "the Czech Republic",
        "the Slovak Republic",
        "Trinidad & Tobago",
        "Tunisia",
        "Turkey",
        "Turkmenistan",
        "Ukraine",
        "United Arab Emirates",
        "United Kingdom",
        "Uruguay",
        "USA",
        "Uzbekistan",
        "Venezuela",
        "Vietnam",
        "Yemen",
        "Zimbabwe",
    ]
    add_countries_to_group(group, countries, apps)
    group.save()


def load_country_group_data_firearms_and_ammunition_OIL_COCs(apps, schema_editor):
    CountryGroup = apps.get_model("web", "CountryGroup")
    group = CountryGroup.objects.create(name="Firearms and Ammunition (OIL) COCs")
    countries = ["Any Country"]
    add_countries_to_group(group, countries, apps)
    group.save()


def load_country_group_data_wood_quota_COOs(apps, schema_editor):
    CountryGroup = apps.get_model("web", "CountryGroup")
    group = CountryGroup.objects.create(name="Wood (Quota) COOs")
    countries = ["Russian Federation"]
    add_countries_to_group(group, countries, apps)
    group.save()


def load_country_group_data_firearms_and_ammunition_oil_COOs(apps, schema_editor):
    CountryGroup = apps.get_model("web", "CountryGroup")
    group = CountryGroup.objects.create(name="Firearms and Ammunition (OIL) COOs")
    countries = ["Any Country"]
    add_countries_to_group(group, countries, apps)
    group.save()


def load_country_group_data_derogation_from_sanctions_COOs(apps, schema_editor):
    CountryGroup = apps.get_model("web", "CountryGroup")
    group = CountryGroup.objects.create(name="Derogation from Sanctions COOs")
    countries = ["Iran", "Russian Federation", "Somalia", "Syria"]
    add_countries_to_group(group, countries, apps)
    group.save()


def load_country_group_data_non_EU_single_countries(apps, schema_editor):
    CountryGroup = apps.get_model("web", "CountryGroup")
    group = CountryGroup.objects.create(name="Non EU Single Countries")
    countries = [
        "Afghanistan",
        "Albania",
        "Algeria",
        "Angola",
        "Argentina",
        "Armenia",
        "Australia",
        "Azerbaijan",
        "Bahamas",
        "Bahrain",
        "Bangladesh",
        "Barbados",
        "Belarus",
        "Bermuda",
        "Bhutan",
        "Bosnia and Herzegovina",
        "Botswana",
        "Brazil",
        "British Virgin Islands",
        "Brunei",
        "Burma",
        "Cambodia",
        "Canada",
        "Chile",
        "China",
        "Colombia",
        "Congo",
        "Congo (Dem. Republic)",
        "Cote d'Ivoire",
        "Cuba",
        "Dominica",
        "Dominican Republic",
        "Ecuador",
        "Egypt",
        "Equatorial Guinea",
        "Ethiopia",
        "Falkland Islands",
        "Faroe Islands",
        "Gabon",
        "Georgia",
        "Ghana",
        "Gibraltar",
        "Greenland",
        "Guatemala",
        "Guernsey",
        "Guinea",
        "Haiti",
        "Honduras",
        "Hong Kong",
        "Iceland",
        "India",
        "Indonesia",
        "Iran",
        "Iraq",
        "Israel",
        "Jamaica",
        "Japan",
        "Jersey",
        "Jordan",
        "Kazakhstan",
        "Kenya",
        "Korea (North)",
        "Korea (South)",
        "Kosovo",
        "Kuwait",
        "Kyrgyzstan",
        "Laos",
        "Lebanon",
        "Libya",
        "Liechtenstein",
        "Macao",
        "Macedonia  Former Yugoslav Republic of",
        "Madagascar",
        "Malaysia",
        "Mauritania",
        "Mauritius",
        "Mexico",
        "Micronesia",
        "Moldova",
        "Mongolia",
        "Montenegro",
        "Morocco",
        "Mozambique",
        "Namibia",
        "Nauru",
        "Nepal",
        "New Zealand",
        "Nigeria",
        "Norway",
        "Oman",
        "Pakistan",
        "Panama",
        "Papua New Guinea",
        "Peru",
        "Philippines",
        "Puerto Rico",
        "Qatar",
        "Russian Federation",
        "Saint Helena",
        "Saudi Arabia",
        "Serbia",
        "Singapore",
        "Soloman Islands",
        "Somalia",
        "South Africa",
        "Sri Lanka",
        "Swaziland",
        "Switzerland",
        "Syria",
        "Taiwan",
        "Tajikistan",
        "Tanzania",
        "Thailand",
        "the Channel Islands",
        "Trinidad & Tobago",
        "Tunisia",
        "Turkey",
        "Turkmenistan",
        "Ukraine",
        "United Arab Emirates",
        "Uruguay",
        "USA",
        "Uzbekistan",
        "Venezuela",
        "Vietnam",
        "Yemen",
        "Zimbabwe",
    ]
    add_countries_to_group(group, countries, apps)
    group.save()


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0028_alter_country_and_country_group"),
    ]

    operations = [
        migrations.RunPython(load_country_group_data_iron_and_steel),
        migrations.RunPython(load_country_group_data_opt_coos),
        migrations.RunPython(load_country_group_data_opt_temp_export_coo),
        migrations.RunPython(load_country_group_data_fireams_ammunition_issuing_countries),
        migrations.RunPython(load_country_group_data_ceriticate_of_manufacture_countries),
        migrations.RunPython(load_country_group_data_textile_coos),
        migrations.RunPython(load_country_group_data_certificate_of_free_sale_countries),
        migrations.RunPython(
            load_country_group_data_certificate_of_free_sale_country_of_manufacture_countries
        ),
        migrations.RunPython(load_country_group_data_firearms_and_ammunition_SIL_COCs),
        migrations.RunPython(load_country_group_data_firearms_and_ammunition_SIL_COOs),
        migrations.RunPython(load_country_group_data_firearms_and_ammunition_OIL_COCs),
        migrations.RunPython(load_country_group_data_wood_quota_COOs),
        migrations.RunPython(load_country_group_data_firearms_and_ammunition_oil_COOs),
        migrations.RunPython(load_country_group_data_derogation_from_sanctions_COOs),
        migrations.RunPython(load_country_group_data_non_EU_single_countries),
    ]