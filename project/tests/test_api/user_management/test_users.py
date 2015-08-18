#
# Copyright (c) 2015 Intel Corporation
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

from test_utils import ApiTestCase, cleanup_after_failed_setup, ClientRole, get_admin_client
from test_utils.objects import Organization, User


class TestOrganizationUsers(ApiTestCase):

    @classmethod
    @cleanup_after_failed_setup(Organization.api_delete_test_orgs)
    def setUpClass(cls):
        cls.organization = Organization.create()
        cls.org_manager_client = User.create_user_for_client(cls.organization.guid, ClientRole.org_manager).app_client

    def test_create_organization_user_with_role(self):
        """Create a user with each of the roles allowed"""
        for role in ["managers", "auditors", "billing_managers"]:
            with self.subTest(role=role):
                expected_user = User.create_via_organization(self.organization.guid, roles=[role])
                users = User.get_list_via_organization(self.organization.guid)
                self.assertInList(expected_user, users)

    def test_create_organization_user(self):
        """Verify that each, admin and organization manager, can create an organization user"""
        for client in [self.org_manager_client, get_admin_client()]:
            with self.subTest(client=client):
                expected_user = User.create_via_organization(self.organization.guid, client=client, roles=["managers"])
                users = User.get_list_via_organization(self.organization.guid, client=client)
                self.assertInList(expected_user, users)

    def test_create_organization_user_two_roles(self):
        expected_user = User.create_via_organization(self.organization.guid, roles=["managers", "auditors"])
        users = User.get_list_via_organization(self.organization.guid)
        self.assertInList(expected_user, users)

    def test_create_organization_user_all_roles(self):
        expected_user = User.create_via_organization(self.organization.guid, roles=["managers", "auditors", "billing_managers"])
        users = User.get_list_via_organization(self.organization.guid)
        self.assertInList(expected_user, users)

    def test_create_organization_user_incorrect_role(self):
        self.assertRaisesUnexpectedResponse(400, "", User.create_via_organization,
                                            organization_guid=self.organization.guid, roles=["i-don't-exist"])

    def test_update_organization_user_add_role(self):
        roles = ["managers"]
        new_roles = ["managers", "auditors"]
        expected_user = User.create_via_organization(self.organization.guid, roles=roles)
        users = User.get_list_via_organization(self.organization.guid)
        self.assertInList(expected_user, users)
        expected_user.update_via_organization(new_roles=new_roles)
        users = User.get_list_via_organization(self.organization.guid)
        self.assertInList(expected_user, users)

    def test_update_organization_user_remove_role(self):
        roles = ["managers", "billing_managers"]
        new_roles = ["managers"]
        expected_user = User.create_via_organization(self.organization.guid, roles=roles)
        users = User.get_list_via_organization(self.organization.guid)
        self.assertInList(expected_user, users)
        expected_user.update_via_organization(new_roles=new_roles)
        users = User.get_list_via_organization(self.organization.guid)
        self.assertInList(expected_user, users)

    def test_update_organization_user_change_role(self):
        roles = ["managers"]
        new_roles = ["auditors"]
        expected_user = User.create_via_organization(self.organization.guid, roles=roles)
        users = User.get_list_via_organization(self.organization.guid)
        self.assertInList(expected_user, users)
        expected_user.update_via_organization(new_roles=new_roles)
        users = User.get_list_via_organization(self.organization.guid)
        self.assertInList(expected_user, users)

    def test_delete_organization_user(self):
        expected_user = User.create_via_organization(self.organization.guid)
        users = User.get_list_via_organization(self.organization.guid)
        self.assertInList(expected_user, users)
        expected_user.delete_via_organization()
        users = User.get_list_via_organization(self.organization.guid)
        self.assertNotInList(expected_user, users)


