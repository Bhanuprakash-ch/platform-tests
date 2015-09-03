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

import functools
import subprocess
import time

from . import CfApiClient, get_logger, log_command, get_config_value, TEST_SETTINGS


__all__ = ["cf_login", "cf_target", "cf_push", "cf_create_service", "cf_delete", "cf_env", "cf_delete_service",
           "cf_api_get_service_instances", "cf_api_create_service_instance", "cf_api_env", "cf_api_services",
           "cf_api_app_summary", "cf_api_space_summary", "cf_api_get_org_managers", "cf_api_get_org_billing_managers",
           "cf_api_get_org_auditors", "cf_api_get_organization_spaces", "cf_api_get_space_routes",
           "cf_api_get_space_service_brokers", "cf_api_get_organization_users", "cf_api_delete_org",
           "cf_api_delete_route"]


logger = get_logger("cloud_foundry_cli")


# ------------------------------- command line interface ------------------------------- #

def log_output_on_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except subprocess.SubprocessError as e:
            logger.error(e.output)
            raise
    return wrapper


def cf_login(organization_name, space_name):
    api_url = get_config_value("cf_endpoint")
    username = TEST_SETTINGS["TEST_USERNAME"]
    password = TEST_SETTINGS["TEST_PASSWORD"]
    command = ["cf", "login", "-a", api_url, "-u", username, "-p", password, "-o", organization_name, "-s", space_name]
    if TEST_SETTINGS["TEST_DISABLE_SSL_VALIDATION"] is True:
        command.append("--skip-ssl-validation")
    log_command(command, replace=(password, "[SECRET]"))
    subprocess.check_call(command)


def cf_target(organization=None, space=None):
    command = ["cf", "target"]
    if organization is not None:
        command += ["-o", organization]
    if space is not None:
        command += ["-s", space]
    log_command(command)
    subprocess.check_call(command)


@log_output_on_error
def cf_push(local_path, local_jar):
    command = ["cf", "push", "-f", local_path, "-p", local_jar]
    log_command(command)
    return subprocess.check_output(command).decode()


@log_output_on_error
def cf_create_service(broker_name, plan, instance_name):
    command = ["cf", "create-service", broker_name, plan, instance_name]
    log_command(command)
    return subprocess.check_output(command).decode()


def cf_delete(app_name):
    command = ["cf", "delete", app_name, "-f"]
    log_command(command)
    subprocess.check_call(command)


@log_output_on_error
def cf_env(app_name):
    command = ["cf", "env", app_name]
    log_command(command)
    return subprocess.check_output(command).decode()


def cf_delete_service(service):
    command = ["cf", "delete-service", service, "-f"]
    log_command(command)
    return subprocess.check_call(command)


# ------------------------------- cf api ------------------------------- #

def __get_all_pages(endpoint, query_params=None):
    """For requests which return paginated results"""
    query_params = query_params or {}
    resources = []
    page_num = 1
    while True:
        params = {"results-per-page": 100, "page": page_num}
        params.update(query_params)
        response = CfApiClient.get_client().request(method="GET", endpoint=endpoint, params=params)
        resources.extend(response["resources"])
        if page_num == response["total_pages"]:
            break
        page_num += 1
    return resources


def __ensure_job_finished(job_id, job_name, timeout=120):
    """Ensure that job requested asynchronously is finished within timeout."""
    endpoint = "jobs/{}".format(job_id)
    now = time.time()
    while time.time() - now < timeout:
        response = CfApiClient.get_client().request(method="GET", endpoint=endpoint)
        job_status = response["entity"]["status"]
        if job_status == "finished":
            return
        logger.info("{} - job status: {}".format(job_name, job_status))
        time.sleep(5)
    raise TimeoutError("Job {} did not finish in {}s".format(job_name, timeout))


def cf_api_get_service_instances(org_guid):
    """GET /v2/service_instances"""
    logger.info("------------------ CF: service instances for org {} ------------------".format(org_guid))
    return __get_all_pages(endpoint="service_instances", query_params={"organization_guid": org_guid})


def cf_api_create_service_instance(instance_name, space_guid, service_plan_guid):
    """POST /v2/service_instances"""
    logger.info("------------------ CF: create service instance {} ------------------".format(instance_name))
    return CfApiClient.get_client().request(
        method="POST",
        path="service_instances",
        params={"accepts_incomplete": "true"},
        body={"name": instance_name, "space_guid": space_guid, "service_plan_guid": service_plan_guid}
    )


