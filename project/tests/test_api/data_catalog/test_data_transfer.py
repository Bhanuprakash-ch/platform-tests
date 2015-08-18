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

import time
import unittest

from test_utils import ApiTestCase, cleanup_after_failed_setup, get_logger, get_admin_client, config
from test_utils.objects import Organization, Transfer, DataSet
import test_utils.api_calls.das_api_calls as das_api


logger = get_logger("test data transfer")


class TestDataTransfer(ApiTestCase):

    @classmethod
    @cleanup_after_failed_setup(Organization.api_delete_test_orgs)
    def setUpClass(cls):
        cls.org = Organization.create()
        cls.org.add_admin()

    def test_get_transfers(self):
        transfers = Transfer.api_get_list(orgs=[self.org])
        logger.info("{} transfers".format(len(transfers)))

    def test_submit_transfer(self):
        data_source = Transfer.get_test_transfer_link()
        expected_transfer = Transfer.api_create(source=data_source, org_guid=self.org.guid)
        expected_transfer.ensure_finished()
        transfer = Transfer.api_get(expected_transfer.id)
        self.assertAttributesEqual(transfer, expected_transfer)

    def test_match_dataset_to_transfer(self):
        data_source = Transfer.get_test_transfer_link()
        expected_transfer = Transfer.api_create(source=data_source, org_guid=self.org.guid)
        expected_transfer.ensure_finished()
        transfers = Transfer.api_get_list(orgs=[self.org])
        self.assertInList(expected_transfer, transfers)
        dataset = DataSet.api_get_matching_to_transfer(org_list=[self.org], transfer=expected_transfer)
        datasets_data = DataSet.api_get_list_and_metadata(org_list=[self.org])
        datasets = datasets_data["data_sets"]
        self.assertInList(dataset, datasets)

    @unittest.skipIf(config.TEST_SETTINGS["TEST_ENVIRONMENT"] == "demo-gotapaas.com", "Change not yet deployed on demo")
    def test_no_token_in_create_transfer_response(self):
        """Verify that the request to create a transfer does not leak 'token' field"""
        response = das_api.api_create_das_request(
            client=get_admin_client(),
            source=Transfer.get_test_transfer_link(),
            title="test-transfer-{}".format(time.time()),
            is_public=False,
            org_guid=self.org.guid
        )
        self.assertTrue("token" not in response, "token should not be returned in response")
