from data_migration.queries.utils import case_owner_ima, rp_wua

sps_application = f"""
WITH rp_wua AS ({rp_wua}), case_owner AS ({case_owner_ima})
SELECT
  ia.case_ref reference
  , 1 is_active
  , xiad.status
  , xiad.submitted_datetime submit_datetime
  , xiad.response_decision decision
  , xiad.refuse_reason
  , xiad.applicant_reference
  , ia.created_datetime create_datetime
  , ia.created_datetime created
  , xiad.variation_no
  , xiad.legacy_case_flag
  , xiad.chief_usage_status
  , xiad.variation_decision
  , xiad.variation_refuse_reason
  , xiad.licence_extended licence_extended_flag
  , CASE WHEN ir.licence_ref IS NULL THEN NULL ELSE 'ILD' || ir.licence_ref END licence_uref_id
  , xiad.last_updated_datetime last_update_datetime
  , xiad.submitted_by_wua_id submitted_by_id
  , xiad.created_by_wua_id created_by_id
  , lu.id last_updated_by_id
  , xiad.importer_id
  , CASE WHEN xiad.importer_id IS NULL THEN NULL ELSE 'i-' || xiad.importer_id || '-' || xiad.importer_office_id END importer_office_legacy_id
  , xiad.agent_id
  , CASE WHEN xiad.agent_id IS NULL THEN NULL ELSE 'i-' || xiad.agent_id || '-' || xiad.agent_office_id END agent_office_legacy_id
  , rp_wua.wua_id contact_id
  , xiad.coo_country_id origin_country_id
  , xiad.coc_country_id consignment_country_id
  , xiad.provided_to_imi_by_wua_id imi_submitted_by_id
  , xiad.date_provided_to_imi imi_submit_datetime
  , iat.id application_type_id
  , 'PriorSurveillanceApplication' process_type
  , case_owner.wua_id case_owner_id
  , ia_details.*
FROM
  impmgr.xview_ima_details xiad
INNER JOIN impmgr.import_applications ia ON ia.id = xiad.ima_id
INNER JOIN impmgr.import_application_types iat
  ON iat.ima_type = xiad.ima_type AND iat.ima_sub_type = xiad.ima_sub_type
INNER JOIN (
SELECT
  ad.ima_id, ad.id imad_id, x.*
FROM impmgr.import_application_details ad
CROSS JOIN XMLTABLE('/*'
  PASSING ad.xml_data
  COLUMNS
    customs_cleared_to_uk VARCHAR2(5) PATH '/IMA/APP_DETAILS/SPS_DETAILS/GOODS_CLEARED[not(fox-error)]/text()'
    , quantity VARCHAR2(100) PATH '/IMA/APP_DETAILS/SPS_DETAILS/COMMODITY_LIST/COMMODITY/QUANTITY[not(fox-error)]/text()'
    , value_gbp VARCHAR2(100) PATH '/IMA/APP_DETAILS/SPS_DETAILS/COMMODITY_LIST/COMMODITY/GBP_VALUE[not(fox-error)]/text()'
    , value_eur VARCHAR2(100) PATH '/IMA/APP_DETAILS/SPS_DETAILS/COMMODITY_LIST/COMMODITY/VALUE[not(fox-error)]/text()'
    , eur_conversion VARCHAR2(100) PATH '/IMA/APP_DETAILS/SPS_DETAILS/COMMODITY_LIST/COMMODITY/GBP_TO_EUR_CONVERSION_RATE[not(fox-error)]/text()'
    , commodity_id VARCHAR2(100) PATH '/IMA/APP_DETAILS/SPS_DETAILS/COMMODITY_LIST/COMMODITY/COMMODITY_ID[not(fox-error)]/text()'
    , file_type VARCHAR2(100) PATH '/IMA/APP_DETAILS/SPS_DETAILS/SPS_DOCUMENT_LIST/SPS_DOCUMENT/TYPE[not(fox-error)]/text()'
    , target_id VARCHAR2(100) PATH '/IMA/APP_DETAILS/SPS_DETAILS/SPS_DOCUMENT_LIST/SPS_DOCUMENT/TARGET_ID[not(fox-error)]/text()'
    , variations_xml XMLTYPE PATH '/IMA/APP_PROCESSING/VARIATIONS/VARIATION_REQUEST_LIST'
    , file_folder_id INTEGER PATH '/IMA/APP_METADATA/APP_DOCS_FF_ID/text()'
    , cover_letter_text XMLTYPE PATH '/IMA/APP_PROCESSING/RESPONSE/APPROVE/COVER_LETTER/*'
    , withdrawal_xml XMLTYPE PATH '/IMA/APP_PROCESSING/WITHDRAWAL/WITHDRAW_LIST'
  ) x
  WHERE status_control = 'C'
) ia_details ON ia_details.ima_id = xiad.ima_id
LEFT JOIN impmgr.ima_responses ir ON ir.ima_id = xiad.ima_id AND ir.licence_ref IS NOT NULL
LEFT JOIN decmgr.resource_people_details rp ON rp.rp_id = xiad.contact_rp_id AND rp.status_control = 'C' AND rp.status <> 'DELETED'
LEFT JOIN securemgr.web_user_accounts lu ON lu.id = xiad.last_updated_by_wua_id
LEFT JOIN rp_wua ON rp_wua.resource_person_id = xiad.contact_rp_id
LEFT JOIN case_owner ON case_owner.ima_id = xiad.ima_id
WHERE
  xiad.ima_type = 'SPS'
  AND xiad.IMA_SUB_TYPE = 'SPS1'
  AND xiad.status_control = 'C'
  AND xiad.status <> 'DELETED'
  AND (
    (iat.status = 'ARCHIVED' AND xiad.submitted_datetime IS NOT NULL)
    OR (
      iat.status = 'CURRENT' AND (
        xiad.submitted_datetime IS NOT NULL OR xiad.last_updated_datetime > CURRENT_DATE - INTERVAL '14' DAY
      )
    )
  )
ORDER BY xiad.imad_id
"""
