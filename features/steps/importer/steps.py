from behave import then, when, given
from web.tests.domains.importer.factory import ImporterFactory
from web.tests.domains.office.factory import OfficeFactory
from features.steps.shared import find_element_with_text, specific_user_navigates_to_page

from web.domains.importer.models import Importer
from selenium.webdriver.support.ui import Select


@given(u'An importer with status "{imp_status}" is created in the system')  # NOQA: F811
def step_impl(context, imp_status):
    if imp_status.lower() == 'current':
        is_active = True

    if imp_status.lower() == 'archived':
        is_active = False

    ImporterFactory(
        name=f'{imp_status} Importer',
        type=Importer.ORGANISATION,
        is_active=is_active
    )


@when(u'the user selects to filter importers with status "{imp_status}"')  # NOQA: F811
def step_impl(context, imp_status):
    status = ""

    if imp_status.lower() == "archived":
        status = "False"

    if imp_status.lower() == "current":
        status = "True"

    select = Select(context.browser.find_element_by_id('id_status'))
    select.select_by_value(status)


@when(u'submits the import search from')  # NOQA: F811
def step_impl(context):
    context.browser.find_element_by_id('btn-submit-search').click()


@then(u'the importer search results contain "{count}" results')  # NOQA: F811
def step_impl(context, count):
    elements = context.browser.find_elements_by_css_selector('#tbl-search-results .result-row')
    element_count = len(elements)

    assert element_count == int(count), f'expecting {count} of elements in search results but found {element_count}'


@then(u'the result at row "{row}" has the name "{name}"')  # NOQA: F811
def step_impl(context, row, name):
    element = context.browser.find_element_by_css_selector(f'#tbl-search-results .result-row:nth-child({int(row)}) td:nth-child(2)')

    assert name in element.text, f'could not find {name} in {element.text}'


@then(u'the result at row "{row}" has the status "{status}"')  # NOQA: F811
def step_impl(context, row, status):
    element = context.browser.find_element_by_css_selector(f'#tbl-search-results .result-row:nth-child({int(row)}) td:nth-child(1)')
    assert status.lower() in element.text.lower(), f'could not find {status} in {element.text}'


@then(u'the result at row "{row}" has the address "{address}"')  # NOQA: F811
def step_impl(context, row, address):
    element = context.browser.find_element_by_css_selector(f'#tbl-search-results .result-row:nth-child({int(row)}) td:nth-child(3)')
    assert address.lower() in element.text.lower(), f'could not find {address} in {element.text}'


@then(u'the result at row "{row}" has the action button "{action}"')  # NOQA: F811
def step_impl(context, row, action):
    context.browser.find_element_by_css_selector(
        f'#tbl-search-results .result-row:nth-child({int(row)}) td:nth-child(4) [data-input_action="{action}"]'
    )


@given(u'the importer "{importer_name}" is created in the system')  # NOQA: F811
def create_importer(context, importer_name):
    assert importer_name in context.IMPORTERS, f'importer {importer_name} not found. Add it to context.IMPORTERS'

    importer_data = context.IMPORTERS[importer_name].copy()
    del importer_data['offices']
    importer = ImporterFactory(**importer_data)

    for office in context.IMPORTERS[importer_name]['offices']:
        importer.offices.add(OfficeFactory(**office))

    importer.save()


@when(u'clicks on "{importer_name}" importer name on the importer search results list')  # NOQA: F811
def click_on_importer_name(context, importer_name):
    find_element_with_text(context, importer_name, "a[@role = 'model-link']").click()


@then(u'the view "{importer_name}" importer page is displayed')  # NOQA: F811
def step_impl(context, importer_name):
    assert importer_name in context.IMPORTERS, f'importer {importer_name} not found. Add it to context.IMPORTERS'

    header = context.browser.find_element_by_css_selector('#context-header h2')
    search = f'View Importer - {importer_name}'
    assert header.text == search, f'expecting header with text "{search}" but got {header.text}'

    importer_data = context.IMPORTERS[importer_name]

    importer_name_field = context.browser.find_element_by_css_selector('form [data-label="Name"]')
    search = importer_data['name']
    assert importer_name_field.text == search, f'expecting header with text "{search}" but got {importer_name_field.text}'


@given(u'the user "{user}" navigates to Importer display page of "{importer_name}"')  # NOQA: F811
@when(u'the user "{user}" navigates to Importer display page of "{importer_name}"')  # NOQA: F811
def step_impl(context, user, importer_name):
    create_importer(context, importer_name)
    specific_user_navigates_to_page(context, user, "Importer List page")
    click_on_importer_name(context, importer_name)


