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
from datetime import datetime
import socket

from .db_client import DBClient
from .platform_version import VersionedComponent
from constants.test_results import TestResult


class TestRunDocument(object):
    COLLECTION_NAME = "test_run"

    def __init__(self, db_client: DBClient, environment, environment_version, suite, release, platform_components):
        self.__db_client = db_client
        self.__environment = environment
        self.__environment_version = environment_version
        self.__suite = suite
        self.__release = release
        self.__platform_components = platform_components

        self.__started_by = socket.gethostname()

        self.__id = None
        self.__start_date = None
        self.__end_date = None
        self.__status = TestResult.success
        self.__test_count = 0
        self.__result = {v: 0 for v in TestResult.values()}
        self.log = None

    def update_result(self, result: TestResult):
        self.__test_count += 1
        self.__result[result.value] += 1
        if result not in (TestResult.success, TestResult.expected_failure):
            self.__status = TestResult.failure
        self.__replace()

    @property
    def id(self):
        return self.__id

    def start(self):
        self.__start_date = datetime.now().isoformat()
        self.__insert()

    def end(self):
        self.__end_date = datetime.now().isoformat()
        self.__replace()

    def __to_mongo_document(self):
        return {
            "environment": self.__environment,
            "environment_version": self.__environment_version,
            "suite": self.__suite,
            "started_by": self.__started_by,
            "release": self.__release,
            "platform_components": VersionedComponent.list_to_db_format(self.__platform_components),
            "start_date": self.__start_date,
            "end_date": self.__end_date,
            "test_count": self.__test_count,
            "result": self.__result,
            "status": self.__status.value,
            "log": self.log
        }

    def __insert(self):
        self.__id = self.__db_client.insert(
            collection_name=self.COLLECTION_NAME,
            document=self.__to_mongo_document()
        )

    def __replace(self):
        self.__db_client.replace(
            collection_name=self.COLLECTION_NAME,
            document_id=self.__id,
            new_document=self.__to_mongo_document()
        )
