# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import time
import requests
from jsonschema import validate
from traitlets import List, Dict
from traitlets.config import Configurable
from . import schema


class RucioConfig(Configurable):  # pragma: no cover
    instances = List(Dict(config=True), config=True)


class Config:
    def __init__(self, rucio_config):
        self.instances = dict()
        self.remote_instances = dict()

        validate(rucio_config.instances, schema=schema.root)
        self.config = rucio_config

        instances = self.config.instances
        for instance in instances:
            if "$url" in instance:
                remote_config, cache_expires_at = self._preprocess_remote_config(
                    instance)

                instance_name = instance['name']
                self.instances[instance_name] = instance
                self.remote_instances[instance_name] = {
                    'expires_at': cache_expires_at,
                    'instance': remote_config
                }
            else:
                instance_name = instance['name']
                self.instances[instance_name] = instance

    def get_instance_config(self, instance_name):
        instance = self.instances[instance_name]
        if "$url" not in instance:
            return instance

        remote_instance = self.remote_instances[instance_name]
        if remote_instance['expires_at'] >= int(time.time()):
            return remote_instance['instance']

        remote_config, cache_expires_at = self._preprocess_remote_config(instance)
        self.remote_instances[instance_name] = {
            'expires_at': cache_expires_at,
            'instance': remote_config
        }
        return remote_config

    def list_instances(self):
        instances = []
        for instance_name in self.instances:
            instances.append({
                'name': instance_name,
                'display_name': self.instances[instance_name]['display_name']
            })

        return instances

    def _preprocess_remote_config(self, remote_config):
        instance = self._retrieve_remote_config(remote_config['$url'])

        for config_item in remote_config:
            instance[config_item] = remote_config[config_item]

        validate(instance, schema=schema.instance)

        if "cache_expires_at" in remote_config:
            cache_expires_at = remote_config['cache_expires_at']
        else:
            # Default lifetime is 24 hours
            cache_expires_at = int(time.time()) + (24 * 3600)

        return (instance, cache_expires_at)

    def _retrieve_remote_config(self, url):
        response = requests.get(url)
        data = response.json()
        validate(data, schema=schema.remote_instance)

        return data
