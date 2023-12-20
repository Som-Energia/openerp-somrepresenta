# -*- coding: utf-8 -*-
from osv import osv
import netsvc
import base64
from som_ov_users.decorators import www_entry_point
from som_ov_users.exceptions import NoSuchUser

class SomOvInvoices(osv.osv_memory):

    _name = 'som.ov.invoices'
    
    CONCEPT_TYPE = {
        '01': 'market',
        '02': 'specific_retribution', 
        '03': 'services',
    }

    @www_entry_point(
        expected_exceptions=(
            NoSuchUser,
        )
    )
    def get_invoices(self, cursor, uid, vat, context=None):
        if context is None:
            context = {}

        users_obj = self.pool.get('som.ov.users')
        partner = users_obj.get_customer(cursor, uid, vat)
        invoice_obj = self.pool.get('giscere.facturacio.factura')

        search_params = [
           ('partner_id','=', partner.id),
           ('state', '!=', 'draft'),
        ]

        invoice_ids = invoice_obj.search(cursor, uid, search_params)

        invoices = invoice_obj.browse(cursor, uid, invoice_ids)
        return [
            dict(
                contract_number=invoice.polissa_id.name,
                invoice_number=invoice.name,
                concept=self.CONCEPT_TYPE[invoice.tipo_factura],
                emission_date=invoice.date_invoice,
                first_period_date=invoice.data_inici,
                last_period_date=invoice.data_final,
                amount=invoice.amount_total,  
                liquidation=None,
            )
            for invoice in invoices
        ]

    @www_entry_point(
        expected_exceptions=(
            NoSuchUser,
        )
    )
    def download_invoice_pdf(self, cursor, uid, vat, invoice_number, context=None):
        if context is None:
            context = {}

        users_obj = self.pool.get('som.ov.users')
        partner = users_obj.get_customer(cursor, uid, vat)
        invoice_obj = self.pool.get('giscere.facturacio.factura')
        search_params = [
            ('partner_id','=', partner.id),
            ('name', '=', invoice_number),
        ]

        invoice_id = invoice_obj.search(cursor, uid, search_params)
        invoice = invoice_obj.browse(cursor, uid, invoice_id)

        report_factura_obj = netsvc.LocalService('report.giscere.factura')
        result, result_format = report_factura_obj.create(cursor, uid, invoice_id, {})

        return dict(
            content = base64.b64encode(result),
            filename = 'invoice_{}_pdf'.format(invoice.name),
            content_type = 'application/{}'.format(result_format),
        )

SomOvInvoices()