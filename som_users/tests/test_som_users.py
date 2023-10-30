# -*- coding: utf-8 -*-
from destral import testing
from destral.transaction import Transaction

from .. import users


class SomUsersTests(testing.OOTestCase):

    def setUp(self):
        self.pool = self.openerp.pool
        self.imd = self.pool.get('ir.model.data')
        self.res_partner = self.pool.get('res.partner')
        self.users = self.pool.get('users')

        self.txn = Transaction().start(self.database)

        self.cursor = self.txn.cursor
        self.uid = self.txn.user

    def tearDown(self):
        self.txn.stop()

    def test__get_partner__user_exists_and_is_active(self):
        res_partner_soci_vat = '48591264S'

        result = self.users.get_partner_info(self.cursor, self.uid, res_partner_soci_vat)

        expected_result = dict(
            nif='48591264S',
            name='Benedetti, Mario',
            email='test@test.test',
            roles=dict(
                customer=True)
        )
        self.assertEqual(expected_result, result)

    def test__get_partner__user_exists_and_is_not_active(self):
        res_partner_address_soci_not_active_vat = '14763905K'

        result = self.users.get_partner_info(self.cursor, self.uid, res_partner_address_soci_not_active_vat)

        self.assertEqual(result['code'], 'PartnerNotExists')

    def test__get_partner__user_does_not_exists(self):
        res_partner_soci_not_exists_vat = '12345678A'

        result = self.users.get_partner_info(self.cursor, self.uid, res_partner_soci_not_exists_vat)

        self.assertEqual(result['code'], 'PartnerNotExists')

    def test__get_partner_profile(self):
        res_partner_soci_vat = '48591264S'

        result = self.users.get_partner_profile(self.cursor, self.uid, res_partner_soci_vat)
        expected_result = dict(
            nif = '48591264S',
            address = 'Rincón de Haikus, 23',
            city = 'Paso de los Toros',
            zip = '08600',
            state = 'Granada',
            phone = dict(
                landline='933333333',
                mobile='666666666',
            ),
            roles = dict(customer=True),
        )

        self.assertEqual(expected_result, result)
