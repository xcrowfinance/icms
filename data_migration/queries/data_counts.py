# Variations

# TODO ICMSLST-1905 check missing variation requests for specific application types
import_application_variation_count = """
SELECT count(*)
FROM impmgr.import_application_details ad
INNER JOIN impmgr.xview_ima_details xid ON ad.id = xid.imad_id
CROSS JOIN XMLTABLE('
for $g1 in /IMA/APP_PROCESSING/VARIATIONS/VARIATION_REQUEST_LIST/VARIATION_REQUEST | <null/>
where /IMA/APP_PROCESSING/VARIATIONS/VARIATION_REQUEST_LIST/VARIATION_REQUEST and $g1/REQUEST_DATE/text()
return
<root>
  <status>{$g1/STATUS/file-id/text()}</status>
</root>
'
PASSING ad.xml_data
COLUMNS
  status VARCHAR2(4000) PATH '/root/status/text()'
) x
WHERE ad.status_control = 'C'
AND ima_type = :IMA_TYPE
AND ima_sub_type = :IMA_SUB_TYPE
"""


# TODO ICMSLST-1905 check variaitons where open/body or open/opened_datetime is null
export_application_variation_count = """
SELECT count(*)
FROM impmgr.xview_certificate_app_details xcad
INNER JOIN impmgr.certificate_app_details cad ON cad.id = xcad.cad_id
CROSS JOIN XMLTABLE('
for $g1 in /CA/CASE/VARIATIONS/VARIATION_LIST/VARIATION | <null/>
where /CA/CASE/VARIATIONS/VARIATION_LIST/VARIATION and $g1/OPEN/BODY/text() and $g1/OPEN/OPENED_DATETIME/text()
return
<root>
  <status>{$g1/STATUS/text()}</status>
</root>
'
PASSING cad.xml_data
COLUMNS
  status VARCHAR2(4000) PATH '/root/status/text()'
) x
WHERE cad.status_control = 'C'
AND xcad.application_type = :CA_TYPE
"""