@when(u'the user clicks to navigate back to importer list page')  # NOQA: F811
def step_impl(context):
    context.browser.find_element_by_css_selector('main #content a.prev-link').click()


@then(u'the importer list page is displayed')  # NOQA: F811
def step_impl(context):
    header = context.browser.find_element_by_css_selector('#context-header h2')
    search = 'Maintain Importers'
    assert header.text == search, f'expecting header with text "{search}" but got {header.text}'


@then(u'the following Importer display page fields have the values')  # NOQA: F811
def step_impl(context):
    for field, value in context.table:
        found_value = context.browser.find_element_by_css_selector(f'[data-label="{field}"]').text
        assert value == found_value, f'expecting field "{field}" to be "{value}" but got "{found_value}"'


@then(u'the following Importer display page Current office data is showned')  # NOQA: F811
def step_impl(context):
    context.browser.find_element_by_id('tg-offices-CURRENT').click()
    field_map = {  # field name to table column mapping
        'Address': 1,
        'Post Code': 2,
        'ROI': 3
    }
    for row, field, value in context.table:
        assert field in field_map, f'Unknown Office field {field}'
        column = field_map[field]

        selector = f'.tab-content[data-tab-key="CURRENT"] table tr:nth-child({row}) td:nth-child({column})'
        found_value = context.browser.find_element_by_css_selector(selector).text
        assert value == found_value, f'expecting to find "{value}" but got "{found_value}"'


@then(u'the Importer display page has no no Archived offices')  # NOQA: F811
def step_impl(context):
    context.browser.find_element_by_id('tg-offices-ARCHIVED').click()
    selector = '.tab-content[data-tab-key="ARCHIVED"] table tr:nth-child(1) td:nth-child(1)'
    value = "There are no offices"
    found_value = context.browser.find_element_by_css_selector(selector).text
    assert value == found_value, f'expecting to find "{value}" but got "{found_value}"'


@when(u'the user "{user}" navigates to Importer edit page of "{importer_name}"')  # NOQA: F811
@given(u'the user "{user}" navigates to Importer edit page of "{importer_name}"')  # NOQA: F811
def step_impl(context, user, importer_name):
    create_importer(context, importer_name)
    specific_user_navigates_to_page(context, user, "Importer List page")
    context.browser.execute_script("window.scrollBy(-15000,0);")
    context.browser.find_element_by_css_selector('a.icon-pencil').click()


@then(u'the following Importer edit page fields have the values')  # NOQA: F811
def step_impl(context):
    for field, value in context.table:
        id = f'#id_{field.lower().replace(" ","_")}'

        if field == 'Type' or field == 'Region origin':
            found_value = (Select(context.browser.find_element_by_css_selector(id))).first_selected_option.text
        else:
            found_value = context.browser.find_element_by_css_selector(id).get_attribute('value')
        assert value == found_value, f'expecting field "{field}" to be "{value}" but got "{found_value}"'


@then(u'the following Importer edit page office data is showned')  # NOQA: F811
def step_impl(context):
    field_map = {  # field name to table column mapping
        'Status': 1,
        'Address': 2,
        'Post Code': 3,
        'ROI': 4
    }
    for row, field, value in context.table:
        assert field in field_map, f'Unknown Office field {field}'
        column = field_map[field]

        selector = f'#tbl-offices tr:nth-child({row}) td:nth-child({column})'
        found_value = context.browser.find_element_by_css_selector(selector).text
        assert value == found_value, f'expecting to find "{value}" but got "{found_value}"'


@when(u'the user clicks on add office')  # NOQA: F811
def step_impl(context):
    context.browser.find_element_by_id('btn-add-office').click()


@when(u'the user enters "{address}" in the new office address fields')  # NOQA: F811
def step_impl(context, address):
    context.browser.find_element_by_css_selector('.new-form-row:last-child textarea').send_keys(address)


@when(u'the user submits the importer edit form')  # NOQA: F811
def step_impl(context):
    context.browser.find_element_by_id('btn-submit').click()


@then(u'the user is redirected to the importer display page of "{importer_name}"')  # NOQA: F811
def step_impl(context, importer_name):
    el_text = context.browser.find_element_by_css_selector('#context-header h2').text
    assert f'View Importer - {importer_name}' == el_text


@then(u'the count of addreses on the importer display page is "{count}"')  # NOQA: F811
def step_impl(context, count):
    els = context.browser.find_elements_by_css_selector('#tbl-offices tbody tr')

    assert count == len(els)


@then(u'the Importer edit page office form shows an error on the address field')  # NOQA: F811
def step_impl(context):
    el = context.browser.find_element_by_css_selector('#id_form-0-address + .error-message')

    assert 'Cannot be empty' == el.text
