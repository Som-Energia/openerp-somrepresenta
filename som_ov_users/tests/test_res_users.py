# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from osv.osv import except_osv

from destral import testing
from destral.transaction import Transaction

import unittest

def get_models(self):
    self.pool = self.openerp.pool
    self.imd = self.pool.get('ir.model.data')
    self.res_users = self.pool.get('res.users')
    self.res_partner = self.pool.get('res.partner')
    self.res_partner_address = self.pool.get('res.partner.address')
    self.wiz_o = self.pool.get('wizard.create.staff.users')

def setup_transaction(self):
    self.txn = Transaction().start(self.database)

    self.cursor = self.txn.cursor
    self.uid = self.txn.user
    def cleanup():
        self.txn.stop()
    self.addCleanup(cleanup)

def reference(self, module, id):
    return self.imd.get_object_reference(
        self.cursor, self.uid, module, id,
    )[1]


class ResUsersTests(testing.OOTestCase):
    get_models = get_models
    setup_transaction = setup_transaction
    reference = reference

    def setUp(self):
        self.get_models()
        self.setup_transaction()
        self.staff_user_id = self.reference('som_ov_users', 'res_users_already_staff')

    def test__is_user_staff__user_is_staff(self):
        user_id = self.staff_user_id

        is_staff = self.res_users._is_user_staff(self.cursor, self.uid, self.res_users, user_id)

        self.assertTrue(is_staff)

    def test__is_user_staff__user_is_not_staff(self):
        user_id = self.reference('som_ov_users', 'res_users_non_staff')

        is_staff = self.res_users._is_user_staff(self.cursor, self.uid, self.res_users, user_id)

        self.assertFalse(is_staff)

    def test__init_wizard_to_turn_into_representation_staff__base_case(self):
        # User has no address and no partner with such VAT exists
        user_id = self.reference('som_ov_users', 'res_users_non_staff')

        data = self.res_users.init_wizard_to_turn_into_representation_staff(self.cursor, self.uid, user_id)

        self.assertEqual(data, dict(
            vat = None,
            email = None,
        ))

    def test__init_wizard_to_turn_into_representation_staff__linked_to_non_staff_address(self):
        partner_id = self.reference(
            "som_ov_users",
            "res_partner_res_users_already_staff",
        )
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        user_id = self.staff_user_id
        # Remove the category
        self.res_partner.write(self.cursor, self.uid, partner_id, {'category_id': [(6, 0, [])]})

        data = self.res_users.init_wizard_to_turn_into_representation_staff(self.cursor, self.uid, user_id)

        # Then the wizard uses data from the linked parnter
        self.assertEqual(data, dict(
            vat = partner.vat,
            email = partner.address[0].email,
        ))

    def test__init_wizard_to_turn_into_representation_staff__linked_partner_already_staff__gives_error(self):
        partner_id = self.reference(
            "som_ov_users",
            "res_partner_res_users_already_staff",
        )
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        user_id = self.staff_user_id

        data = self.res_users.init_wizard_to_turn_into_representation_staff(self.cursor, self.uid, user_id)

        self.assertEqual(data, dict(
            vat = partner.vat,
            email = partner.address[0].email,
            error = "La usuaria ja estàva com a gestora de l'Oficina Virtual de Representa",
        ))

    def test__init_wizard_to_turn_into_representation_staff__when_linked_to_a_secondary_address__warn_not_the_address_to_be_used(self):
        partner_id = self.reference(
            "som_ov_users",
            "res_partner_res_users_already_staff",
        )
        user_id = self.staff_user_id
        new_partner_address_id = self.reference(
            "som_ov_users",
            "res_partner_address_unlinked",
        )
        # Remove the category and add the new address
        LINK = 4
        SET = 6
        self.res_partner.write(self.cursor, self.uid, partner_id, {
            'category_id': [(SET, 0, [])],
            # Add the new address to the existing one
            'address': [(LINK, new_partner_address_id)],
        })
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        user = self.res_users.browse(self.cursor, self.uid, user_id)
        # The linked address is not the first one of the partner
        self.res_users.write(self.cursor, self.uid, user_id, dict(
            address_id=new_partner_address_id,
        ))

        data = self.res_users.init_wizard_to_turn_into_representation_staff(self.cursor, self.uid, user_id)

        self.assertEqual(data, dict(
            vat = partner.vat,
            email = partner.address[0].email, # not "unlinked@somenergia.coop"
            warning = (
                "L'adreça vinculada a la usuària, {linked}, "
                "no serà la que es fará servir a la OV sinó "
                "la de l'adreça principal de la persona {primary}"
            ).format(
                linked = user.address_id.email,
                primary = partner.address[0].email,
            ),
        ))

    def test__init_wizard_to_turn_into_representation_staff__user_linked_to_a_partnerless_address(self):
        user_id = self.staff_user_id
        new_partner_address_id = self.reference(
            "som_ov_users",
            "res_partner_address_unlinked",
        )
        # The user address is an unlinked one
        self.res_users.write(self.cursor, self.uid, user_id, dict(
            address_id=new_partner_address_id,
        ))

        data = self.res_users.init_wizard_to_turn_into_representation_staff(self.cursor, self.uid, user_id)

        self.assertEqual(data, dict(
            error = "La usuària té una adreça que no està vinculada a cap persona",
        ))

    def test__init_wizard_to_turn_into_representation_staff__linked_partner_without_vat(self):
        partner_id = self.reference(
            "som_ov_users",
            "res_partner_res_users_already_staff",
        )
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        user_id = self.staff_user_id
        # Remove the category and the partner VAT
        self.res_partner.write(self.cursor, self.uid, partner_id, {
            'category_id': [(6, 0, [])],
            'vat': False,
        })

        data = self.res_users.init_wizard_to_turn_into_representation_staff(self.cursor, self.uid, user_id)

        self.assertEqual(data, dict(
            error = "La persona vinculada per l'adreça de la usuària no té VAT",
        ))

    def test__init_wizard_to_turn_into_representation_staff__linked_partner_without_email(self):
        partner_id = self.reference(
            "som_ov_users",
            "res_partner_res_users_already_staff",
        )
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        user_id = self.staff_user_id
        # Remove the category
        self.res_partner.write(self.cursor, self.uid, partner_id, {
            'category_id': [(6, 0, [])],
        })
        self.res_partner_address.write(self.cursor, self.uid, partner.address[0].id, dict(
            email = False,
        ))

        data = self.res_users.init_wizard_to_turn_into_representation_staff(self.cursor, self.uid, user_id)

        self.assertEqual(data, dict(
            error = "L'adreça primària de la persona vinculada a la usuària no té email",
        ))

    def test__init_wizard_to_turn_into_representation_staff__dupped_vat(self):
        partner_id = self.reference(
            "som_ov_users",
            "res_partner_res_users_already_staff",
        )
        other_partner_id = self.reference(
            "som_ov_users",
            "res_partner_soci",
        )

        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        other_partner = self.res_partner.browse(self.cursor, self.uid, other_partner_id)
        user_id = self.staff_user_id

        # Remove the category
        self.res_partner.write(self.cursor, self.uid, partner_id, {
            'category_id': [(6, 0, [])],
            'vat': other_partner.vat,
        })

        data = self.res_users.init_wizard_to_turn_into_representation_staff(self.cursor, self.uid, user_id)

        # Then the wizard uses data from the linked parnter
        self.assertEqual(data, dict(
            error = "El VAT de la persona vinculada a la usuària, {vat}, està assignat a més persones".format(vat=other_partner.vat),
        ))

