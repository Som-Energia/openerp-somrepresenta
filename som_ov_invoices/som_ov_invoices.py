# -*- coding: utf-8 -*-
from osv import osv
import netsvc
import base64
import zipfile
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

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
           ('state', 'in', ['open', 'paid']),
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
                payment_status=invoice.state,
                liquidation=None,
            )
            for invoice in invoices
        ]

    def validate_invoices(self, cursor, uid, vat, invoice_numbers):
        users_obj = self.pool.get('som.ov.users')
        partner = users_obj.get_customer(cursor, uid, vat)
        invoice_obj = self.pool.get('giscere.facturacio.factura')
        search_params = [
            ('number', 'in', invoice_numbers),
        ]

        invoice_ids = invoice_obj.search(cursor, uid, search_params)

        for invoice_id in invoice_ids:
            invoice = invoice_obj.browse(cursor, uid, invoice_id)

            if invoice.partner_id.id != partner.id:
                raise UnauthorizedAccess(
                    username=vat,
                    resource_type='Invoice',
                    resource_name=invoice.number,
                )
        return invoice_ids

    def do_invoice_pdf(self, cursor, uid, report_factura_obj, invoice_id):
        invoice_obj = self.pool.get('giscere.facturacio.factura')

        invoice = invoice_obj.browse(cursor, uid, invoice_id)

        result, result_format = report_factura_obj.create(cursor, uid, invoice.id, {})

        filename = (
            '{invoice_code}_{cil}.pdf'
        ).format(
            invoice_code=invoice.number,
            cil=invoice.cil_id.name,
        )

        return result, result_format, filename

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

        invoice_id = self.validate_invoices(cursor, uid, vat, [invoice_number])

        if not invoice_id:
            raise NoSuchInvoice(invoice_number)

        report_factura_obj = netsvc.LocalService('report.giscere.factura')

        result, result_format, filename = self.do_invoice_pdf(cursor, uid, report_factura_obj, invoice_id)

        return dict(
            content=base64.b64encode(result),
            filename=filename,
            content_type='application/{}'.format(result_format),
        )

    @www_entry_point(
        expected_exceptions=(
            NoSuchUser,
            UnauthorizedAccess,
        )
    )
    def download_invoices_zip(self, cursor, uid, vat, invoice_numbers, context=None):
        if context is None:
            context = {}

        invoice_ids = self.validate_invoices(cursor, uid, vat, invoice_numbers)

        report_factura_obj = netsvc.LocalService('report.giscere.factura')

        zipfile_io = StringIO.StringIO()
        zipfile_ = zipfile.ZipFile(
            zipfile_io, 'w', compression=zipfile.ZIP_DEFLATED
        )

        for invoice_id in invoice_ids:
            result, result_format, filename = self.do_invoice_pdf(cursor, uid, report_factura_obj, invoice_id)
            zipfile_.writestr(filename, result)

        zipfile_.close()

        return dict(
            content=base64.b64encode(zipfile_io.getvalue()),
            filename='{}_invoices_from_{}.zip'.format(vat, invoice_numbers[0]),
            content_type='application/{}'.format(result_format),
        )

SomOvInvoices()
