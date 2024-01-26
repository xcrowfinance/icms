import_approval_request_xml = """
<REQUEST_APPROVAL>
  <IMPORTER_ID>3</IMPORTER_ID>
  <EXPORTER_ID />
  <STATUS>COMPLETED</STATUS>
  <CONTACT_WUA_ID/>
  <REQUEST_DATE>2022-11-14T14:55:14</REQUEST_DATE>
  <REQUEST_CREATED_BY_WUA_ID>2</REQUEST_CREATED_BY_WUA_ID>
  <REQUESTER_NAME>Mr Prod User</REQUESTER_NAME>
  <RESPONSE_DATE>2022-11-14T15:12:14</RESPONSE_DATE>
  <RESPONDED_BY_WUA_ID>2</RESPONDED_BY_WUA_ID>
  <RESPONDER_NAME>Mr Prod User</RESPONDER_NAME>
  <RESPONSE>APPROVE</RESPONSE>
  <RESPONSE_REASON>Test Reason</RESPONSE_REASON>
</REQUEST_APPROVAL>
""".strip()

export_approval_request_xml = """
<REQUEST_APPROVAL>
  <IMPORTER_ID></IMPORTER_ID>
  <EXPORTER_ID>3</EXPORTER_ID>
  <STATUS>COMPLETED</STATUS>
  <CONTACT_WUA_ID/>
  <REQUEST_DATE>2022-11-14T14:55:14</REQUEST_DATE>
  <REQUEST_CREATED_BY_WUA_ID>2</REQUEST_CREATED_BY_WUA_ID>
  <REQUESTER_NAME>Mr Prod User</REQUESTER_NAME>
  <RESPONSE_DATE>2022-11-14T15:12:14</RESPONSE_DATE>
  <RESPONDED_BY_WUA_ID>2</RESPONDED_BY_WUA_ID>
  <RESPONDER_NAME>Mr Prod User</RESPONDER_NAME>
  <RESPONSE>APPROVE</RESPONSE>
  <RESPONSE_REASON>Test Reason</RESPONSE_REASON>
</REQUEST_APPROVAL>
""".strip()


phone_number_xml = """
<TELEPHONE_NO_LIST>
  <TELEPHONE_NO>
    <TELEPHONE_HASH_CODE>12345678</TELEPHONE_HASH_CODE>
    <TYPE>H</TYPE>
    <COMMENT>My Home</COMMENT>
  </TELEPHONE_NO>
  <TELEPHONE_NO>
    <TELEPHONE_HASH_CODE>+212345678</TELEPHONE_HASH_CODE>
    <TYPE>M</TYPE>
    <COMMENT />
  </TELEPHONE_NO>
</TELEPHONE_NO_LIST>
""".strip()


personal_email_xml = """
<PERSONAL_EMAIL_LIST>
  <PERSONAL_EMAIL>
    <EMAIL_ADDRESS>test_a</EMAIL_ADDRESS>
    <PORTAL_NOTIFICATIONS>Primary</PORTAL_NOTIFICATIONS>
    <TYPE>H</TYPE>
    <COMMENT>A COMMENT</COMMENT>
  </PERSONAL_EMAIL>
  <PERSONAL_EMAIL>
    <EMAIL_ADDRESS>test_b</EMAIL_ADDRESS>
    <PORTAL_NOTIFICATIONS>Yes</PORTAL_NOTIFICATIONS>
    <TYPE>W</TYPE>
    <COMMENT />
  </PERSONAL_EMAIL>
  <PERSONAL_EMAIL>
    <EMAIL_ADDRESS>test_c</EMAIL_ADDRESS>
    <PORTAL_NOTIFICATIONS>No</PORTAL_NOTIFICATIONS>
    <TYPE>H</TYPE>
    <COMMENT />
  </PERSONAL_EMAIL>
</PERSONAL_EMAIL_LIST>
""".strip()


alternative_email_xml = """
<DISTRIBUTION_EMAIL_LIST>
  <DISTRIBUTION_EMAIL>
    <EMAIL_ADDRESS>test_d</EMAIL_ADDRESS>
    <PORTAL_NOTIFICATIONS>Yes</PORTAL_NOTIFICATIONS>
    <TYPE>H</TYPE>
    <COMMENT>A COMMENT</COMMENT>
  </DISTRIBUTION_EMAIL>
  <DISTRIBUTION_EMAIL>
    <EMAIL_ADDRESS>test_e</EMAIL_ADDRESS>
    <PORTAL_NOTIFICATIONS>No</PORTAL_NOTIFICATIONS>
    <TYPE>W</TYPE>
    <COMMENT />
  </DISTRIBUTION_EMAIL>
</DISTRIBUTION_EMAIL_LIST>
""".strip()


personal_email_excluded_xml = """
<PERSONAL_EMAIL_LIST>
  <PERSONAL_EMAIL>
    <EMAIL_ADDRESS>test_a_excluded</EMAIL_ADDRESS>
    <PORTAL_NOTIFICATIONS>Primary</PORTAL_NOTIFICATIONS>
    <TYPE>H</TYPE>
    <COMMENT>A COMMENT</COMMENT>
  </PERSONAL_EMAIL>
</PERSONAL_EMAIL_LIST>
""".strip()


phone_number_excluded_xml = """
<TELEPHONE_NO_LIST>
  <TELEPHONE_NO>
    <TELEPHONE_HASH_CODE>999</TELEPHONE_HASH_CODE>
    <TYPE>H</TYPE>
    <COMMENT>My Home</COMMENT>
  </TELEPHONE_NO>
</TELEPHONE_NO_LIST>
""".strip()
