# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from osv.osv import except_osv

from destral import testing
from destral.transaction import Transaction

import unittest


class OrmLink:
    create = 0
    update = 1
    delete = 2
    unlink = 3
    link = 4
    clear = 5
    set = 6

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
        self.staff_partner_id = self.reference('som_ov_users', 'res_partner_res_users_already_staff')
        self.non_staff_user_id = self.reference('som_ov_users', 'res_users_non_staff')
        self.unlinked_address_id = self.reference('som_ov_users', 'res_partner_address_unlinked')
        self.non_staff_partner_id = self.reference('som_ov_users', 'res_partner_not_customer')
        self.other_partner_id = self.reference('som_ov_users', 'res_partner_soci')
        self.cat_staff_id = self.reference("som_ov_users", "res_partner_category_ovrepresenta_staff")

    def set_user_address(self, user_id, address_id):
        self.res_users.write(self.cursor, self.uid, user_id, {
            'address_id': address_id,
        })

    def add_partner_address(self, partner_id, address_id):
        self.res_partner.write(self.cursor, self.uid, partner_id, {
            'address': [(OrmLink.link, address_id)],
        })

    def clear_partner_categories(self, partner_id):
        self.res_partner.write(self.cursor, self.uid, partner_id, {
            'category_id': [(OrmLink.set, 0, [])],
        })

    def add_partner_category(self, partner_id, category_id):
        self.res_partner.write(self.cursor, self.uid, partner_id, {
            'category_id': [(OrmLink.link, category_id)],
        })

    def set_partner_vat(self, partner_id, vat):
        self.res_partner.write(self.cursor, self.uid, partner_id, {
            'vat': vat,
        })

    def set_partner_primary_email(self, partner_id, email):
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        primary_address_id = partner.address[0].id
        self.res_partner_address.write(self.cursor, self.uid, primary_address_id, {
            'email': email,
        })

    def test__is_user_staff__user_is_staff(self):
        user_id = self.staff_user_id

        is_staff = self.res_users._is_user_staff(self.cursor, self.uid, user_id)

        self.assertTrue(is_staff)

    def test__is_user_staff__user_is_not_staff(self):
        user_id = self.non_staff_user_id

        is_staff = self.res_users._is_user_staff(self.cursor, self.uid, user_id)

        self.assertFalse(is_staff)

    def test__init_wizard_to_turn_into_representation_staff__base_case(self):
        """User has no address and no partner with such VAT exists"""
        user_id = self.non_staff_user_id

        data = self.res_users.init_wizard_to_turn_into_representation_staff(self.cursor, self.uid, user_id)

        self.assertEqual(data, dict(
            vat = None,
            email = None,
        ))

    def test__init_wizard_to_turn_into_representation_staff__linked_to_non_staff_address__takes_data_from_address(self):
        user_id = self.staff_user_id
        partner_id = self.staff_partner_id
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        # Remove the category
        self.clear_partner_categories(partner_id)

        data = self.res_users.init_wizard_to_turn_into_representation_staff(self.cursor, self.uid, user_id)

        # Then the wizard uses data from the linked parnter
        self.assertEqual(data, dict(
            vat = partner.vat,
            email = partner.address[0].email,
        ))

    def test__init_wizard_to_turn_into_representation_staff__linked_partner_already_staff__returns_error(self):
        user_id = self.staff_user_id
        partner_id = self.staff_partner_id
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)

        data = self.res_users.init_wizard_to_turn_into_representation_staff(self.cursor, self.uid, user_id)

        self.assertEqual(data, dict(
            vat = partner.vat,
            email = partner.address[0].email,
            init_error=True,
            init_message = "La usuaria ja estàva com a gestora de l'Oficina Virtual de Representa",
        ))

    def test__init_wizard_to_turn_into_representation_staff__when_linked_to_a_secondary_address__warn_not_the_address_to_be_used(self):
        user_id = self.staff_user_id
        partner_id = self.staff_partner_id
        new_partner_address_id = self.unlinked_address_id
        # Remove the category
        self.clear_partner_categories(partner_id)
        # Add the new address to the existing one
        self.add_partner_address(partner_id, new_partner_address_id)
        # The linked address is not the first one of the partner
        self.set_user_address(user_id, new_partner_address_id)

        data = self.res_users.init_wizard_to_turn_into_representation_staff(self.cursor, self.uid, user_id)

        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        user = self.res_users.browse(self.cursor, self.uid, user_id)
        self.assertEqual(data, dict(
            vat = partner.vat,
            email = partner.address[0].email, # not "unlinked@somenergia.coop"
            init_error=False,
            init_message = (
                "L'adreça vinculada a la usuària, {linked}, "
                "no serà la que es fará servir a la OV sinó "
                "la de l'adreça principal de la persona {primary}"
            ).format(
                linked = user.address_id.email,
                primary = partner.address[0].email,
            ),
        ))

    def test__init_wizard_to_turn_into_representation_staff__user_linked_to_a_partnerless_address__returns_error(self):
        user_id = self.staff_user_id
        # The user address is an unlinked one
        self.set_user_address(user_id, self.unlinked_address_id)

        data = self.res_users.init_wizard_to_turn_into_representation_staff(self.cursor, self.uid, user_id)

        self.assertEqual(data, dict(
            init_error=True,
            init_message = "La usuària té una adreça que no està vinculada a cap persona",
        ))

    def test__init_wizard_to_turn_into_representation_staff__linked_partner_without_vat__returns_error(self):
        user_id = self.staff_user_id
        partner_id = self.staff_partner_id
        # Remove the category and the partner VAT
        self.clear_partner_categories(partner_id)
        self.set_partner_vat(partner_id, False)

        data = self.res_users.init_wizard_to_turn_into_representation_staff(self.cursor, self.uid, user_id)

        self.assertEqual(data, dict(
            init_error=True,
            init_message = "La persona vinculada per l'adreça de la usuària no té VAT",
        ))

    def test__init_wizard_to_turn_into_representation_staff__linked_partner_without_email__returns_error(self):
        user_id = self.staff_user_id
        partner_id = self.staff_partner_id
        self.clear_partner_categories(partner_id)
        self.set_partner_primary_email(partner_id, False)

        data = self.res_users.init_wizard_to_turn_into_representation_staff(self.cursor, self.uid, user_id)

        self.assertEqual(data, dict(
            init_error=True,
            init_message = "L'adreça primària de la persona vinculada a la usuària no té email",
        ))

    def test__init_wizard_to_turn_into_representation_staff__dupped_vat__returns_error(self):
        user_id = self.staff_user_id
        partner_id = self.staff_partner_id
        other_partner_id = self.other_partner_id
        other_partner = self.res_partner.browse(self.cursor, self.uid, other_partner_id)
        # Remove the category and set the vat of another existing partner
        self.clear_partner_categories(partner_id)
        self.set_partner_vat(partner_id, other_partner.vat)

        data = self.res_users.init_wizard_to_turn_into_representation_staff(self.cursor, self.uid, user_id)

        # Then the wizard uses data from the linked parnter
        self.assertEqual(data, dict(
            init_error=True,
            init_message = "El VAT de la persona vinculada a la usuària, {vat}, està assignat a més persones".format(vat=other_partner.vat),
        ))

    def test__process_wizard_to_turn_into_representation_staff__base_case(self):
        """User has no address and provided VAT does not exist"""
        user_id = self.non_staff_user_id
        vat_not_in_db = 'ESP4594924E'
        email="user@server.com"
        user = self.res_users.browse(self.cursor, self.uid, user_id)

        data = self.res_users.process_wizard_to_turn_into_representation_staff(
            self.cursor, self.uid,
            user=user,
            vat=vat_not_in_db,
            email=email,
        )

        self.assertEqual(
            data['info'], "La usuària ha estat convertida en gestora de l'Oficina Virtual de Representa")
        user = self.res_users.browse(self.cursor, self.uid, user_id)
        self.assertTrue(user.address_id, "Should be linked to an address")
        self.assertEqual(user.address_id.id, user.address_id.partner_id.address[0].id)
        self.assertEqual(user.address_id.partner_id.vat, vat_not_in_db)
        self.assertEqual(user.address_id.email, email)
        self.assertEqual(user.address_id.name, user.name)
        self.assertEqual(user.address_id.partner_id.name, user.name)
        self.assertEqual([x.id for x in user.address_id.partner_id.category_id], [self.cat_staff_id])

    def test__process_wizard_to_turn_into_representation_staff__unlinked_dupped_vat__returns_error(self):
        user_id = self.non_staff_user_id
        partner_id = self.non_staff_partner_id
        other_partner_id = self.other_partner_id
        other_partner = self.res_partner.browse(self.cursor, self.uid, other_partner_id)
        dupped_vat = other_partner.vat
        # Set the vat of another existing partner
        self.set_partner_vat(partner_id, dupped_vat)
        user = self.res_users.browse(self.cursor, self.uid, user_id)

        data = self.res_users.process_wizard_to_turn_into_representation_staff(
            self.cursor, self.uid,
            user=user,
            vat=dupped_vat,
            email="user@server.com",
        )

        self.assertEqual(
            data['info'],
            "El VAT de la persona vinculada a la usuària, {vat}, està assignat a més persones".format(vat=other_partner.vat),
        )

    def test__process_wizard_to_turn_into_representation_staff__unlinked_with_category__returns_error(self):
        user_id = self.non_staff_user_id
        partner_id = self.non_staff_partner_id
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        vat = partner.vat
        self.add_partner_category(partner_id, self.cat_staff_id)
        user = self.res_users.browse(self.cursor, self.uid, user_id)

        data = self.res_users.process_wizard_to_turn_into_representation_staff(
            self.cursor, self.uid,
            user=user,
            vat=vat,
            email=partner.address[0].email, # Same as existing address
        )

        self.assertEqual(
            data['info'],
            "La persona ja és gestora de l'Oficina Virtual de Representa. "
            "Potser el VAT {vat} ja està vinculat amb una altra usuària".format(vat=vat),
        )

