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

from abc import ABCMeta, abstractclassmethod

from ...http_calls import cloud_foundry as cf
from ..http_client_configuration import HttpClientConfiguration
from ..http_client_type import HttpClientType
from ...constants import TapComponent
from .base import BaseConfigurationProvider


class BaseBrokerConfigurationProvider(BaseConfigurationProvider, metaclass=ABCMeta):
    """Base class that all broker configuration provider implementations derive from."""
    username_env_key = "AUTH_USER"
    password_env_key = "AUTH_PASS"
    environment_json = "environment_json"

    @classmethod
    def provide_configuration(cls) -> HttpClientConfiguration:
        """Provide http client configuration."""
        response = cf.cf_api_get_apps()
        app_guid = next((app["metadata"]["guid"] for app in response
                         if app["entity"]["name"] == cls.tap_component().value), None)
        assert app_guid is not None, "App {} was not found on CF".format(cls.tap_component.value)
        app_broker_env = cf.cf_api_get_app_env(app_guid)
        return HttpClientConfiguration(
            cls.http_client_type(),
            cls.http_client_url(),
            app_broker_env[cls.environment_json][cls.username_env_key],
            app_broker_env[cls.environment_json][cls.username_env_key]
        )

    @abstractclassmethod
    def tap_component(self) -> TapComponent:
        """Provide tap component."""

    @abstractclassmethod
    def http_client_type(self) -> HttpClientType:
        """Provide http client type."""

    @abstractclassmethod
    def http_client_url(self) -> str:
        """Provide http client url."""

    @classmethod
    def _get_environment(cls):
        """Provide environment variables."""
        response = cf.cf_api_get_apps()
        app_guid = next((app["metadata"]["guid"] for app in response
                         if app["entity"]["name"] == cls.tap_component().value), None)
        assert app_guid is not None, "No such app {}".format(cls.tap_component())
        return cf.cf_api_get_app_env(app_guid)
