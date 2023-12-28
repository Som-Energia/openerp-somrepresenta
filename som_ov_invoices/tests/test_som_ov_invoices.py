# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from destral import testing
from destral.transaction import Transaction

from .. import som_ov_invoices


class SomOvInvoicesTests(testing.OOTestCase):

    def setUp(self):
        self.pool = self.openerp.pool
        self.imd = self.pool.get('ir.model.data')
        self.invoice = self.pool.get('som.ov.invoices')

        self.txn = Transaction().start(self.database)

        self.cursor = self.txn.cursor
        self.uid = self.txn.user

    def tearDown(self):
        self.txn.stop()

    base_vat = 'ES48591264S'
    legal_vat = 'ESW2796397D'
    base_invoice = 'F0'
    missing_vat = 'ES11111111H'

    def test__get_invoices__base(self):
        vat = self.base_vat

        result = self.invoice.get_invoices(self.cursor, self.uid, vat)

        expected_result = [
            dict(
                contract_number='103',
                invoice_number='F0',
                concept='market',
                emission_date='2022-10-31',
                first_period_date='2022-10-01',
                last_period_date='2022-10-31',
                amount=28.77,
                liquidation=None,
            ),
        ]
        self.assertEqual(expected_result, result)

    def test__get_invoices__no_draft(self):
        vat = self.legal_vat

        result = self.invoice.get_invoices(self.cursor, self.uid, vat)

        self.assertEqual(result, [])

    def test__get_invoices__user_not_exists(self):
        vat = self.missing_vat

        result = self.invoice.get_invoices(self.cursor, self.uid, vat)

        self.assertEqual(result, dict(
            code='NoSuchUser',
            error='User does not exist',
            trace=result.get('trace', "TRACE IS MISSING"),
        ))

    def test__download_invoice_pdf__user_not_exists(self):
        vat = self.missing_vat
        invoice_number = self.base_invoice

        result = self.invoice.download_invoice_pdf(self.cursor, self.uid, vat, invoice_number)

        self.assertEqual(result, dict(
            code='NoSuchUser',
            error='User does not exist',
            trace=result.get('trace', "TRACE IS MISSING"),
        ))

    def test__download_invoice_pdf__not_such_invoice_for_vat(self):
        vat = self.legal_vat
        invoice_number = 'No such invoice'

        result = self.invoice.download_invoice_pdf(self.cursor, self.uid, vat, invoice_number)

        self.assertEqual(result, dict(
            code='NoSuchInvoice',
            error="No invoice found with number 'No such invoice'",
            invoice_number='No such invoice',
            trace=result.get('trace', "TRACE IS MISSING"),
        ))

    def test__download_invoice_pdf__ok(self):
        vat = self.base_vat
        invoice_number = self.base_invoice

        result = self.invoice.download_invoice_pdf(self.cursor, self.uid, vat, invoice_number)

        self.assertEqual(result['filename'], 'factura-F0-20221031-103-market-20221001-20221031.pdf')
        self.assertEqual(result['content_type'], 'application/pdf')

