# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from destral import testing
from destral.transaction import Transaction

from .. import som_ov_installations


class SomInstallationsTests(testing.OOTestCase):

    def setUp(self):
        self.pool = self.openerp.pool
        self.imd = self.pool.get('ir.model.data')
        self.installation = self.pool.get('som.ov.installations')

        self.txn = Transaction().start(self.database)

        self.cursor = self.txn.cursor
        self.uid = self.txn.user
        self.maxDiff = None

    def tearDown(self):
        self.txn.stop()

    base_vat = 'ES48591264S'
    legal_vat = 'ESW2796397D'
    missing_vat = 'ES11111111H'
    no_contracts_vat = 'ES36464471H'
    no_installation_vat = 'TODO'
    no_coordinates__contract_number = '103'

    def test__get_installations__base(self):
        vat = self.base_vat

        result = self.installation.get_installations(self.cursor, self.uid, vat)

        expected_result = [
            dict(
                contract_number='103',
                installation_name='Installation 3',
            ),
        ]
        self.assertEqual(expected_result, result)

    def test__get_installations__multiple_installations(self):
        vat = self.legal_vat

        result = self.installation.get_installations(self.cursor, self.uid, vat)

        expected_result = [
            dict(
                contract_number='100',
                installation_name='Installation 0',
            ),
            dict(
                contract_number='101',
                installation_name='Installation 1',
            ),
            dict(
                contract_number='102',
                installation_name='Installation 2',
            ),
        ]
        self.assertEqual(expected_result, result)

    def test__get_installations__user_not_exists(self):
        vat = self.missing_vat

        result = self.installation.get_installations(self.cursor, self.uid, vat)

        self.assertEqual(result, dict(
            code='PartnerNotExists',
            error='Partner does not exist',
            trace=result.get('trace', "TRACE IS MISSING"),
        ))

    # def test__get_installations__user_inactive(self):

    def reference(self, module, id):
        return self.imd.get_object_reference(
            self.cursor, self.uid, module, id,
        )[1]

    def test__get_installations__user_have_not_installations(self):
        vat = self.legal_vat

        installation_obj = self.pool.get('giscere.instalacio')
        installation_id = self.reference('som_ov_installations', 'giscere_instalacio_1')

        installation_obj.unlink(self.cursor, self.uid, [installation_id])

        result = self.installation.get_installations(self.cursor, self.uid, vat)
        # TODO: Assert an error log has been generated
        self.assertEqual(result, [
            dict(
                contract_number='100',
                installation_name='Installation 0',
            ),
            # This is the one removed
            #dict(
            #    contract_number='101',
            #    installation_name='Installation 1',
            #),
            dict(
                contract_number='102',
                installation_name='Installation 2',
            ),
        ])

    def test__get_installations__contract_with_no_related_installation(self):
        vat = self.no_contracts_vat

        result = self.installation.get_installations(self.cursor, self.uid, vat)

        self.assertEqual(result, dict(
            code='InstallationsNotFound',
            error='No installations found for this partner',
            trace=result.get('trace', "TRACE IS MISSING"),
        ))

    def test__get_installation_details__base(self):
        contract_number = '101'

        result = self.installation.get_installation_details(self.cursor, self.uid, contract_number)

        expected_result = dict(
            installation_details=dict(
                contract_number='101',
                name = 'Installation 1',
                address = 'Carrer Buenaventura Durruti 2 aclaridor 08080 (Girona)',
                city = 'Girona',
                postal_code='08080',
                province='Girona',
                coordinates = '41.54670,0.80284',
                ministry_code = 'RE-00001',
                technology = False,
                cil='ES1234000000000001JK1F002',
                rated_power=801.0,
                type = 'IT-00001',
            ),
            contract_details=dict(
                billing_mode='index',
                proxy_fee=1.5,
                cost_deviation='included',
                reduction_deviation=100.0,
                representation_type='indirecta_cnmc',
                iban='**** **** **** **** **** 5257',
                discharge_date='2022-02-22',
                status='esborrany',
            ),
        )
        self.assertEqual(expected_result, result)

    def test__get_installation_details__contract_not_exists(self):
        contract_number = 'non_existing_contract_number'

        result = self.installation.get_installation_details(self.cursor, self.uid, contract_number)

        self.assertEqual(result['code'], 'ContractNotExists')
        self.assertEqual(result, dict(
            code='ContractNotExists',
            error='Contract does not exist',
            trace=result.get('trace', "TRACE IS MISSING"),
        ))

    def test__get_installation_details__contract_with_no_installation(self):
        installation_obj = self.pool.get('giscere.instalacio')
        installation_id = self.reference('som_ov_installations', 'giscere_instalacio_1')

        installation_obj.unlink(self.cursor, self.uid, [installation_id])

        contract_number = '101'

        result = self.installation.get_installation_details(self.cursor, self.uid, contract_number)

        self.assertEqual(result, dict(
            code='ContractWithoutInstallation',
            error="No installation found for contract '101'",
            contract_number='101',
            trace=result.get('trace', "TRACE IS MISSING"),
        ))

    def test__get_installation_details__coordinates_are_empty(self):
        contract_number = self.no_coordinates__contract_number

        result = self.installation.get_installation_details(self.cursor, self.uid, contract_number)

        expected_coordinates = None
        self.assertEqual(expected_coordinates, result['installation_details']['coordinates'])

    #def test_get_installation_details__other_people_installation
    #def test_get_installation_details__other_people_installation
    #def test_get_installations___inactive_contracts_included_same_installation
