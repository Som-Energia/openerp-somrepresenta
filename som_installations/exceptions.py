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


class InstallationsNotFound(SomInstallationsException):
    def __init__(self):
        super(InstallationsNotFound, self).__init__(
            text="No installations found for this partner")


class InstallationNotFound(SomInstallationsException):
    def __init__(self):
        super(InstallationNotFound, self).__init__(
            text="The requested installation does not exist")


class ContractNotExists(SomInstallationsException):
    def __init__(self):
        super(ContractNotExists, self).__init__(
            text="Contract does not exist")
