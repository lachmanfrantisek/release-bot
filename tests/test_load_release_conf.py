# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from release_bot.configuration import configuration
from pathlib import Path
import pytest


class TestLoadReleaseConf:

    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        configuration.set_logging(level=10)
        configuration.debug = True

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """

    @pytest.fixture
    def empty_conf(self, tmpdir):
        conf = Path(str(tmpdir))/"relase-conf.yaml"
        conf.touch()
        return str(tmpdir)

    @pytest.fixture
    def non_existing_conf(self, tmpdir):
        return str(tmpdir)

    @pytest.fixture
    def valid_new_release(self):
        new_release = {'version': '0.1.0',
                       'commitish': 'xxx',
                       'author_name': 'John Doe',
                       'author_email': 'jdoe@example.com',
                       'python_versions': [],
                       'fedora': False,
                       'fedora_branches': [],
                       'changelog': [],
                       'fs_path': '',
                       'tempdir': None}
        return new_release

    @pytest.fixture
    def missing_items_conf(self, tmpdir):
        conf_content = (Path(__file__).parent/"src/missing_items_conf.yaml").read_text()
        conf = Path(str(tmpdir))/"release-conf.yaml"
        conf.write_text(conf_content)
        return str(tmpdir)

    @pytest.fixture
    def missing_author_conf(self, tmpdir):
        conf_content = (Path(__file__).parent/"src/missing_author.yaml").read_text()
        conf = Path(str(tmpdir))/"release-conf.yaml"
        conf.write_text(conf_content)
        return str(tmpdir)

    @pytest.fixture
    def valid_conf(self, tmpdir):
        conf_content = (Path(__file__).parent/"src/release-conf.yaml").read_text()
        conf = Path(str(tmpdir))/"release-conf.yaml"
        conf.write_text(conf_content)
        return str(tmpdir)

    def test_empty_conf(self, empty_conf):
        # if there are any required items, this test must fail
        if configuration.REQUIRED_ITEMS['release-conf']:
            with pytest.raises(SystemExit) as error:
                configuration.load_release_conf(empty_conf)
            assert error.type == SystemExit
            assert error.value.code == 1

    def test_non_exiting_conf(self, non_existing_conf):
        with pytest.raises(SystemExit) as error:
            configuration.load_release_conf(non_existing_conf)
        assert error.type == SystemExit
        assert error.value.code == 1

    def test_missing_required_items(self, missing_items_conf):
        # set python_versions as required
        configuration.REQUIRED_ITEMS['release_conf'] = ['python_versions']
        with pytest.raises(SystemExit) as error:
            configuration.load_release_conf(missing_items_conf)
        assert error.type == SystemExit
        assert error.value.code == 1

    def test_author_overwrites(self, missing_author_conf, valid_new_release):
        author_name = valid_new_release['author_name']
        author_email = valid_new_release['author_email']

        release_conf = configuration.load_release_conf(missing_author_conf)
        valid_new_release.update(release_conf)

        assert valid_new_release['author_name'] == author_name
        assert valid_new_release['author_email'] == author_email

    def test_fedora_disabling(self, valid_conf, valid_new_release):
        # fas_username is empty
        release_conf = configuration.load_release_conf(valid_conf)
        valid_new_release.update(release_conf)
        assert valid_new_release['fedora'] is False

    def test_normal_use_case(self, valid_conf, valid_new_release):
        # set fas_username because without it, fedora releasing will be disabled
        configuration.fas_username = 'test'
        # test if all items in configuration are properly loaded
        release_conf = configuration.load_release_conf(valid_conf)
        valid_new_release.update(release_conf)
        # this assertion also tests if versions are correct data type
        assert valid_new_release['python_versions'] == [2, 3]
        assert valid_new_release['changelog'] == ['Example changelog entry',
                                                  'Another changelog entry']
        assert valid_new_release['author_name'] == 'John Smith'
        assert valid_new_release['author_email'] == 'jsmith@example.com'
        assert valid_new_release['fedora'] is True
        # this assertion also tests if branches are correct data type
        assert valid_new_release['fedora_branches'] == ['f27', 'f28', '13']
