# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from destral import testing
from destral.transaction import Transaction

from som_users.exceptions import PartnerNotExists

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
        self.maxDiff = None

    def tearDown(self):
        self.txn.stop()

    def test__get_user_login_info__user_exists_and_is_active(self):
        res_partner_soci_vat = 'ES48591264S'

        result = self.users.identify_login(self.cursor, self.uid, res_partner_soci_vat)

        expected_result = dict(
            vat='ES48591264S',
            name='Benedetti, Mario',
            email='test@test.test',
            roles=['customer'],
            username='ES48591264S',
        )
        self.assertEqual(expected_result, result)

    def test__get_user_login_info__user_exists_and_is_not_active(self):
        res_partner_address_soci_not_active_vat = 'ES14763905K'

        result = self.users.identify_login(self.cursor, self.uid, res_partner_address_soci_not_active_vat)

        self.assertEqual(result['code'], 'PartnerNotExists')

    def test__get_user_login_info__user_does_not_exists(self):
        res_partner_soci_not_exists_vat = 'ES12345678A'

        result = self.users.identify_login(self.cursor, self.uid, res_partner_soci_not_exists_vat)

        self.assertEqual(result['code'], 'PartnerNotExists')

    def test__get_profile(self):
        res_partner_soci_vat = 'ES48591264S'

        result = self.users.get_profile(self.cursor, self.uid, res_partner_soci_vat)
        expected_result = dict(
            vat = 'ES48591264S',
            name = 'Benedetti, Mario',
            email = 'test@test.test',
            address = 'Rincón de Haikus, 23',
            city = 'Paso de los Toros',
            zip = '08600',
            state = 'Granada',
            phones = ['933333333', '666666666'],
            roles = ['customer'],
            username = 'ES48591264S',
            proxy_vat= None,
            proxy_name= None,
            signed_documents = [],
        )

        self.assertEqual(expected_result, result)

    def test__get_profile__without_phone_numbers(self):
        res_partner_soci_vat = 'ES48591264S'

        # get address id
        partner_id = self.res_partner.search(
            self.cursor,
            self.uid,
            [('vat', '=', res_partner_soci_vat)]
        )
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)[0]
        address_id = partner.address[0].id

        # overwrite values
        res_partner_address_model = self.pool.get('res.partner.address')
        res_partner_address_model.write(self.cursor, self.uid, address_id, {'phone': False, 'mobile': False})

        result = self.users.get_profile(self.cursor, self.uid, res_partner_soci_vat)
        expected_result = dict(
            vat = 'ES48591264S',
            name = 'Benedetti, Mario',
            email = 'test@test.test',
            address = 'Rincón de Haikus, 23',
            city = 'Paso de los Toros',
            zip = '08600',
            state = 'Granada',
            phones = [],
            roles = ['customer'],
            username = 'ES48591264S',
            proxy_vat= None,
            proxy_name= None,
            signed_documents = [],
        )
        self.assertEqual(expected_result, result)

    def test__get_profile__with_legal_proxy(self):
        username = 'ESW2796397D'

        result = self.users.get_profile(self.cursor, self.uid, username)
        expected_result = dict(
            vat = 'ESW2796397D',
            name = 'ACME Industries',
            email = 'info@acme.com',
            address = 'Cañon, 12',
            city = 'El Camino',
            zip = '08600',
            state = 'Granada',
            phones = ['933333333', '666666666'],
            roles = ['customer'],
            username = 'ESW2796397D',
            proxy_vat= 'ES12345678X',
            proxy_name= 'Aplastado, Coyote',
            signed_documents = [],
        )
        self.assertEqual(expected_result, result)


    def test__documents_signed_by_customer__no_documents_signed(self):
        username = 'ES48591264S'
        result = self.users._documents_signed_by_customer(self.cursor, self.uid, username)
        self.assertEqual([], result)

    def test__documents_signed_by_customer__a_documents_signed(self):
        username = 'ES48591264S'
        self.users.sign_document(self.cursor, self.uid, username, 'RGPD_OV_REPRESENTA')

        result = self.users._documents_signed_by_customer(self.cursor, self.uid, username)

        self.assertEqual([
            dict(
                document = 'RGPD_OV_REPRESENTA',
                version = '2023-11-09 00:00:00',
            ),
        ], result)

    def test__documents_signed_by_customer__wrong_customer(self):
        username = 'NOTEXISTING'
        self.users.sign_document(self.cursor, self.uid, username, 'RGPD_OV_REPRESENTA')

        with self.assertRaises(PartnerNotExists) as ctx:
            self.users._documents_signed_by_customer(self.cursor, self.uid, username)

        self.assertEqual(format(ctx.exception), "Partner does not exist")



    def _test__sign_document__returned_in_profile(self):
        username = 'ES48591264S'
        self.users.sign_document(self.cursor, self.uid, username, 'RGPD_OV_REPRESENTA')

        result = self.users.get_profile(self.cursor, self.uid, username)
        expected_result = dict(
            vat = 'ES48591264S',
            name = 'Benedetti, Mario',
            email = 'test@test.test',
            address = 'Rincón de Haikus, 23',
            city = 'Paso de los Toros',
            zip = '08600',
            state = 'Granada',
            phones = ['933333333', '666666666'],
            roles = ['customer'],
            username = 'ES48591264S',
            signed_documents = [
                dict(
                    document = 'RGPD_OV_REPRESENTA',
                    version = '2023-11-09 00:00:00',
                ),
            ],
        )

        self.assertEqual(expected_result, result)


