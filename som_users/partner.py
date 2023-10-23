# -*- coding: utf-8 -*-
from osv import osv

class Partner(osv.osv):

    _name = 'partner'
    _inherit = 'res.partner'

    def get_partner(self, cursor, uid, cif):
        partner_obj = self.pool.get('res.partner')
        search_params = [('nif','=', cif)]
        partner_id = partner_obj.search(cursor, uid, search_params)

        if partner_id:
            partner = partner_obj.read(cursor, uid, partner_id)   
            return partner
        return 'User not found'

Partner()