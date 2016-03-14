#
# Copyright (c) 2016 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from constants.tap_components import TapComponent as TAP
from test_utils import ConsoleClient, platform_api_calls as api
from test_utils.remote_logger.remote_logger_decorator import log_components
from objects import User, Organization
from runner.tap_test_case import TapTestCase, cleanup_after_failed_setup
from runner.decorators import priority, components



@log_components()
@components(TAP.console)
class AppDevelopmentPage(TapTestCase):

    @classmethod
    @cleanup_after_failed_setup(User.cf_api_tear_down_test_users, User.api_tear_down_test_invitations,
                                Organization.cf_api_tear_down_test_orgs)
    def setUpClass(cls):
        cls.step("Create organization and get test user and admin client")
        test_org = Organization.api_create()
        cls.non_admin_client = User.api_create_by_adding_to_organization(test_org.guid).login()
        cls.admin_client = ConsoleClient.get_admin_client()

    @priority.medium
    def test_get_app_development_page(self):
        clients = {"non_admin": self.non_admin_client, "admin": self.admin_client}
        for name, client in clients.items():
            with self.subTest(client=name):
                self.step("Get 'App development' page")
                page = api.api_get_app_development_page(client)
                self.step("Check that header is present")
                self.assertIn("<h3>Tools</h3>", page)
                self.step("Check that url to cloudfoundry documentation is present")
                self.assertIn('<a href="http://docs.cloudfoundry.org/devguide/#cf" target="_blank">', page)
