import os
import shutil
import tempfile
import unittest

from mock import Mock, patch

from pulp.devel.unit.util import touch

from pulp.plugins.conduits.repo_publish import RepoPublishConduit
from pulp.plugins.config import PluginCallConfiguration
from pulp.plugins.model import Repository
from pulp.plugins.util.publish_step import PublishStep

from pulp_openstack.common import constants
from pulp_openstack.plugins.distributors import publish_steps


class TestPublishImagesStep(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.working_directory = os.path.join(self.temp_dir, 'working')
        self.publish_directory = os.path.join(self.temp_dir, 'publish')
        self.content_directory = os.path.join(self.temp_dir, 'content')
        os.makedirs(self.working_directory)
        os.makedirs(self.publish_directory)
        os.makedirs(self.content_directory)
        repo = Repository('foo_repo_id', working_dir=self.working_directory)
        config = PluginCallConfiguration(None, None)
        conduit = RepoPublishConduit(repo.id, 'foo_repo')
        self.parent = PublishStep('test-step', repo, conduit, config)

    def tearDown(self):
        shutil.rmtree(self.working_directory)

    def test_process_unit(self):
        step = publish_steps.PublishImagesStep()
        fake_image_filename = 'fake-zero-byte-image.qcow2'
        touch(os.path.join(self.content_directory, fake_image_filename))
        unit = Mock(unit_key={'image_checksum': 'd41d8cd98f00b204e9800998ecf8427e'},
                    storage_path=os.path.join(self.content_directory, fake_image_filename))
        step.get_working_dir = Mock(return_value=self.publish_directory)
        step.process_unit(unit)
        # verify symlink
        expected_symlink = os.path.join(self.publish_directory, 'web', fake_image_filename)
        self.assertTrue(os.path.exists(expected_symlink))

    def test_finalize(self):
        step = publish_steps.PublishImagesStep()
        step.redirect_context = Mock()
        step.finalize()
        step.redirect_context.finalize.assert_called_once_with()


class TestWebPublisher(unittest.TestCase):

    def setUp(self):
        self.working_directory = tempfile.mkdtemp()
        self.publish_dir = os.path.join(self.working_directory, 'publish')
        self.master_dir = os.path.join(self.working_directory, 'master')
        self.working_temp = os.path.join(self.working_directory, 'work')
        self.repo = Mock(id='foo', working_dir=self.working_temp)

    def tearDown(self):
        shutil.rmtree(self.working_directory)

    @patch('pulp.plugins.util.publish_step.common_utils.get_working_directory')
    @patch('pulp_openstack.plugins.distributors.publish_steps.AtomicDirectoryPublishStep')
    @patch('pulp_openstack.plugins.distributors.publish_steps.PublishImagesStep')
    def test_init(self, mock_images_step, mock_web_publish_step, get_working_directory):
        mock_conduit = Mock()
        mock_config = {
            constants.CONFIG_KEY_GLANCE_PUBLISH_DIRECTORY: self.publish_dir
        }

        publisher = publish_steps.WebPublisher(self.repo, mock_conduit, mock_config)

        self.assertEquals(publisher.children, [mock_images_step.return_value,
                                               mock_web_publish_step.return_value])
        get_working_directory.assert_called_once_with()
