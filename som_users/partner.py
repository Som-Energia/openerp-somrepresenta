# -*- coding: utf-8 -*-
from osv import osv

from som_users.decorators import www_entry_point
from som_users.exceptions import PartnerNotExists


class Partner(osv.osv):

    _name = 'partner'
    _inherit = 'res.partner'


    @www_entry_point(
        expected_exceptions=PartnerNotExists
    )
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
        raise PartnerNotExists()

    def get_profile(self, cursor, uid, nif):
        partner_obj = self.pool.get('res.partner')

        search_params = [
           ('vat','=', nif),
           ('active','=', True)
        ]
        partner_id = partner_obj.search(cursor, uid, search_params)
        if partner_id:
            partner = partner_obj.browse(cursor, uid, partner_id)[0]

            return dict(
               nif=str(partner.vat),
               address=str(partner.address[0].street),
               city=str(partner.address[0].city),
               zip=str(partner.address[0].zip),
               state=str(partner.address[0].state_id.name),
               phone=str(partner.address[0].phone),
               roles=dict(
                   customer=partner.customer)
           )
        return dict()


Partner()
