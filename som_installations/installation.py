# -*- coding: utf-8 -*-
from osv import osv

from som_users.decorators import www_entry_point

from som_users.exceptions import PartnerNotExists

from som_installations.exceptions import InstallationsNotExists, PolissaNotExists


class Installation(osv.osv):

    _name = 'installation'

    @www_entry_point(
        expected_exceptions=PartnerNotExists
    )
    def get_installations_by(self, cursor, uid, vat):
        partner_obj = self.pool.get('res.partner')
        search_params = [
           ('vat','=', vat),
           ('active','=', True),
           ('customer','=', True),
        ]
        partner_id = partner_obj.search(cursor, uid, search_params)
        if not partner_id:
            raise PartnerNotExists()

        installation_obj = self.pool.get('giscere.instalacio')
        search_params = [
           ('titular','=', partner_id[0]),
        ]
        installation_ids = installation_obj.search(cursor, uid, search_params)
        if not installation_ids:
            raise InstallationsNotExists()

        installations = [
            installation_obj.browse(cursor, uid, installation_id)[0]
            for installation_id in installation_ids
        ]

        return [
            dict(
                contract_number=self._get_contract_number_by(installation.titular),
                installation_name=installation.name,
            )
            for installation in installations
        ]


    def _get_contract_number_by(self, cursor, uid, partner_id):
        polissa_obj = self.pool.get('giscere.polissa')
        search_params = [
           ('titular','=', partner_id),
        ]
        polissa_id = polissa_obj.search(cursor, uid, search_params)
        if not polissa_id:
            raise PolissaNotExists()

        polissa = polissa_obj.browse(cursor, uid, polissa_id)[0]

        return polissa.id


Installation()
