"""Custom exceptions."""


class ServerTokenError(Exception):
    pass


class UnsetServerToken(Exception):
    pass


class InvalidEnvironment(Exception):
    pass
