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