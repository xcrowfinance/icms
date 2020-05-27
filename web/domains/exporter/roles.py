#!/usr/bin/env python
# -*- coding: utf-8 -*-
# NOQA: C0301

EXPORTER_ROLES = [{
    'name':
    'Exporter Contacts:Approve/Reject Agents and Exporters:{id}',
    'description':
    'Users in this role will be able to approve and reject access for agents and new exporter contacts.',
    'role_order':
    60,
    'permissions': [{
        'name':
        'Approve/Reject Agents and Exporters',
        'codename':
        'IMP_EXPORTER_CONTACTS:AGENT_APPROVER:{id}:MAILSHOT_RECIPIENT'
    }, {
        'name':
        'Approve/Reject Agents and Exporters',
        'codename':
        'IMP_EXPORTER_CONTACTS:AGENT_APPROVER:{id}:IMP_CERT_SEARCH_CASES_LHS'
    }, {
        'name':
        'Approve/Reject Agents and Exporters',
        'codename':
        'IMP_EXPORTER_CONTACTS:AGENT_APPROVER:{id}:IMP_CERT_AGENT_APPROVER'
    }]
}, {
    'name':
    'Exporter Contacts:Edit Applications:{id}',
    'description':
    'Users in this role will be able to create and edit new applications for the exporter.',
    'role_order':
    40,
    'permissions': [{
        'name':
        'Edit Applications',
        'codename':
        'IMP_EXPORTER_CONTACTS:EDIT_APPLICATION:{id}:MAILSHOT_RECIPIENT'
    }, {
        'name':
        'Edit Applications',
        'codename':
        'IMP_EXPORTER_CONTACTS:EDIT_APPLICATION:{id}:IMP_CERT_SEARCH_CASES_LHS'
    }, {
        'name':
        'Edit Applications',
        'codename':
        'IMP_EXPORTER_CONTACTS:EDIT_APPLICATION:{id}:IMP_CERT_EDIT_APPLICATION'
    }]
}, {
    'name':
    'Exporter Contacts:View Applications/Certificates:{id}',
    'description':
    'Users in this role have the ability to view all applications and certificates for a particular exporter.',
    'role_order':
    30,
    'permissions': [{
        'name':
        'View Applications/Certificates',
        'codename':
        'IMP_EXPORTER_CONTACTS:VIEW_APPLICATION:{id}:MAILSHOT_RECIPIENT'
    }, {
        'name':
        'View Applications/Certificates',
        'codename':
        'IMP_EXPORTER_CONTACTS:VIEW_APPLICATION:{id}:IMP_CERT_VIEW_APPLICATION'
    }, {
        'name':
        'View Applications/Certificates',
        'codename':
        'IMP_EXPORTER_CONTACTS:VIEW_APPLICATION:{id}:IMP_CERT_SEARCH_CASES_LHS'
    }]
}]
