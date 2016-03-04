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

import itertools

from constants.services import PARAMETRIZED_SERVICE_INSTANCES, ServiceLabels
from constants.tap_components import TapComponent as TAP
from test_utils import ApiTestCase, iPython, get_test_name, priority, components
from objects import ServiceInstance, ServiceType, Organization, User
from constants.HttpStatus import ServiceCatalogHttpStatus as HttpStatus


@components(TAP.service_catalog, TAP.application_broker, TAP.gearpump_broker, TAP.hbase_broker, TAP.hdfs_broker,
            TAP.kafka_broker, TAP.smtp_broker, TAP.yarn_broker, TAP.zookeeper_broker, TAP.zookeeper_wssb_broker)
class MarketplaceServices(ApiTestCase):

    @classmethod
    def setUpClass(cls):
        cls.step("Create test organization and test space")
        cls.test_org = Organization.api_create(space_names=("test-space",))
        cls.test_space = cls.test_org.spaces[0]
        cls.step("Get list of available services from Marketplace")
        cls.marketplace = ServiceType.api_get_list_from_marketplace(cls.test_space.guid)
        cls.step("Create space developer client")
        cls.space_developer_client = User.api_create_by_adding_to_space(cls.test_org.guid, cls.test_space.guid,
                                                                        roles=User.SPACE_ROLES["developer"]).login()
        cls.step("Create space auditor client")
        cls.space_auditor_client = User.api_create_by_adding_to_space(cls.test_org.guid, cls.test_space.guid,
                                                                      roles=User.SPACE_ROLES["auditor"]).login()
        cls.step("Create space manager client")
        cls.space_manager_client = User.api_create_by_adding_to_space(cls.test_org.guid, cls.test_space.guid,
                                                                      roles=User.SPACE_ROLES["manager"]).login()

    def _create_and_delete_service_instance(self, org_guid, space_guid, service_label, plan_guid):
        self.step("Create service instance")
        instance = ServiceInstance.api_create(
            org_guid=org_guid,
            space_guid=space_guid,
            service_label=service_label,
            service_plan_guid=plan_guid
        )
        self.step("Check that the instance was created")
        instances = ServiceInstance.api_get_list(space_guid=space_guid)
        self.assertIn(instance, instances)
        self.step("Delete the instance")
        instance.api_delete()
        self.step("Check that the instance was deleted")
        instances = ServiceInstance.api_get_list(space_guid=space_guid)
        self.assertNotIn(instance, instances)

    def _create_ipython_instance_and_login(self, param_key, param_value):
        param = {param_key: param_value}
        self.step("Create service instance and check it exist in list")
        ipython = iPython(self.test_org.guid, self.test_space.guid, params=param)
        self.assertInWithRetry(ipython.instance, ServiceInstance.api_get_list, self.test_space.guid)
        self.step("Get credentials for the new ipython service instance")
        ipython.get_credentials()
        ipython.login()
        terminal = ipython.connect_to_terminal(terminal_no=0)
        _ = terminal.get_output()
        return terminal

    @priority.medium
    def test_check_marketplace_services_list_vs_cloudfoundry(self):
        self.step("Check that services in cf are the same as in Marketplace")
        cf_marketplace = ServiceType.cf_api_get_list_from_marketplace_by_space(self.test_space.guid)
        self.assertUnorderedListEqual(self.marketplace, cf_marketplace)

    @priority.high
    def test_create_and_delete_service_instance(self):
        tested_service_types = [st for st in self.marketplace if st.label not in PARAMETRIZED_SERVICE_INSTANCES]
        for service_type in tested_service_types:
            for plan in service_type.service_plans:
                with self.subTest(service=service_type.label, plan=plan["name"]):
                    self._create_and_delete_service_instance(self.test_org.guid, self.test_space.guid,
                                                             service_type.label, plan["guid"])

    @priority.low
    def test_create_instance_with_non_required_parameter(self):
        param_key = "test_param"
        param_value = "test_value"
        terminal = self._create_ipython_instance_and_login(param_key, param_value)
        terminal.send_input("env\n")
        output = "".join(terminal.get_output())
        self.assertIn("{}={}".format(param_key, param_value), output)

    @priority.medium
    def test_cannot_create_service_instance_with_name_of_an_existing_instance(self):
        existing_name = get_test_name()
        self.step("Create service instance")
        instance = ServiceInstance.api_create(
            org_guid=self.test_org.guid,
            space_guid=self.test_space.guid,
            service_label=ServiceLabels.KAFKA,
            name=existing_name,
            service_plan_name="shared"
        )
        service_list = ServiceInstance.api_get_list(space_guid=self.test_space.guid)
        self.step("Check that the instance was created")
        self.assertIn(instance, service_list, "Instance was not created")
        for service_type in self.marketplace:
            plan_guid = next(iter(service_type.service_plan_guids))
            with self.subTest(service_type=service_type):
                self.assertRaisesUnexpectedResponse(HttpStatus.CODE_CONFLICT,
                                                    HttpStatus.MSG_SERVICE_NAME_TAKEN.format(existing_name),
                                                    ServiceInstance.api_create, self.test_org.guid,
                                                    self.test_space.guid, service_type.label, existing_name,
                                                    service_plan_guid=plan_guid, client=self.space_developer_client)
        self.assertUnorderedListEqual(service_list, ServiceInstance.api_get_list(space_guid=self.test_space.guid),
                                      "Some new services were created")

    @priority.low
    def test_cannot_create_instance_without_a_name(self):
        """DPNG-5154 Http status 500 when trying to create a service instance without a name"""
        expected_instance_list = ServiceInstance.api_get_list(self.test_space.guid)
        self.step("Check that gateway instance cannot be created with empty name")
        self.assertRaisesUnexpectedResponse(HttpStatus.CODE_BAD_REQUEST, HttpStatus.MSG_BAD_REQUEST,
                                            ServiceInstance.api_create, self.test_org.guid, self.test_space.guid,
                                            ServiceLabels.KAFKA, "", service_plan_name="shared",
                                            client=self.space_developer_client)
        self.assertUnorderedListEqual(expected_instance_list, ServiceInstance.api_get_list(self.test_space.guid),
                                      "New instance was created")

    @priority.medium
    def test_cannot_create_instance_as_non_space_developer(self):
        test_clients = {"space_auditor": self.space_auditor_client, "space_manager": self.space_manager_client}
        for service_type, (name, client) in itertools.product(self.marketplace, test_clients.items()):
            for plan in service_type.service_plans:
                with self.subTest(service=service_type.label, plan=plan["name"]):
                    self.step("Try to create new gateway instance")
                    self.assertRaisesUnexpectedResponse(HttpStatus.CODE_FORBIDDEN, HttpStatus.MSG_FORBIDDEN,
                                                        ServiceInstance.api_create, self.test_org.guid,
                                                        self.test_space.guid, service_type.label,
                                                        service_plan_guid=plan["guid"], client=client)


