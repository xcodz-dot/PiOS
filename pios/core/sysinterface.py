class CompatibilityError(Exception):
    pass


class CompatibilityMinimumVersionRequired(CompatibilityError):
    pass


class CompatibilityMaximumVersionRequired(CompatibilityError):
    pass


class InstallerError(Exception):
    pass


class InstallerScriptError(InstallerError):
    pass


class InstallerInvalidPackage(InstallerError):
    pass


class InstallerFileNotFound(InstallerError):
    pass


class InstallerUnknownPpkFormat(InstallerError):
    pass
