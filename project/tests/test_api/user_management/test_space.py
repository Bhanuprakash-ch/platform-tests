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

from constants.HttpStatus import UserManagementHttpStatus as HttpStatus
from constants.tap_components import TapComponent as TAP
from test_utils import ApiTestCase, cleanup_after_failed_setup, priority, components
from objects import Organization, Space, User


@components(TAP.user_management)
class Spaces(ApiTestCase):
    @classmethod
    @cleanup_after_failed_setup(Organization.cf_api_tear_down_test_orgs)
    def setUpClass(cls):
        cls.step("Create an organization")
        cls.test_org = Organization.api_create()

    @priority.medium
    def test_get_spaces_list_in_new_org(self):
        self.step("Create new organization")
        org = Organization.api_create()
        self.step("Get list of spaces in the org and check that there are none")
        spaces = org.api_get_spaces()
        self.assertEqual(len(spaces), 0, "There are spaces in a new organization")

    @priority.high
    def test_create_space(self):
        self.step("Create new space in the organization")
        space = Space.api_create(org=self.test_org)
        self.step("Check that the space is on the org space list")
        spaces = Space.api_get_list()
        self.assertIn(space, spaces)

    @priority.medium
    def test_cannot_create_space_with_existing_name(self):
        self.step("Create a space")
        space = Space.api_create(org=self.test_org)
        self.step("Check that attempt to create a space with the same name in the same org returns an error")
        self.assertRaisesUnexpectedResponse(HttpStatus.CODE_BAD_REQUEST, HttpStatus.MSG_BAD_REQUEST, Space.api_create,
                                            org=self.test_org, name=space.name)

    @priority.low
    def test_create_space_with_long_name(self):
        self.step("Create space with name 400 char long")
        long_name = Space.NAME_PREFIX + "t" * 400
        space = Space.api_create(org=self.test_org, name=long_name)
        self.step("Check that the space with long name is present on space list")
        spaces = Space.api_get_list()
        self.assertIn(space, spaces)

    @priority.low
    def test_create_space_with_empty_name(self):
        self.step("Check that attempt to create space with empty name returns an error")
        self.assertRaisesUnexpectedResponse(HttpStatus.CODE_BAD_REQUEST, HttpStatus.MSG_BAD_REQUEST, Space.api_create,
                                            name="", org=self.test_org)

    @priority.high
    def test_delete_space(self):
        self.step("Create a space")
        space = Space.api_create(org=self.test_org)
        self.step("Delete the space")
        space.api_delete(org=self.test_org)
        self.step("Check that the deleted space is not present on the space list")
        self.assertNotInWithRetry(space, Space.api_get_list)

    @priority.low
    def test_cannot_delete_not_existing_space(self):
        self.step("Create a space")
        space = Space.api_create(org=self.test_org)
        self.step("Delete the space")
        space.api_delete(org=self.test_org)
        self.assertNotInWithRetry(space, Space.api_get_list)
        self.step("Check that attempt to delete the space again returns an error")
        self.assertRaisesUnexpectedResponse(HttpStatus.CODE_NOT_FOUND, HttpStatus.MSG_NOT_FOUND, space.api_delete)

    @priority.low
    def test_cannot_delete_space_with_user(self):
        self.step("Create a space")
        space = Space.api_create(org=self.test_org)
        self.step("Add new platform user to the space")
        User.api_create_by_adding_to_space(org_guid=self.test_org.guid, space_guid=space.guid)
        self.step("Delete the space")
        space.api_delete(org=self.test_org)
        self.step("Check that the space is not on the space list")
        self.assertNotInWithRetry(space, Space.api_get_list)
