class SomUsersException(Exception):
    def __init__(self, text, message=None):
        self.exc_type = 'error'
        self.text = text
        self.message = message
        super(SomUsersException, self).__init__(self.text)

    @property
    def code(self):
        return self.__class__.__name__

    def to_dict(self):
        return dict(
            code=self.code,
            error=self.text,
            message=self.message
        )


class PartnerNotExists(SomUsersException):
    def __init__(self):
        super(PartnerNotExists, self).__init__(
            text="Partner does not exist"
        )

class NoDocumentVersions(SomUsersException):
    def __init__(self, document):
        super(NoDocumentVersions, self).__init__(
            text="Document {} has no version available to sign".format(document)
            text="Partner does not exist")

class FailSendEmail(SomUsersException):
    def __init__(self, message):
        super(FailSendEmail, self).__init__(
            text="Error sending email",
            message=message
        )