def cf_api_env(app_guid):
    """GET /apps/{app_guid}/env"""
    logger.info("------------------ CF: env for app {} ------------------".format(app_guid))
    return CfApiClient.get_client().request(method="GET", endpoint="apps/{}/env".format(app_guid))


def cf_api_services(space_guid):
    """GET /v2/apps/{app_guid}/services"""
    logger.info("------------------ CF: services for space {} ------------------".format(space_guid))
    return CfApiClient.get_client().request(method="GET", endpoint="spaces/{}/services".format(space_guid))


def cf_api_app_summary(app_guid):
    """GET /v2/apps/{app_guid}/summary"""
    logger.info("------------------ CF: summary for app {} ------------------".format(app_guid))
    return CfApiClient.get_client().request("GET", "apps/{}/summary".format(app_guid))


def cf_api_space_summary(space_guid):
    """GET /v2/spaces/{space_guid}/summary - Equal to running cf apps and cf services"""
    logger.info("------------------ CF: summary for space {} ------------------".format(space_guid))
    return CfApiClient.get_client().request("GET", "spaces/{}/summary".format(space_guid))


def cf_api_get_org_managers(org_guid):
    """GET /v2/organizations/{org_guid}/managers"""
    logger.info("------------------ CF: managers in org {} ------------------".format(org_guid))
    return __get_all_pages(endpoint="organizations/{}/managers".format(org_guid))


def cf_api_get_org_billing_managers(org_guid):
    """GET /v2/organizations/{org_guid}/billing_managers"""
    logger.info("------------------ CF: billing managers in org {} ------------------".format(org_guid))
    return __get_all_pages(endpoint="organizations/{}/billing_managers".format(org_guid))


def cf_api_get_org_auditors(org_guid):
    """GET /v2/organizations/{org_guid}/auditors"""
    logger.info("------------------ CF: auditors in org {} ------------------".format(org_guid))
    return __get_all_pages(endpoint="organizations/{}/auditors".format(org_guid))


def cf_api_get_organization_spaces(org_guid):
    """GET /v2/organizations/{org_guid}/spaces"""
    logger.info("------------------ CF: spaces in org {} ------------------".format(org_guid))
    return __get_all_pages(endpoint="organizations/{}/spaces".format(org_guid))


def cf_api_get_space_routes(space_guid):
    """GET /v2/spaces/{space_guid}/routes"""
    logger.info("------------------ CF: get routes in space {} ------------------".format(space_guid))
    return CfApiClient.get_client().request(method="GET", endpoint="spaces/{}/routes".format(space_guid))


def cf_api_get_space_service_brokers(space_guid):
    """GET /v2/spaces/{space_guid}/service_brokers"""
    logger.info("------------------ CF: service brokers for space {} ------------------".format(space_guid))
    return __get_all_pages(endpoint="service_brokers", query_params={"space_guid": space_guid})


def cf_api_get_organization_users(org_guid):
    """GET /v2/organizations/{org_guid}/users"""
    logger.info("------------------ CF: get users in org {} ------------------".format(org_guid))
    return __get_all_pages(endpoint="organizations/{}/users".format(org_guid))


def cf_api_get_orgs():
    """GET /v2/organizations"""
    logger.info("------------------ CF: get all organizations ------------------")
    return __get_all_pages(endpoint="organizations")


def cf_api_delete_org(org_guid):
    """DELETE /v2/organizations/{org_guid}"""
    logger.info("------------------ CF: delete organization {} ------------------".format(org_guid))
    response = CfApiClient.get_client().request("DELETE", endpoint="organizations/{}".format(org_guid),
                                                params={"async": "true", "recursive": "true"})
    __ensure_job_finished(job_id=response["entity"]["guid"], job_name="delete org")


def cf_api_delete_route(route_guid):
    """DELETE /v2/routes/{route_guid}"""
    logger.info("------------------ CF: delete route {} ------------------".format(route_guid))
    response = CfApiClient.get_client().request(method="DELETE", endpoint="routes/{}".format(route_guid),
                                                params={"async": "true"})
    __ensure_job_finished(job_id=response["entity"]["guid"], job_name="delete route")