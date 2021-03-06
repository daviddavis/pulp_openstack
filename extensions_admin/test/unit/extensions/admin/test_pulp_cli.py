import unittest

import mock
from pulp.client.commands.repo.cudl import CreateRepositoryCommand, DeleteRepositoryCommand
from pulp.client.commands.repo.sync_publish import PublishStatusCommand, RunPublishRepositoryCommand
from pulp.client.extensions.core import PulpCli

from pulp_openstack.extensions.admin import pulp_cli
from pulp_openstack.extensions.admin import images
from pulp_openstack.extensions.admin.repo_list import ListOpenstackRepositoriesCommand
from pulp_openstack.extensions.admin.upload import UploadOpenstackImageCommand


class TestInitialize(unittest.TestCase):
    def test_structure(self):
        context = mock.MagicMock()
        context.config = {
            'filesystem': {'upload_working_dir': '/a/b/c'},
            'output': {'poll_frequency_in_seconds': 3}
        }
        context.cli = PulpCli(context)

        # create the tree of commands and sections
        pulp_cli.initialize(context)

        # verify that sections exist and have the right commands
        openstack_section = context.cli.root_section.subsections['openstack']

        repo_section = openstack_section.subsections['repo']
        self.assertTrue(isinstance(repo_section.commands['create'], CreateRepositoryCommand))
        self.assertTrue(isinstance(repo_section.commands['delete'], DeleteRepositoryCommand))
        self.assertTrue(isinstance(repo_section.commands['list'], ListOpenstackRepositoriesCommand))
        self.assertTrue(isinstance(repo_section.commands['copy'], images.ImageCopyCommand))
        self.assertTrue(isinstance(repo_section.commands['remove'], images.ImageRemoveCommand))

        upload_section = repo_section.subsections['uploads']
        self.assertTrue(isinstance(upload_section.commands['upload'], UploadOpenstackImageCommand))

        section = repo_section.subsections['publish']
        glance_section = section.subsections['http']
        self.assertTrue(isinstance(glance_section.commands['status'], PublishStatusCommand))
        self.assertTrue(isinstance(glance_section.commands['run'], RunPublishRepositoryCommand))

        section = repo_section.subsections['publish']
        glance_section = section.subsections['glance']
        self.assertTrue(isinstance(glance_section.commands['status'], PublishStatusCommand))
        self.assertTrue(isinstance(glance_section.commands['run'], RunPublishRepositoryCommand))
