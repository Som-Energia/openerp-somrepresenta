# -*- coding: utf-8 -*-
from destral import testing
from destral.transaction import Transaction

from .. import partner

class SomUsersTests(testing.OOTestCase):

    def setUp(self):
        self.pool = self.openerp.pool
        self.imd = self.pool.get('ir.model.data')
        self.res_partner = self.pool.get('res.partner')
        self.partner = self.pool.get('partner')

        self.txn = Transaction().start(self.database)

        self.cursor = self.txn.cursor
        self.uid = self.txn.user

    def tearDown(self):
        self.txn.stop()

    def test__get_partner__user_exists_and_is_active(self):
        res_partner_address_soci_vat = '48591264S'

        result = self.partner.get_partner(self.cursor, self.uid, res_partner_address_soci_vat)

        expected_result = dict(
            nif='48591264S',
            name='Benedetti, Mario',
            email='test@test.test',
            roles=dict(
                costumer=True)
        )
        self.assertEqual(expected_result, result)
