class BaseDomainException(Exception):
    pass


class NoActivityFound(BaseDomainException):
    pass


class ActivityAlreadyHasDescription(BaseDomainException):
    def __init__(self, activity_id: int, description: str) -> None:
        self.activity_id = activity_id
        self.description = description


class StravaAuthenticationError(BaseDomainException):
    pass


class StravaApiError(BaseDomainException):
    pass
