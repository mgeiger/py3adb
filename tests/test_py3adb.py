from py3adb import ADB
import pytest
import os


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


@pytest.mark.usefixtures('adb_executable')
def test_instantiation(adb_executable):
    """
    Just make sure that we can instantiate the ADB object
    :return:
    """
    adb = ADB(adb_executable)


