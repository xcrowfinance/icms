from collections.abc import Generator

from django.core.management.base import BaseCommand

from web.models import Country, OverseasRegion


def countries_data() -> Generator[tuple, None, None]:
    ST = Country.SOVEREIGN_TERRITORY
    SYS = Country.SYSTEM

    AFRICA = OverseasRegion.objects.get(name="Africa")
    ASIA = OverseasRegion.objects.get(name="Asia Pacific")
    CHINA = OverseasRegion.objects.get(name="China and Hong Kong")
    EASTERN_EUROPE = OverseasRegion.objects.get(name="Eastern Europe and Central Asia")
    EUROPE = OverseasRegion.objects.get(name="Europe")
    LATIN_AMERICA = OverseasRegion.objects.get(name="Latin America and Caribbean")
    MIDDLE_EAST = OverseasRegion.objects.get(name="Middle East, Afghanistan and Pakistan")
    AMERICA = OverseasRegion.objects.get(name="North America")
    SOUTH_ASIA = OverseasRegion.objects.get(name="South Asia")
    ANTARCTICA = OverseasRegion.objects.get(name="Antarctica")

    yield from [
        (1, "Afghanistan", "AF", ST, "660", True, MIDDLE_EAST),
        (2, "Albania", "AL", ST, "70", True, EUROPE),
        (3, "Algeria", "DZ", ST, "208", True, AFRICA),
        (None, "American Samoa", "AS", ST, "830", False, ASIA),
        (None, "Andorra", "AD", ST, "043", False, EUROPE),
        (4, "Angola (including Cabinda)", "AO", ST, "330", True, AFRICA),
        (None, "Anguilla", "AI", ST, "446", False, LATIN_AMERICA),
        (
            None,
            "Antarctica (territory south of 60° south latitude, not AQ Norwegian NOK including the "
            "French Southern Territories (TF), Bouvet Krone Islands (BV), South Georgia and South Sandwich Islands (GS))",
            "AQ",
            ST,
            "891",
            False,
            ANTARCTICA,
        ),
        (None, "Antigua and Barbuda", "AG", ST, "459", False, LATIN_AMERICA),
        (7, "Argentina", "AR", ST, "528", True, LATIN_AMERICA),
        (8, "Armenia", "AM", ST, "77", True, EASTERN_EUROPE),
        (176, "Aruba", "AW", ST, "474", True, LATIN_AMERICA),
        (9, "Australia", "AU", ST, "800", True, ASIA),
        (10, "Austria (excluding Jungholz and Mittelberg)", "AT", ST, "38", True, EUROPE),
        (11, "Azerbaijan", "AZ", ST, "78", True, EASTERN_EUROPE),
        (12, "Bahamas", "BS", ST, "453", True, LATIN_AMERICA),
        (13, "Bahrain", "BH", ST, "640", True, MIDDLE_EAST),
        (14, "Bangladesh (formerly East Pakistan)", "BD", ST, "666", True, SOUTH_ASIA),
        (15, "Barbados", "BB", ST, "469", True, LATIN_AMERICA),
        (16, "Belarus", "BY", ST, "73", True, EASTERN_EUROPE),
        (17, "Belgium", "BE", ST, "17", True, EUROPE),
        (169, "Belize (formerly British Honduras)", "BZ", ST, "421", True, LATIN_AMERICA),
        (167, "Benin (formerly Dahomey)", "BJ", ST, "284", True, AFRICA),
        (18, "Bermuda", "BM", ST, "413", True, LATIN_AMERICA),
        (19, "Bhutan", "BT", ST, "675", True, SOUTH_ASIA),
        (160, "Bolivia", "BO", ST, "516", True, LATIN_AMERICA),
        (None, "Netherlands Antilles", "AN", ST, "478", False, LATIN_AMERICA),
        (20, "Bosnia and Herzegovina", "BA", ST, "93", True, EUROPE),
        (21, "Botswana", "BW", ST, "391", True, AFRICA),
        (None, "Bouvet Island", "BV", ST, "892", False, ANTARCTICA),
        (22, "Brazil", "BR", ST, "508", True, LATIN_AMERICA),
        (None, "British Antarctic Territory", "AQ", ST, "891", False, ANTARCTICA),
        (None, "British Indian Ocean Territory", "IO", ST, "357", False, AFRICA),
        (23, "British Virgin Islands", "VG", ST, "468", True, LATIN_AMERICA),
        (24, "Brunei", "BN", ST, "703", True, ASIA),
        (25, "Bulgaria", "BG", ST, "68", True, EUROPE),
        (184, "Burkina Faso (formerly Upper Volta)", "BF", ST, "236", True, AFRICA),
        (None, "Burundi", "BI", ST, "328", False, AFRICA),
        (27, "Cambodia (Kampuchea)", "KH", ST, "696", True, ASIA),
        (183, "Cameroon", "CM", ST, "302", True, AFRICA),
        (28, "Canada", "CA", ST, "404", True, AMERICA),
        (None, "Canary Islands", "IC", ST, "11", False, EUROPE),
        (None, "Cape Verde", "CV", ST, "247", False, AFRICA),
        (None, "Cayman Islands", "KY", ST, "463", False, LATIN_AMERICA),
        (None, "Central African Republic", "CF", ST, "306", False, AFRICA),
        (None, "Ceuta", "XC", ST, "021", False, AFRICA),
        (None, "Chad", "TD", ST, "244", False, AFRICA),
        (29, "Chile", "CL", ST, "512", True, LATIN_AMERICA),
        (30, CHINA, "CN", ST, "720", True, CHINA),
        (None, "Christmas Island (Indian Ocean)", "CX", ST, "834", False, ASIA),
        (None, "Cocos (Keeling) Islands", "CC", ST, "833", False, ASIA),
        (31, "Colombia", "CO", ST, "480", True, LATIN_AMERICA),
        (None, "Comoros (Great Comoro Anjouan and Moheli)", "KM", ST, "375", False, AFRICA),
        (33, "Congo", "CG", ST, "318", True, AFRICA),
        (34, "Congo (Democratic Republic of – formerly CD Zaire)", "CD", ST, "322", True, AFRICA),
        (None, "Continental Shelf (NW European) - Belgian Sector", "ZB", SYS, "", False, EUROPE),
        (None, "Continental Shelf (NW European) - Cyprus Sector", "ZJ", SYS, "", False, EUROPE),
        (None, "Continental Shelf (NW European) - Danish Sector", "ZD", SYS, "", False, EUROPE),
        (None, "Continental Shelf (NW European) - Finland Sector", "ZK", SYS, "", False, EUROPE),
        (None, "Continental Shelf (NW European) - French Sector", "ZF", SYS, "", False, EUROPE),
        (None, "Continental Shelf (NW European) - German Sector", "ZG", SYS, "", False, EUROPE),
        (None, "Continental Shelf (NW European) - Greece Sector", "ZC", SYS, "", False, EUROPE),
        (None, "Continental Shelf (NW European) - Irish Sector", "ZE", SYS, "", False, EUROPE),
        (None, "Continental Shelf (NW European) - Italy Sector", "ZL", SYS, "", False, EUROPE),
        (
            None,
            "Continental Shelf (NW European) - Netherlands Sector",
            "ZH",
            SYS,
            "",
            False,
            EUROPE,
        ),
        (None, "Continental Shelf (NW European) - Norwegian Sector", "ZN", SYS, "", False, EUROPE),
        (None, "Continental Shelf (NW European) - Sweden Sector", "ZS", SYS, "", False, EUROPE),
        (
            181,
            "Continental Shelf (NW European) - United Kingdom Sector",
            "ZU",
            SYS,
            "999",
            True,
            EUROPE,
        ),
        (None, "Cook Islands", "CK", ST, "837", False, ASIA),
        (162, "Costa Rica", "CR", ST, "436", True, LATIN_AMERICA),
        (36, "Croatia", "HR", ST, "92", True, EUROPE),
        (37, "Cuba", "CU", ST, "448", True, LATIN_AMERICA),
        (None, "Curacao", "CW", ST, "475", False, LATIN_AMERICA),
        (38, "Cyprus", "CY", ST, "600", True, EUROPE),
        (156, "Czech Republic", "CZ", ST, "61", True, EUROPE),
        (39, "Denmark", "DK", ST, "8", True, EUROPE),
        (None, "Djibouti", "DJ", ST, "338", False, AFRICA),
        (40, "Dominica", "DM", ST, "460", True, LATIN_AMERICA),
        (41, "Dominican Republic", "DO", ST, "456", True, LATIN_AMERICA),
        (None, "East Timor", "TL", ST, "626", False, ASIA),
        (42, "Ecuador (including Galapagos Islands)", "EC", ST, "500", True, LATIN_AMERICA),
        (43, "Egypt", "EG", ST, "220", True, AFRICA),
        (163, "El Salvador", "SV", ST, "428", True, LATIN_AMERICA),
        (
            44,
            "Equatorial Guinea (comprising Fernando Po and adjacent islets, Annobon, Corisco and the Elobey Islands "
            "(with adjacent islets) and Rio Muni)",
            "GQ",
            ST,
            "310",
            True,
            AFRICA,
        ),
        (None, "Eritrea", "ER", ST, "336", False, AFRICA),
        (45, "Estonia", "EE", ST, "53", True, EUROPE),
        (46, "Ethiopia", "ET", ST, "334", True, AFRICA),
        (47, "Falkland Islands", "FK", ST, "529", True, LATIN_AMERICA),
        (48, "Faroe Islands", "FO", ST, "41", True, EUROPE),
        (None, "Fiji", "FJ", ST, "815", False, ASIA),
        (49, "Finland (including Aland Islands)", "FI", ST, "32", True, EUROPE),
        (50, "France (including Monaco)", "FR", ST, "1", True, EUROPE),
        (None, "French Antarctic Territory", "AQ", ST, "891", False, ANTARCTICA),
        (None, "French Guiana", "GF", ST, "1", False, LATIN_AMERICA),
        (None, "French Polynesia", "PF", ST, "822", False, ASIA),
        (None, "French Southern Territory", "TF", ST, "894", False, ANTARCTICA),
        (51, "Gabon", "GA", ST, "314", True, AFRICA),
        (159, "Gambia", "GM", ST, "252", True, AFRICA),
        (52, "Georgia", "GE", ST, "76", True, EASTERN_EUROPE),
        (
            53,
            "Germany (including the island of Heligoland: excluding the territory of Busingen)",
            "DE",
            ST,
            "4",
            True,
            EUROPE,
        ),
        (54, "Ghana", "GH", ST, "276", True, AFRICA),
        (55, "Gibraltar", "GI", ST, "44", True, EUROPE),
        (56, "Greece", "GR", ST, "9", True, EUROPE),
        (57, "Greenland", "GL", ST, "406", True, EUROPE),
        (None, "Grenada (including Southern Grenadines)", "GD", ST, "473", False, LATIN_AMERICA),
        (None, "Guadeloupe", "GP", ST, "1", False, LATIN_AMERICA),
        (None, "Guam", "GU", ST, "813", False, ASIA),
        (58, "Guatemala", "GT", ST, "416", True, LATIN_AMERICA),
        (59, "Guernsey", "GG", ST, "6", True, EUROPE),
        (60, "Guinea", "GN", ST, "260", True, AFRICA),
        (None, "Guinea-Bissau (formerly Portuguese Guinea)", "GW", ST, "257", False, AFRICA),
        (170, "Guyana", "GY", ST, "488", True, LATIN_AMERICA),
        (61, "Haiti", "HT", ST, "452", True, LATIN_AMERICA),
        (None, "Hawaii", "US", ST, "452", False, AMERICA),
        (None, "Heard and McDonald Islands", "HM", ST, "835", False, ASIA),
        (62, "Honduras (including Swan Islands)", "HN", ST, "424", True, LATIN_AMERICA),
        (63, "Hong Kong", "HK", ST, "740", True, CHINA),
        (64, "Hungary", "HU", ST, "64", True, EUROPE),
        (65, "Iceland", "IS", ST, "24", True, EUROPE),
        (66, "India", "IN", ST, "664", True, SOUTH_ASIA),
        (67, "Indonesia", "ID", ST, "700", True, ASIA),
        (68, "Iran", "IR", ST, "616", True, MIDDLE_EAST),
        (69, "Iraq", "IQ", ST, "612", True, MIDDLE_EAST),
        (70, "Irish Republic", "IE", ST, "7", True, EUROPE),
        (71, "Israel", "IL", ST, "624", True, EUROPE),
        (
            72,
            "Italy (including Livigno; excluding the Municipality of Campione d’Italia)",
            "IT",
            ST,
            "5",
            True,
            EUROPE,
        ),
        (35, "Ivory Coast (Cote d’Ivoire)", "CI", ST, "272", True, AFRICA),
        (73, "Jamaica", "JM", ST, "464", True, LATIN_AMERICA),
        (74, "Japan", "JP", ST, "732", True, ASIA),
        (75, "Jersey", "JE", ST, "6", True, EUROPE),
        (76, "Jordan", "JO", ST, "628", True, MIDDLE_EAST),
        (77, "Kazakhstan", "KZ", ST, "79", True, EASTERN_EUROPE),
        (78, "Kenya", "KE", ST, "346", True, AFRICA),
        (None, "Kiribati", "KI", ST, "812", False, ASIA),
        (79, "Korea, North", "KP", ST, "724", True, ASIA),
        (80, "Korea, South", "KR", ST, "728", True, ASIA),
        (81, "Kosovo", "XK", ST, "95", True, EUROPE),
        (82, "Kuwait", "KW", ST, "636", True, MIDDLE_EAST),
        (83, "Kyrgyzstan", "KG", ST, "83", True, EASTERN_EUROPE),
        (84, "Lao People’s Democratic Republic", "LA", ST, "684", True, ASIA),
        (85, "Latvia", "LV", ST, "54", True, EUROPE),
        (86, "Lebanon", "LB", ST, "604", True, MIDDLE_EAST),
        (None, "Lesotho", "LS", ST, "395", False, AFRICA),
        (173, "Liberia", "LR", ST, "268", True, AFRICA),
        (87, "Libya", "LY", ST, "216", True, AFRICA),
        (88, "Liechtenstein", "LI", ST, "37", True, EUROPE),
        (89, "Lithuania", "LT", ST, "55", True, EUROPE),
        (90, "Luxembourg", "LU", ST, "18", True, EUROPE),
        (91, "Macao", "MO", ST, "743", True, CHINA),
        (92, "Macedonia (F.Y.R.)", "MK", ST, "96", True, EUROPE),
        (93, "Madagascar (Malgasy Republic)", "MG", ST, "370", True, AFRICA),
        (None, "Malawi", "MW", ST, "386", False, AFRICA),
        (
            94,
            "Malaysia (Peninsular Malaysia and Eastern Malaysia (Labuanm Sabah and Sarawak))",
            "MY",
            ST,
            "701",
            True,
            ASIA,
        ),
        (174, "Maldives", "MV", ST, "667", True, SOUTH_ASIA),
        (178, "Mali", "ML", ST, "232", True, AFRICA),
        (95, "Malta (including Gozo and Comino)", "MT", ST, "46", True, EUROPE),
        (None, "Marshall Islands", "MH", ST, "824", False, ASIA),
        (None, "Martinique", "MQ", ST, "1", False, LATIN_AMERICA),
        (96, "Mauritania", "MR", ST, "228", True, AFRICA),
        (97, "Mauritius", "MU", ST, "373", True, AFRICA),
        (None, "Mayotte (Grand Terre and Pamanzi)", "YT", ST, "377", False, AFRICA),
        (
            None,
            "Melilla (including Penon de Velez de la Gomera, Penon de Alhucemas and the Chafarinas Islands)",
            "XL",
            ST,
            "023",
            False,
            AFRICA,
        ),
        (98, "Mexico", "MX", ST, "412", True, LATIN_AMERICA),
        (99, "Micronesia (Federated States of)", "FM", ST, "823", True, ASIA),
        (100, "Moldova, Rep of", "MD", ST, "74", True, EASTERN_EUROPE),
        (182, "Monaco", "FR", ST, "001", True, EUROPE),
        (101, "Mongolia", "MN", ST, "716", True, EASTERN_EUROPE),
        (102, "Montenegro", "ME", ST, "97", True, EUROPE),
        (None, "Montserrat", "MS", ST, "470", False, LATIN_AMERICA),
        (103, "Morocco", "MA", ST, "204", True, AFRICA),
        (104, "Mozambique", "MZ", ST, "366", True, AFRICA),
        (26, "Myanmar (Burma)", "MM", ST, "676", True, ASIA),
        (105, "Namibia", "NA", ST, "389", True, AFRICA),
        (106, "Nauru", "NR", ST, "803", True, ASIA),
        (107, "Nepal", "NP", ST, "672", True, SOUTH_ASIA),
        (108, "Netherlands", "NL", ST, "3", True, EUROPE),
        (None, "New Caledonia and Dependencies", "NC", ST, "809", False, ASIA),
        (109, "New Zealand excluding Ross Dependency (Antarctica)", "NZ", ST, "804", True, ASIA),
        (164, "Nicaragua (including Corn Islands)", "NI", ST, "432", True, LATIN_AMERICA),
        (None, "Niger", "NE", ST, "240", False, AFRICA),
        (110, "Nigeria", "NG", ST, "288", True, AFRICA),
        (None, "Niue Island", "NU", ST, "838", False, ASIA),
        (None, "Norfolk Island", "NF", ST, "836", False, ASIA),
        (None, "Northern Mariana Islands", "MP", ST, "820", False, ASIA),
        (
            111,
            "Norway (including Svalbard Archipelago and Jan Mayen Island)",
            "NO",
            ST,
            "28",
            True,
            EUROPE,
        ),
        (
            165,
            "Occupied Palestinian Territory (West Bank (including East Jerusalem) and Gaza Strip)",
            "PS",
            ST,
            "625",
            True,
            MIDDLE_EAST,
        ),
        (112, "Oman (formerly Muscat and Oman)", "OM", ST, "649", True, MIDDLE_EAST),
        (113, "Pakistan", "PK", ST, "662", True, MIDDLE_EAST),
        (None, "Palau", "PW", ST, "825", False, ASIA),
        (114, "Panama (including the former Canal Zone)", "PA", ST, "442", True, LATIN_AMERICA),
        (177, "Papua New Guinea", "PG", ST, "801", True, ASIA),
        (161, "Paraguay", "PY", ST, "520", True, LATIN_AMERICA),
        (115, "Peru", "PE", ST, "504", True, LATIN_AMERICA),
        (116, "Philippines", "PH", ST, "708", True, ASIA),
        (None, "Pitcairn Island", "PN", ST, "813", False, ASIA),
        (117, "Poland", "PL", ST, "60", True, EUROPE),
        (118, "Portugal (including Azores and Madeira)", "PT", ST, "10", True, EUROPE),
        (119, "Puerto Rico", "PR", ST, "400", True, AMERICA),
        (120, "Qatar", "QA", ST, "644", True, MIDDLE_EAST),
        (121, "Romania", "RO", ST, "66", True, EUROPE),
        (122, "Russia", "RU", ST, "75", True, EASTERN_EUROPE),
        (179, "Rwanda", "RW", ST, "324", True, AFRICA),
        (None, "Samoa (formerly Western Samoa)", "WS", ST, "819", False, ASIA),
        (None, "St Berthelemy", "GP", ST, "466", False, LATIN_AMERICA),
        (None, "Bonaire, Sint Eustatius and Saba", "BQ", ST, "477", False, LATIN_AMERICA),
        (None, "St Kitts and Nevis", "KN", ST, "449", False, LATIN_AMERICA),
        (
            123,
            "St Helena (including Ascension Island and Tristan da Cunha Islands)",
            "SH",
            ST,
            "329",
            True,
            AFRICA,
        ),
        (None, "St Lucia", "LC", ST, "465", False, LATIN_AMERICA),
        (None, "St Maarten (Dutch Part)", "SX", ST, "479", False, LATIN_AMERICA),
        (None, "St Pierre and Miquelon", "PM", ST, "408", False, AMERICA),
        (None, "St Vincent and the Grenadines", "VC", ST, "467", False, LATIN_AMERICA),
        (None, "San Marino", "SM", ST, "047", False, EUROPE),
        (None, "Sao Tome and Principe", ST, ST, "311", False, AFRICA),
        (124, "Saudi Arabia", "SA", ST, "632", True, MIDDLE_EAST),
        (171, "Senegal", "SN", ST, "248", True, AFRICA),
        (125, "Serbia", "XS", ST, "98", True, EUROPE),
        (172, "Seychelles", "SC", ST, "355", True, AFRICA),
        (None, "Sierra Leone", "SL", ST, "264", False, AFRICA),
        (126, "Singapore", "SG", ST, "706", True, ASIA),
        (157, "Slovakia", "SK", ST, "63", True, EUROPE),
        (127, "Slovenia", "SI", ST, "91", True, EUROPE),
        (128, "Solomon Islands", "SB", ST, "806", True, ASIA),
        (129, "Somalia", "SO", ST, "342", True, AFRICA),
        (130, "South Africa", "ZA", ST, "388", True, AFRICA),
        (None, "South Georgia and South Sandwich Islands", "GS", ST, "893", False, LATIN_AMERICA),
        (131, "Spain (including Balearic Islands)", "ES", ST, "11", True, EUROPE),
        (132, "Sri Lanka (formerly Ceylon)", "LK", ST, "669", True, SOUTH_ASIA),
        (166, "North Sudan", "SD", ST, "224", True, AFRICA),
        (None, "South Sudan", "SS", ST, "225", False, AFRICA),
        (168, "Suriname", "SR", ST, "492", True, LATIN_AMERICA),
        (133, "Swaziland (Ngwame)", "SZ", ST, "393", True, AFRICA),
        (134, "Sweden", "SE", ST, "30", True, EUROPE),
        (
            135,
            "Switzerland (including the German territory Busingen and the Italian Municipality of Campione d’Italia)",
            "CH",
            ST,
            "39",
            True,
            EUROPE,
        ),
        (136, "Syria", "SY", ST, "608", True, MIDDLE_EAST),
        (137, "Taiwan", "TW", ST, "736", True, CHINA),
        (138, "Tajikistan", "TJ", ST, "82", True, EASTERN_EUROPE),
        (139, "Tanzania (Tanganyika, Zanzibar, Pemba)", "TZ", ST, "352", True, AFRICA),
        (140, "Thailand", "TH", ST, "680", True, ASIA),
        (None, "Togo", "TG", ST, "280", False, AFRICA),
        (None, "Tokelau Islands", "TK", ST, "839", False, ASIA),
        (None, "Tonga", "TO", ST, "817", False, ASIA),
        (141, "Trinidad and Tobago", "TT", ST, "472", True, LATIN_AMERICA),
        (142, "Tunisia", "TN", ST, "212", True, AFRICA),
        (143, "Turkey", "TR", ST, "52", True, EASTERN_EUROPE),
        (144, "Turkmenistan", "TM", ST, "80", True, EASTERN_EUROPE),
        (None, "Turks and Caicos Islands", "TC", ST, "454", False, LATIN_AMERICA),
        (None, "Tuvalu", "TV", ST, "807", False, ASIA),
        (180, "Uganda", "UG", ST, "350", True, AFRICA),
        (146, "Ukraine", "UA", ST, "72", True, EASTERN_EUROPE),
        (
            147,
            "United Arab Emirates (Abu Dhabi, Ajman, Dubai, Fujaairah, Ras al Khaimah, Sharjah and Umm al Qaiwain)",
            "AE",
            ST,
            "647",
            True,
            MIDDLE_EAST,
        ),
        (148, "United Kingdom (Great Britain and Northern Ireland)", "GB", ST, "6", True, EUROPE),
        (
            None,
            "United States minor outlying islands (including Baker Island, Howland Island, Jarvis Island, Johnson Atoll,"
            " Kingman Reef, Midway Islands, Navassa Island, Palmyra Atoll and Wake Island)",
            "UM",
            ST,
            "832",
            False,
            AMERICA,
        ),
        (145, "United States of America (including Puerto Rico)", "US", ST, "400", True, AMERICA),
        (149, "Uruguay", "UY", ST, "524", True, LATIN_AMERICA),
        (150, "Uzbekistan", "UZ", ST, "81", True, EASTERN_EUROPE),
        (None, "Vanuatu", "VU", ST, "816", False, ASIA),
        (None, "Vatican City", "VA", ST, "045", False, EUROPE),
        (151, "Venezuela", "VE", ST, "484", True, LATIN_AMERICA),
        (152, "Vietnam", "VN", ST, "690", True, ASIA),
        (None, "Virgin Islands of USA", "VI", ST, "457", False, LATIN_AMERICA),
        (None, "Wallis and Futuna Islands", "WF", ST, "811", False, ASIA),
        (None, "Western Sahara", "EH", ST, "229", False, AFRICA),
        (153, "Yemen", "YE", ST, "653", True, MIDDLE_EAST),
        (175, "Zambia", "ZM", ST, "378", True, AFRICA),
        (154, "Zimbabwe", "ZW", ST, "382", True, AFRICA),
        (5, "Any Country", "G001", SYS, "958", True, None),
        (6, "Any Non EU Country", "G012", SYS, "n/a", True, None),
        (32, "Any EU Country", "G025", SYS, "959", True, None),
        (158, "European Union", "EUNI", SYS, "N/A", True, None),
    ]


