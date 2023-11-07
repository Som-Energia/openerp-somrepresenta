# -*- coding: utf-8 -*-
from osv import osv

from som_users.decorators import www_entry_point
from som_users.exceptions import PartnerNotExists


class Users(osv.osv_memory):

    _name = "users"

    @www_entry_point(
        expected_exceptions=PartnerNotExists
    )
    def identify_login(self, cursor, uid, login):
        #TODO: get res.users login info
        partner_obj = self.pool.get('res.partner')
        search_params = [
            ('vat','=', login),
            ('active','=', True),
            ('customer','=', True)
        ]
        partner_id = partner_obj.search(cursor, uid, search_params)
        if partner_id:
            partner = partner_obj.browse(cursor, uid, partner_id)[0]

            return dict(
                vat=partner.vat,
                name=partner.name,
                email=partner.address[0].email,
                roles=['customer'],
                username=partner.vat,
            )
        raise PartnerNotExists()

    @www_entry_point(
        expected_exceptions=PartnerNotExists
    )
    def get_profile(self, cursor, uid, username):
        # Get user profile: for now recover customer profile
        partner_obj = self.pool.get('res.partner')
        search_params = [
           ('vat','=', username),
           ('active','=', True),
           ('customer','=', True),
        ]
        partner_id = partner_obj.search(cursor, uid, search_params)
        if not partner_id:
            raise PartnerNotExists()

        partner = partner_obj.browse(cursor, uid, partner_id)[0]

        return dict(
            username=partner.vat,
            roles=['customer'],
            vat=partner.vat,
            name=partner.name,
            email=partner.address[0].email,
            address=partner.address[0].street,
            city=partner.address[0].city,
            zip=partner.address[0].zip,
            state=partner.address[0].state_id.name,
            phones=[
                partner.address[0][key]
                for key in ['phone', 'mobile']
                if partner.address[0][key]
            ],
            proxy_vat=partner.representante_id.vat if partner.representante_id else False,
            proxy_name=partner.representante_id.name if partner.representante_id else False,
        )


Users()
