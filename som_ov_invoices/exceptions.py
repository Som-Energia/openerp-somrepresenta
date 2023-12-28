class SomInvoicesException(Exception):
    def __init__(self, text):
        self.exc_type = 'error'
        self.text = text
        super(SomInvoicesException, self).__init__(self.text)

    @property
    def code(self):
        return self.__class__.__name__

    def to_dict(self):
        return dict(
            code=self.code,
            error=self.text,
        )


class NoSuchInvoice(SomInvoicesException):
    def __init__(self, invoice_number):
        super(NoSuchInvoice, self).__init__(
            text="No invoice found with number '{}'".format(invoice_number))
        self.invoice_number = invoice_number

    def to_dict(self):
        return dict(
            super(NoSuchInvoice, self).to_dict(),
            invoice_number=self.invoice_number,
        )
