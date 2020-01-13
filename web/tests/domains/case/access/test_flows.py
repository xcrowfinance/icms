import datetime

from django.contrib.auth.models import Permission
from django.test import TestCase
from viewflow.models import Process

from web.models import User
from web.tests.domains.user.factory import UserFactory


def grant(user, permission_codename):
    permission = Permission.objects.create(name=permission_codename,
                                           codename=permission_codename,
                                           content_type_id=15)
    user.user_permissions.add(permission)


class ExportAccessRequestFlowTest(TestCase):

    def setUp(self):
        self.test_access_requester = UserFactory(username='test_access_requester',
                                                 password='test',
                                                 password_disposition=User.FULL,
                                                 is_superuser=False,
                                                 is_active=True)
        grant(self.test_access_requester, 'create_access_request')

        self.ilb_admin_user = UserFactory(username='ilb_admin_user',
                                          password='test',
                                          password_disposition=User.FULL,
                                          is_superuser=False,
                                          is_active=True)
        grant(self.ilb_admin_user, 'review_access_request')

    def testFlow(self):
        self.client.force_login(self.test_access_requester)

        response = self.client.post(
            '/viewflow/workflow/web/accessrequest/start/',
            {'request_type': 'MAIN_EXPORTER_ACCESS',
             'organisation_name': 'Test7201',
             'organisation_address': '''50 Victoria St
             London
             SW1H 0TL''',
             '_viewflow_activation-started': datetime.datetime.now().strftime('%d-%b-%Y %H:%M:%S')}
        )
        assert response.status_code == 302
        process = Process.objects.get()
        self.assertEquals('NEW', process.status)

        self.client.logout()
        self.client.force_login(self.ilb_admin_user)

        response = self.client.post(
            '/viewflow/workflow/web/accessrequest/1/review_request/2/',
            {'response': 'MAIN_EXPORTER_ACCESS',
             '_viewflow_activation-started': datetime.datetime.now().strftime('%d-%b-%Y %H:%M:%S')}
        )
        assert response.status_code == 302
        process.refresh_from_db()
        self.assertEquals('NEW', process.status)

        self.assertEquals(2, process.task_set.count())

        # self.assertEquals('DONE', process.status)
