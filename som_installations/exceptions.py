class SomInstallationsException(Exception):
    def __init__(self, text):
        self.exc_type = 'error'
        self.text = text

    @property
    def code(self):
        return self.__class__.__name__

    def to_dict(self):
        return dict(
            code=self.code,
            error=self.text,
        )


class InstallationsNotExists(SomInstallationsException):
    def __init__(self):
        super(InstallationsNotExists, self).__init__(
            text="Installations does not exist")


class PolissaNotExists(SomInstallationsException):
    def __init__(self):
        super(PolissaNotExists, self).__init__(
            text="Polissa does not exist")
