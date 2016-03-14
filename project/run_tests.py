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

import os
import requests

from teamcity import is_running_under_teamcity

from constants.priority_levels import Priority
from constants.tap_components import TapComponent
from test_utils import config, get_logger, change_log_file_path
from runner.test_runner import TestRunner
from runner.loader import TapTestLoader


logger = get_logger(__name__)


def check_environment_viability():
    """Check that basic calls to the console and cf api work"""
    try:
        domain = config.CONFIG["domain"]
        verify = config.CONFIG["ssl_validation"]
        console_endpoint = "https://console.{}".format(domain)
        cf_endpoint = "https://api.{}/{}/info".format(domain, config.CONFIG["cf_api_version"])
        requests.get(console_endpoint, verify=verify).raise_for_status()
        requests.get(cf_endpoint, verify=verify).raise_for_status()
    except requests.HTTPError as e:
        logger.error("Environment {} is unavailable - status {}".format(e.response.url, e.response.status_code))
        raise


if __name__ == "__main__":

    # parse settings passed from command line and update config
    args = config.parse_arguments()

    if not is_running_under_teamcity():
        log_dir = args.log_file_directory
        os.makedirs(log_dir, exist_ok=True)
        change_log_file_path(args.log_file_directory)

    config.update_test_config(client_type=args.client_type,
                              domain=args.environment,
                              proxy=args.proxy,
                              logged_response_body_length=args.logged_response_body_length,
                              logging_level=args.logging_level,
                              platform_version=args.platform_version,
                              repository=args.repository,
                              database_url=args.database_url,
                              test_suite=args.suite)
    for key in config.LOGGED_CONFIG_KEYS:
        logger.info("{}={}".format(key, config.CONFIG.get(key)))

    # check that environment is up and running
    check_environment_viability()

    # run tests
    runner = TestRunner()
    components = [getattr(TapComponent, c) for c in args.components]
    priority = getattr(Priority, args.priority)
    loader = TapTestLoader(path=args.suite, test_name=args.test, priority=priority, components=components)
    runner.run(loader.test_suite)
