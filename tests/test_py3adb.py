import pytest
import os
from pathlib import Path

import py3adb
from py3adb import ADB


@pytest.fixture(scope='module')
def adb_executable():
    """
    Default ADB executable location in Linux

    :return: Location of default ADB executable if there
    """
    file_location = '/usr/bin/adb'
    if not os.path.isfile(file_location):
        return None
    return file_location


@pytest.mark.usefixtures('tmpdir')
@pytest.fixture(scope='function')
def fake_adb_executable(tmpdir):
    """
    Generates a fake executable used for mocking

    :param tmpdir:
    :return: Executable Path
    """
    executable = os.path.join(tmpdir, 'adb')
    Path(executable).touch(mode=0o666, exist_ok=True)
    yield executable


@pytest.mark.usefixtures('adb_executable')
def test_instantiation(adb_executable):
    """
    Just make sure that we can instantiate the ADB object
    :return: None
    """
    try:
        adb = ADB(adb_executable)  # noqa: W0612
    except:  # noqa
        pytest.fail("No failure should be raised")


@pytest.mark.usefixtures('fake_adb_executable')
def test_pyadb_version(fake_adb_executable):
    """
    Ensures the version in the Class ADB is the same as the package

    :param fake_adb_executable: A fake executable location
    :return: None
    """
    adb = ADB(fake_adb_executable)
    assert adb.pyadb_version() == py3adb.__version__
