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

from constants.tap_components import TapComponent as TAP
from test_utils import ApiTestCase, priority, components
from objects import LatestEvent
from test_utils.remote_logger.remote_logger_decorator import log_components


@log_components()
@components(TAP.latest_events_service)
class LatestEventsService(ApiTestCase):

    @priority.low
    def test_latest_events(self):
        self.step("Check that latest events service does not crash after basic request")
        LatestEvent.api_get_latest_events()
