# -*- coding: utf-8 -*-
from destral import testing
from destral.transaction import Transaction

class SomUsersTests(testing.OOTestCase):

    def setUp(self):
        self.pool = self.openerp.pool
        self.imd = self.pool.get('ir.model.data')
        self.partner = self.pool.get('res.partner')

        self.txn = Transaction().start(self.database)

        self.cursor = self.txn.cursor
        self.uid = self.txn.user

    def tearDown(self):
        self.txn.stop()

    def test__get_partner__user_exists(self):

        partner_id = self.imd.get_object_reference(
            self.cursor, self.uid, 'base', 'res_partner_asus'
        )[1]

        expected_partner_cif = self.partner.read(
            self.cursor, self.uid, partner_id,['cif']
        )['cif']

        partner = self.partner.get_partner(self.cursor, self.uid, 123)
        partner_cif = partner['cif']

        self.assertEqual(expected_partner_cif, partner_cif)