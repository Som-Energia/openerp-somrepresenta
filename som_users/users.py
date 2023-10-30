# -*- coding: utf-8 -*-
from osv import osv

from som_users.decorators import www_entry_point
from som_users.exceptions import PartnerNotExists


class Users(osv.osv_memory):

    _name = "users"

    @www_entry_point(
        expected_exceptions=PartnerNotExists
    )
    def get_partner_info(self, cursor, uid, nif):
        partner_obj = self.pool.get('res.partner')
        search_params = [
            ('vat','=', nif),
            ('active','=', True)
        ]
        partner_id = partner_obj.search(cursor, uid, search_params)
        if partner_id:
            partner = partner_obj.browse(cursor, uid, partner_id)[0]

            return dict(
                nif=partner.vat,
                name=partner.name,
                email=partner.address[0].email,
                roles=dict(
                    customer=partner.customer)
            )
        raise PartnerNotExists()

    def get_partner_profile(self, cursor, uid, nif):
        partner_obj = self.pool.get('res.partner')
        search_params = [
           ('vat','=', nif),
           ('active','=', True)
        ]
        partner_id = partner_obj.search(cursor, uid, search_params)
        if partner_id:
            partner = partner_obj.browse(cursor, uid, partner_id)[0]

            return dict(
               nif=partner.vat,
               address=partner.address[0].street,
               city=partner.address[0].city,
               zip=partner.address[0].zip,
               state=partner.address[0].state_id.name,
               phone=dict(
                   landline=partner.address[0].phone,
                   mobile=partner.address[0].mobile,
               ),
               roles=dict(
                   customer=partner.customer)
           )
        return dict()


Users()
