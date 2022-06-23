class ObjectAlreadyExists(Exception):
    pass

class ValidationError(Exception):
    pass

class IncorrectPasswordScheme(Exception):
    pass

class CredentialsError(Exception):
    pass

class NotAuthenticatedError(Exception):
    pass