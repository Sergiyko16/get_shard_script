import os
import sys
from dataclasses import dataclass
from typing import List

import yaml


@dataclass
class ShardInfo:
    name: str
    min_system: int
    max_system: int


GCP_REPO_PATH_ENV_NAME = 'GCP_REPO_PATH'

if GCP_REPO_PATH_ENV_NAME not in os.environ:
    print("'GCP_REPO_PATH' environment variable is not specified!")
    exit(1)

production_path = os.path.join(os.environ[GCP_REPO_PATH_ENV_NAME],
                               "playbooks/environments/production/group_vars/all.yml")

staging_path = os.path.join(os.environ[GCP_REPO_PATH_ENV_NAME], "playbooks/environments/staging/group_vars/all.yml")

arguments = sys.argv

if not arguments or len(arguments) < 2:
    print("SystemId should be provided.")
    print("Examples:")
    print("\tpython get_shard.py 4444960")
    print("\tpython get_shard.py 4444960 staging")
    print("\tpython get_shard.py 4444960 production")
    exit(1)

try:
    system_id = int(arguments[1])
except ValueError:
    print('SystemId is invalid')
    exit(1)

environment = "production"

if len(arguments) > 2:
    environment = arguments[2]

config_path = production_path

if environment not in ["staging", "production"]:
    print("Environment is invalid. Allowed values: 'staging', 'production'")
    exit(1)

if environment == "staging":
    config_path = staging_path

with open(config_path, 'r') as file:
    content = file.read()
    content = content.replace(" !vault |", "")

    try:
        yaml_content = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        print(exc)

    shards: List[ShardInfo] = []

    current_min_system_id = 0

    for shard in yaml_content['shards']:
        max_system_id = int(shard['maxSystemId'])

        shards.append(ShardInfo(shard['schema'], current_min_system_id, max_system_id))

        current_min_system_id = max_system_id + 1

    for shard in shards:
        if shard.min_system <= system_id <= shard.max_system:
            print(f"System Id: {system_id}, Shard: {shard.name}, Environment: {environment}")
            exit(0)

    print('Unable to find the shard')
