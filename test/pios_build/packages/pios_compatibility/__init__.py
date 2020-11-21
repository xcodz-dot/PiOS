from packaging.version import Version

from pios import __version__ as pios_version
from pios.core import sysinterface


def minimum_required(version: str):
    if Version(version) > Version(pios_version):
        raise sysinterface.CompatibilityMinimumVersionRequired(version)


def maximum_required(version: str):
    if Version(version) < Version(pios_version):
        raise sysinterface.CompatibilityMaximumVersionRequired(version)


class PiOSVersionGroup:
    def __init__(self, *args):
        self.versions = [Version(x) for x in args]
        self.pios_version = Version(pios_version)
        self.e = True in [pios_version == x for x in self.versions]

    def __bool__(self):
        return self.e


class PiOS:
    def __init__(self, version: str):
        self.version = Version(version)
        self.pios_version = Version(pios_version)
        self.e = version == pios_version

    def __bool__(self):
        return self.e


class PiOSMinimum:
    def __init__(self, version: str):
        self.version = Version(version)
        self.pios_version = Version(pios_version)
        self.e = version >= pios_version

    def __bool__(self):
        return self.e


class PiOSMaximum:
    def __init__(self, version: str):
        self.version = Version(version)
        self.pios_version = Version(pios_version)
        self.e = version <= pios_version

    def __bool__(self):
        return self.e
