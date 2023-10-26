# -*- coding: utf-8 -*-
from osv import osv

class Partner(osv.osv):

    _name = 'partner'
    _inherit = 'res.partner'

    def get_partner(self, cursor, uid, cif):
        partner_obj = self.pool.get('res.partner')
        search_params = [('vat','=', cif)]
        partner_id = partner_obj.search(cursor, uid, search_params)
        if partner_id:
            partner = partner_obj.browse(cursor, uid, partner_id)
            return dict(
                nif=str(partner[0].vat),
                name=str(partner[0].name),
                email=str(partner[0].address[0].email) if partner[0].address else '',
                roles=dict(
                    costumer=partner[0].customer)
            )
        return None

Partner()