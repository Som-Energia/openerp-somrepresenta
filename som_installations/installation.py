# -*- coding: utf-8 -*-
from osv import osv

from som_users.decorators import www_entry_point
from som_users.exceptions import PartnerNotExists

from som_installations.exceptions import (
    InstallationNotFound,
    InstallationsNotFound,
    ContractNotExists
)


class Installation(osv.osv_memory):

    _name = 'installation'

    @www_entry_point(
        expected_exceptions=(
            PartnerNotExists,
            InstallationsNotFound,
            InstallationNotFound,
            ContractNotExists
        )
    )
    def get_installations(self, cursor, uid, vat):
        users_obj = self.pool.get('users')
        partner = users_obj.get_customer(cursor, uid, vat)
        installation_obj = self.pool.get('giscere.instalacio')
        search_params = [
           ('titular','=', partner.id),
        ]
        installation_ids = installation_obj.search(cursor, uid, search_params)
        if not installation_ids:
            raise InstallationsNotFound()

        installations = installation_obj.browse(cursor, uid, installation_ids)

        return [
            dict(
                contract_number=self._get_contract_number(cursor, uid, partner.id),
                installation_name=installation.name,
            )
            for installation in installations
        ]

    @www_entry_point(
        expected_exceptions=(
            InstallationNotFound,
            ContractNotExists
        )
    )
    def get_installation_details(self, cursor, uid, installation_name):
        installation_obj = self.pool.get('giscere.instalacio')
        installation_search_params = [
           ('name','=', installation_name),
        ]
        installation_id = installation_obj.search(cursor, uid, installation_search_params)
        if not installation_id:
            raise InstallationNotFound()

        installation = installation_obj.browse(cursor, uid, installation_id)[0]
        installation_details = dict(
            contract_number=self._get_contract_number(cursor, uid, installation.titular.id),
            name=installation.name,
            address=installation.cil.direccio,
            city=installation.cil.id_municipi.name,
            postal_code=installation.cil.dp,
            province=installation.cil.id_provincia.name,
            coordinates=installation.utm_x.replace(',', '.') + ',' + installation.utm_y.replace(',', '.') if installation.utm_x and installation.utm_y else False,
            technology=installation.tecnologia,
            cil=installation.cil.name,
            rated_power=installation.potencia_nominal,
            type=installation.tipo,
            ministry_code=installation.codigo_ministerio,
        )

        polissa_obj = self.pool.get('giscere.polissa')
        contract_search_params = [
           ('name','=', self._get_contract_number(cursor, uid, installation.titular.id)),
        ]
        contract_id = polissa_obj.search(cursor, uid, contract_search_params)
        if not contract_id:
            raise ContractNotExists()

        contract = polissa_obj.browse(cursor, uid, contract_id)[0]
        contract_details = dict(
            billing_mode=contract.mode_facturacio,
            proxy_fee=contract.representant_fee,
            cost_deviation=contract.desvios,
            reduction_deviation=contract.efecte_cartera,
            representation_type=contract.representation_type,
            iban=self._format_iban(contract.bank.printable_iban),
            discharge_date=contract.data_alta,
            status=contract.state,
        )

        return dict(
            installation_details=installation_details,
            contract_details=contract_details
        )

    def _format_iban(self, iban):
        """Hide all but the last 4 digits of an IBAN number"""
        return '**** **** **** **** **** {}'.format(iban[-4:])

    def _get_contract_number(self, cursor, uid, partner_id):
        polissa_obj = self.pool.get('giscere.polissa')
        search_params = [
           ('titular','=', partner_id),
        ]
        contract_id = polissa_obj.search(cursor, uid, search_params)
        if not contract_id:
            raise ContractNotExists()
        contract = polissa_obj.browse(cursor, uid, contract_id)[0]
        return contract.name


Installation()
