from web.domains.mailshot.models import Mailshot
from web.tests.auth import AuthTestCase
from web.tests.domains.template.factory import TemplateFactory

from .factory import MailshotFactory

LOGIN_URL = '/'


class MailshotListViewTest(AuthTestCase):
    url = '/mailshot/'
    redirect_url = f'{LOGIN_URL}?next={url}'

    def test_authorized_access(self):
        self.login()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_page_title(self):
        self.login()
        response = self.client.get(self.url)
        self.assertEqual(response.context_data['page_title'],
                         'Maintain Mailshots')

    def test_number_of_pages(self):
        # Create 51 product legislation as paging lists 50 items per page
        for i in range(62):
            MailshotFactory()

        self.login()
        response = self.client.get(self.url)
        page = response.context_data['page']
        self.assertEqual(page.paginator.num_pages, 2)

    def test_page_results(self):
        for i in range(65):
            MailshotFactory()
        self.login()
        response = self.client.get(self.url + '?page=2')
        page = response.context_data['page']
        self.assertEqual(len(page.object_list), 15)


class MailshotCreateViewTest(AuthTestCase):
    url = '/mailshot/new/'
    redirect_url = f'{LOGIN_URL}?next={url}'

    def setUp(self):
        super().setUp()
        # Create publish mailshot template for testing
        TemplateFactory(
            template_code='PUBLISH_MAILSHOT',
            template_title='New Mailshot',
            template_content='Template Content')  # Create a constabulary

    def test_anonymous_access_redirects(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.redirect_url)

    def test_authorized_access_redirects(self):
        self.login()
        response = self.client.get(self.url)
        mailshot = Mailshot.objects.first()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/mailshot/{mailshot.id}/edit/')

    def test_create_as_draft(self):
        self.login()
        self.client.get(self.url)
        mailshot = Mailshot.objects.first()
        self.assertEqual(mailshot.status, Mailshot.DRAFT)


class MailshotEditViewTest(AuthTestCase):
    def setUp(self):
        super().setUp()
        self.mailshot = MailshotFactory(
            status=Mailshot.DRAFT)  # Create a mailshot
        self.mailshot.save()
        self.url = f'/mailshot/{self.mailshot.id}/edit/'
        self.redirect_url = f'{LOGIN_URL}?next={self.url}'

    def test_anonymous_access_redirects(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.redirect_url)

    def test_authorized_access(self):
        self.login()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_page_title(self):
        self.login()
        response = self.client.get(self.url)
        self.assertEqual(response.context_data['page_title'],
                         f"Editing {self.mailshot}")


class MailshotDetailViewTest(AuthTestCase):
    def setUp(self):
        super().setUp()
        self.mailshot = MailshotFactory()  # Create a mailshot
        self.mailshot.save()
        self.url = f'/mailshot/{self.mailshot.id}/'
        self.redirect_url = f'{LOGIN_URL}?next={self.url}'

    def test_anonymous_access_redirects(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.redirect_url)

    def test_authorized_access(self):
        self.login()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_page_title(self):
        self.login()
        response = self.client.get(self.url)
        self.assertEqual(response.context_data['page_title'],
                         f"Viewing {self.mailshot}")
