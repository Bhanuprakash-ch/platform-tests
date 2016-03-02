#
# Copyright (c) 2016 Intel Corporation
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

from test_utils import cloud_foundry as cf


class Buildpack(object):

    def __init__(self, name, guid, url, filename, position, enabled, locked):
        self.name = name
        self.guid = guid
        self.url = url
        self.filename = filename
        self.enabled = enabled
        self.position = position
        self.locked = locked

    # -------------------------------- cf api -------------------------------- #

    @classmethod
    def cf_api_get_list(cls):
        """
        create buildpack list from cf infos
        :return: list of buildpacks
        """
        cf_data = cf.cf_api_get_buildpacks()
        buildpacks = []
        for data in cf_data:
            buildpack = cls(name=data["entity"]["name"], guid=data["metadata"]["guid"], url=data["metadata"]["url"],
                            filename=data["entity"]["filename"], position=data["entity"]["position"],
                            enabled=data["entity"]["enabled"], locked=data["entity"]["locked"])
            buildpacks.append(buildpack)
        return buildpacks