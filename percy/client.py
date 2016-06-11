# -*- coding: utf-8 -*-

from percy.connection import Connection
from percy.environment import Environment
from percy.config import Config
from percy import utils

__all__ = ['Client']


class Client(object):

    def __init__(self, connection=None, config=None, environment=None):
        self._environment = environment if environment else Environment()
        self._config = config if config else Config()
        self._connection = connection if connection else Connection(self.config)

    @property
    def connection(self):
        return self._connection

    @property
    def config(self):
        return self._config

    @property
    def environment(self):
        return self._environment

    def create_build(self, **kwargs):
        repo = kwargs.get('repo') or self.environment.repo
        branch = kwargs.get('branch') or self.environment.branch
        pull_request_number = kwargs.get('pull_request_number') \
            or self.environment.pull_request_number

        data = {
            'data': {
                'type': 'builds',
                'attributes': {
                    'branch': branch,
                    'pull-request-number': pull_request_number,
                }
            }
        }
        path = "{base_url}/repos/{repo}/builds/".format(
            base_url=self.config.api_url,
            repo=repo,
        )
        return self._connection.post(path=path, data=data)

    def finalize_build(self, build_id):
        path = "{base_url}/builds/{build_id}/finalize".format(
            base_url=self.config.api_url,
            build_id=build_id,
        )
        return self._connection.post(path=path, data={})

    def create_snapshot(self, build_id, resources, **kwargs):
        if not resources or len(resources) <= 0:
            raise ValueError(
                'resources should be an array of Percy.Resource objects'
            )
        widths = kwargs.get('widths', self.config.default_widths)
        data = {
            'data': {
                'type': 'snapshots',
                'attributes': {
                    'name': kwargs.get('name'),
                    'enable-javascript': kwargs.get('enable_javascript'),
                    'widths': widths,
                },
                'relationships': {
                    'resources': {
                        'data': [r.serialize() for r in resources],
                    }
                }
            }
        }
        path = "{base_url}/builds/{build_id}/snapshots/".format(
            base_url=self.config.api_url,
            build_id=build_id
        )
        return self._connection.post(path=path, data=data)

    def finalize_snapshot(self, snapshot_id):
        path = "{base_url}/snapshots/{snapshot_id}/finalize".format(
            base_url=self.config.api_url,
            snapshot_id=snapshot_id
        )
        return self._connection.post(path=path, data={})

    def upload_resource(self, build_id, content):
        sha = utils.sha256hash(content)
        data = {
            'data': {
                'type': 'resources',
                'id': sha,
                'attributes': {
                    'base64-content': utils.base64encode(content),
                }

            }
        }
        path = "{base_url}/builds/{build_id}/resources/".format(
            base_url=self.config.api_url,
            build_id=build_id
        )
        return self._connection.post(path=path, data=data)