def add_region_to_existing_countries(stdout) -> None:
    """
    For existing countries add the overseas region.
    pk is used as part of the select as country name is editable so could potentially change prior to go-live.
    Data Migration will always insert the countries in the same order.
    N.B. pk 155 missing (the Channel Islands) which has been deleted from V1
    """
    for (
        country_id,
        name,
        hmrc_code,
        _type,
        commission_code,
        is_active,
        region,
    ) in countries_data():
        if country_id:
            try:
                country = Country.objects.get(
                    pk=country_id,
                    is_active=is_active,
                    hmrc_code=hmrc_code,
                    commission_code=commission_code,
                )
                country.overseas_region = region
                country.save()
            except Country.DoesNotExist:
                stdout.write(f"WARNING: Unable to find country id: {country_id}, name {name}")


def add_inactive_countries() -> None:
    """Add all countries on uk-trade-tariff-country-and-currency-codes website that are not already (active) in the database."""
    for (
        country_id,
        name,
        hmrc_code,
        _type,
        commission_code,
        is_active,
        region,
    ) in countries_data():
        if not country_id and not is_active:
            Country.objects.get_or_create(
                name=name,
                defaults={
                    "is_active": is_active,
                    "hmrc_code": hmrc_code,
                    "commission_code": commission_code,
                    "overseas_region": region,
                    "type": _type,
                },
            )


class Command(BaseCommand):
    """
    Countries data including HMRC code sourced from:
    https://www.gov.uk/government/publications/uk-trade-tariff-country-and-currency-codes/uk-trade-tariff-country-and-currency-codes

    Regions data sourced from:
    https://data.trade.gov.uk/datasets/240d5034-6a83-451b-8307-5755672f881b#countries-territories-and-regions

    Commission code data sourced from:
    https://ec.europa.eu/eurostat/documents/3859598/5889816/KS-BM-05-002-EN.PDF.pdf/62e82e02-4632-438b-a284-e8fe75984b32
    https://ec.europa.eu/eurostat/documents/3859598/11361906/KS-GQ-20-010-EN-N.pdf/259cd250-1710-0a8a-f190-ff6eb39b39ed
    """

    help = """Add V2 reference data, Countries and Overseas Regions"""

    def handle(self, *args, **options) -> None:
        add_region_to_existing_countries(self.stdout)
        add_inactive_countries()
