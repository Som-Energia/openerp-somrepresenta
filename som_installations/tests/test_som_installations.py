# -*- coding: utf-8 -*-
from destral import testing
from destral.transaction import Transaction

from .. import installation


class SomInstallationsTests(testing.OOTestCase):

    def setUp(self):
        self.pool = self.openerp.pool
        self.imd = self.pool.get('ir.model.data')
        self.installation = self.pool.get('installation')

        self.txn = Transaction().start(self.database)

        self.cursor = self.txn.cursor
        self.uid = self.txn.user
        self.maxDiff = None

    def tearDown(self):
        self.txn.stop()

    def test__get_installations_by__user_exists_is_active_and_have_installations(self):
        a_partner_vat = 'ES48591264S'

        result = self.installation.get_installations_by(self.cursor, self.uid, a_partner_vat)

        expected_result = [
            dict(
                contract_number='000',
                installation_name='Installation 0',
            ),
            dict(
                contract_number='000',
                installation_name='Installation 1',
            ),
        ]
        self.assertEqual(expected_result, result)

    def test__get_installations_by__user_not_exists(self):
        an_invalid_partner_vat = 123

        result = self.installation.get_installations_by(self.cursor, self.uid, an_invalid_partner_vat)

        self.assertEqual(result['code'], 'PartnerNotExists')
