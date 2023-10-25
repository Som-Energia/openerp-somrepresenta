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

    def test__get_partner__user_not_exists(self):
        an_invalid_partner_vat = 123
        result = self.partner.get_partner(self.cursor, self.uid, an_invalid_partner_vat)

        self.assertIsNone(result)


    def test__get_partner__user_exists(self):
        partner_id = self.imd.get_object_reference(
            self.cursor, self.uid, 'base', 'res_partner_asus'
        )[1]
        res_partner_asus_vat = 'S2903826B'

        partner = self.partner.get_partner(self.cursor, self.uid, res_partner_asus_vat)
        partner_cif = partner[0]['vat']

        expected_partner_cif = self.res_partner.read(
            self.cursor, self.uid, partner_id,['vat']
        )['vat']
        self.assertEqual(expected_partner_cif, partner_cif)