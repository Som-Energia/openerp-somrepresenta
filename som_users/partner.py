# -*- coding: utf-8 -*-
from osv import osv


class Partner(osv.osv):

    _name = 'partner'
    _inherit = 'res.partner'

    def get_partner(self, cursor, uid, cif):
        partner_obj = self.pool.get('res.partner')
        search_params = [
            ('vat','=', cif),
            ('active','=', True)
        ]
        partner_id = partner_obj.search(cursor, uid, search_params)
        if partner_id:
            partner = partner_obj.browse(cursor, uid, partner_id)[0]

            return dict(
                nif=str(partner.vat),
                name=str(partner.name),
                email=str(partner.address[0].email),
                roles=dict(
                    costumer=partner.customer)
            )
        return dict()


Partner()
