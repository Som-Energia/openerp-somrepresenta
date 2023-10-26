class SomUsersException(Exception):
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


class PartnerNotExists(SomUsersException):
    def __init__(self):
        super(PartnerNotExists, self).__init__(
            text="Partner does not exist")
