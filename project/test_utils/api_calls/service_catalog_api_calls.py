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

from test_utils import get_logger


APP_NAME = "service-catalog"
logger = get_logger("service-catalog calls")


# ----------------------------------------------- Services ----------------------------------------------- #


def api_get_marketplace_services(client, space_guid):
    """GET /rest/services"""
    logger.debug("------------------ Get marketplace services ------------------")
    return client.call(APP_NAME, "get_marketplace_services", space=space_guid)


def api_get_service(client, service_guid):
    """GET /rest/service/{service_guid}"""
    logger.debug("------------------ Get service {} ------------------".format(service_guid))
    return client.call(APP_NAME, "get_service", service_guid=service_guid)


# ----------------------------------------------- Service Instances ----------------------------------------------- #


def api_get_service_instances(client, space_guid, service_guid):
    """GET /rest/service_instances"""
    logger.debug("--------------- Get service instances for service {} in space {} ---------------".format(service_guid,
                                                                                                          space_guid))
    raise NotImplementedError("Please add swagger schema for this method in swagger/service_catalog_swagger.json")


def api_create_service_instance(client, name, space_guid, service_plan_guid, parameters=None):
    """POST /rest/service_instances"""
    logger.debug("------------------ Create service instance in space {} ------------------".format(space_guid))
    body = {
        "name": name,
        "service_plan_guid": service_plan_guid,
        "space_guid": space_guid,
        "parameters": {"name": name}
    }
    return client.call(APP_NAME, "create_service_instance", body=body)


def api_delete_service_instance(client, service_instance_guid):
    """DELETE /rest/service_instances/{service_instance_guid}"""
    logger.debug("------------------ Delete service instance {} ------------------".format(service_instance_guid))
    return client.call(APP_NAME, "delete_service_instance", instance=service_instance_guid)


# ----------------------------------------------- Applications ----------------------------------------------- #

def api_get_filtered_applications(client, space, service_label=None):
    """GET /rest/apps"""
    logger.info("------------------ Get applications in space {} ------------------".format(space))
    params = {"space": space}
    if service_label is not None:
        params["service_label"] = service_label
    return client.call(APP_NAME, "get_filtered_applications", **params)


def api_get_app_summary(client, app_guid):
    """GET /rest/apps/{app_guid}"""
    logger.debug("------------------ Get {} details ------------------".format(app_guid))
    return client.call(APP_NAME, "get_app_details", app_guid=app_guid)


def api_delete_app(client, app_guid, cascade=True):
    """DELETE /rest/apps/{app_guid}"""
    logger.debug("------------------ Delete app {} ------------------".format(app_guid))
    return client.call(APP_NAME, "delete_app", app_guid=app_guid, cascade=cascade)


def api_get_app_orphan_services(client, app_guid):
    """GET /rest/apps/{app_guid}/orphan_services"""
    logger.debug("------------------ Retrieve orphan services fo app {} ------------------".format(app_guid))
    raise NotImplementedError("Please add swagger schema for this method in swagger/service_catalog_swagger.json")


def api_restage_app(client, app_guid, new_app_name):
    """POST /rest/apps/{app_guid}/status"""
    logger.debug("------------------ Restage app {} ------------------".format(app_guid))
    raise NotImplementedError("Please add swagger schema for this method in swagger/service_catalog_swagger.json")


# ----------------------------------------------- Service Bindings ----------------------------------------------- #


def api_get_app_bindings(client, app_guid):
    """GET /rest/apps/{app_guid}/service_bindings"""
    logger.debug("----------------- Get bindings of app {}-----------------".format(app_guid))
    raise NotImplementedError("Please add swagger schema for this method in swagger/service_catalog_swagger.json")


def api_create_service_binding(client, app_guid, service_instance_guid):
    """POST /rest/apps/{app_guid}/service_bindings"""
    logger.debug("--------------- Create binding for app {} to service {} ---------------".format(app_guid,
                                                                                                 service_instance_guid))
    raise NotImplementedError("Please add swagger schema for this method in swagger/service_catalog_swagger.json")


def api_delete_service_binding(client, binding_guid):
    """DELETE /rest/service_bindings/{binding_guid}"""
    logger.debug("------------------ Delete binding {} ------------------".format(binding_guid))
    raise NotImplementedError("Please add swagger schema for this method in swagger/service_catalog_swagger.json")


# ----------------------------------------------- Atk ----------------------------------------------- #


def api_create_scoring_engine(client, atk_name, instance_name, space_guid, service_plan_guid):
    """POST /rest/orgs/atk/scoring-engine"""
    logger.debug("------------------ Create scoring engine for atk {} ------------------".format(atk_name))
    raise NotImplementedError("Please add schema for this method in app_launcher_helper_swagger.json")
