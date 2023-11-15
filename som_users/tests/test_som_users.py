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

    def reference(self, module, id):
        ir_model_data_obj = self.pool.get("ir.model.data")
        return ir_model_data_obj.get_object_reference(
            self.cursor, self.uid, module, id,
        )[1]

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

    def test__sign_document__all_ok(self):
        username = 'ES48591264S'

        result = self.users.sign_document(self.cursor, self.uid, username, 'RGPD_OV_REPRESENTA')

        self.assertEqual(result, dict(
            signed_version = '2023-11-09 00:00:00',
        ))

    def test__sign_document__signs_last_document_version(self):
        username = 'ES48591264S'
        document_type_id = self.reference(
            "som_signed_documents",
            "type_ovrepresenta_rgpd"
        )
        document_version_obj = self.pool.get('signed.document.type.version')
        document_version_obj.create(self.cursor, self.uid, dict(
            type=document_type_id,
            date='2040-03-02',
        ))

        result = self.users.sign_document(self.cursor, self.uid, username, 'RGPD_OV_REPRESENTA')

        self.assertEqual(result, dict(
            signed_version = '2040-03-02 00:00:00',
        ))

    def test__sign_document__wrong_customer(self):
        username = 'NOTEXISTING'

        result = self.users.sign_document(self.cursor, self.uid, username, 'RGPD_OV_REPRESENTA')

        self.assertEqual(result, dict(
            code='PartnerNotExists',
            error='Partner does not exist',
            trace=result.get('trace', "TRACE IS MISSING"),
        ))

    def test__sign_document__document_without_version(self):
        username = 'ES48591264S'

        version_id = self.reference(
            "som_signed_documents",
            "version_type_ovrepresenta_rgpd_2023"
        )
        print("version_ids", version_id)
        document_version_obj = self.pool.get('signed.document.type.version')
        document_version_obj.unlink(self.cursor, self.uid, version_id)

        result = self.users.sign_document(self.cursor, self.uid, username, 'RGPD_OV_REPRESENTA')

        self.assertEqual(result, dict(
            code='NoDocumentVersions',
            error='Document RGPD_OV_REPRESENTA has no version available to sign',
            trace=(result or {}).get('trace', "TRACE IS MISSING"),
        ))

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

        with self.assertRaises(PartnerNotExists) as ctx:
            self.users._documents_signed_by_customer(self.cursor, self.uid, username)

        self.assertEqual(format(ctx.exception), "Partner does not exist")

    def test__documents_signed_by_customer__filter_other_customer_signatures(self):
        username = 'ES48591264S'
        other = 'ES14763905K'
        self.users.sign_document(self.cursor, self.uid, other, 'RGPD_OV_REPRESENTA')

        result = self.users._documents_signed_by_customer(self.cursor, self.uid, username)

        self.assertEqual([], result)

    def test__sign_document__returned_in_profile(self):
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
            proxy_vat = None,
            proxy_name = None,
            signed_documents = [
                dict(
                    document = 'RGPD_OV_REPRESENTA',
                    version = '2023-11-09 00:00:00',
                ),
            ],
        )

        self.assertEqual(expected_result, result)


