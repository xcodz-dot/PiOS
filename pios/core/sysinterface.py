class CompatibilityError(Exception):
    pass


class CompatibilityMinimumVersionRequired(CompatibilityError):
    pass


class CompatibilityMaximumVersionRequired(CompatibilityError):
    pass
