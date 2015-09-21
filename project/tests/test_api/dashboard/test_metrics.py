#
# Copyright (c) 2015 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from test_utils import ApiTestCase
from objects import Organization, DataSet, User


expected_metrics_keys = ["appsDown", "appsRunning", "datasetCount", "domainsUsage", "domainsUsagePercent",
                         "latestEvents", "memoryUsage", "memoryUsageAbsolute", "privateDatasets", "publicDatasets",
                         "serviceUsage", "serviceUsagePercent", "totalUsers"]


class Metrics(ApiTestCase):
    @classmethod
    def setUpClass(cls):
        cls.step("Retrieve metrics for seedorg")
        cls.seedorg = Organization.get_org_and_space_by_name(org_name="seedorg")[0]
        cls.seedorg.api_get_metrics()

    def test_metrics_contains_all_keys(self):
        self.step("Check that metrics response contains all expected fields")
        keys = list(self.seedorg.metrics.keys())
        self.assertUnorderedListEqual(keys, expected_metrics_keys)

    def test_service_count(self):
        self.step("Get apps and services from cf and check that servivceUsage metrics is correct")
        apps, services = self.seedorg.cf_api_get_apps_and_services()
        self.assertEqual(self.seedorg.metrics["serviceUsage"], len(services))

    def test_application_metrics(self):
        self.step("Get apps from cf and check that appsRunning and appsDown metrics are correct")
        cf_apps_up = []
        cf_apps_down = []
        org_spaces = self.seedorg.cf_api_get_spaces()
        for space in org_spaces:
            apps, _ = space.cf_api_get_space_summary()
            for app in apps:
                if app.is_started:
                    cf_apps_up.append(app)
                else:
                    cf_apps_down.append(app)
        dashboard_apps_running = self.seedorg.metrics["appsRunning"]
        dashboard_apps_down = self.seedorg.metrics["appsDown"]
        metrics_are_equal = (len(cf_apps_up) == dashboard_apps_running and len(cf_apps_down) == dashboard_apps_down)
        self.assertTrue(metrics_are_equal,
                        "\nApps running: {} - expected: {}\nApps down: {} - expected: {}".format(dashboard_apps_running,
                                                                                                 len(cf_apps_up),
                                                                                                 dashboard_apps_down,
                                                                                                 len(cf_apps_down)))

    def test_user_count(self):
        self.step("Get org users from cf and check that totalUsers metrics is correct")
        cf_user_list = User.cf_api_get_list_in_organization(org_guid=self.seedorg.guid)
        dashboard_total_users = self.seedorg.metrics["totalUsers"]
        self.assertEqual(len(cf_user_list), dashboard_total_users,
                         "\nUsers: {} - expected: {}".format(dashboard_total_users, len(cf_user_list)))

    def test_data_metrics(self):
        self.step("Get seedorg datasets and check datasetCount, privateDatasets, publicDatasets metrics are correct")
        public_datasets = []
        private_datasets = []
        datasets = DataSet.api_get_list([self.seedorg])
        for table in datasets:
            if table.is_public:
                public_datasets.append(table)
            else:
                private_datasets.append(table)
        dashboard_datasets_count = self.seedorg.metrics['datasetCount']
        dashboard_private_datasets = self.seedorg.metrics['privateDatasets']
        dashboard_public_datasets = self.seedorg.metrics['publicDatasets']
        metrics_are_equal = (len(datasets) == dashboard_datasets_count and
                             len(private_datasets) == dashboard_private_datasets and
                             len(public_datasets) == dashboard_public_datasets)
        self.assertTrue(metrics_are_equal,
                        "\nDatasets count: {} - expected: {}\nPrivate datasets: {} - expected: {}"
                        "\nPublic datasets: {} - expected: {}".format(dashboard_datasets_count, len(datasets),
                                                                      dashboard_private_datasets, len(private_datasets),
                                                                      dashboard_public_datasets, len(public_datasets)))
