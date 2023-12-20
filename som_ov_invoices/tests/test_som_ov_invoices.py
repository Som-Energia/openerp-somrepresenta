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
    base_invoice = 'Proforma Test invoice 0'

    def test__get_invoices__base(self):
        vat = self.base_vat

        result = self.invoice.get_invoices(self.cursor, self.uid, vat)

        expected_result = [
            dict(
                contract_number='103',
                invoice_number='Factura 0',
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

    def test__download_invoice_pdf__ok(self):
        vat = self.base_vat
        invoice_number = self.base_invoice

        result = self.invoice.download_invoice_pdf(self.cursor, self.uid, vat, invoice_number)

        self.assertEqual(result['filename'], 'invoice_{}_pdf'.format(invoice_number))
        self.assertEqual(result['content_type'], 'application/pdf')


