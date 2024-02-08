# -*- coding: utf-8 -*-
from osv import osv
import netsvc
import base64

from som_ov_users.decorators import www_entry_point
from som_ov_users.exceptions import NoSuchUser
from exceptions import NoSuchInvoice, UnauthorizedAccess

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
                invoice_number=invoice.number,
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
            NoSuchInvoice,
            UnauthorizedAccess,
        )
    )
    def download_invoice_pdf(self, cursor, uid, vat, invoice_number, context=None):
        if context is None:
            context = {}

        users_obj = self.pool.get('som.ov.users')
        partner = users_obj.get_customer(cursor, uid, vat)
        invoice_obj = self.pool.get('giscere.facturacio.factura')
        search_params = [
            ('number', '=', invoice_number),
        ]

        invoice_id = invoice_obj.search(cursor, uid, search_params)
        if not invoice_id:
            raise NoSuchInvoice(invoice_number)

        invoice = invoice_obj.browse(cursor, uid, invoice_id)[0]

        if invoice.partner_id.id != partner.id:
            raise UnauthorizedAccess(
                username=vat,
                resource_type='Invoice',
                resource_name=invoice_number,
            )

        report_factura_obj = netsvc.LocalService('report.giscere.factura')
        result, result_format = report_factura_obj.create(cursor, uid, invoice_id, {})

        filename = (
            '{invoice_code}_{cil}.pdf'
        ).format(
            invoice_code=invoice.number,
            cil=invoice.cil_id.name,
        )

        return dict(
            content=base64.b64encode(result),
            filename=filename,
            content_type='application/{}'.format(result_format),
        )


SomOvInvoices()

