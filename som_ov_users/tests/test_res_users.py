# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from osv.osv import except_osv

from destral import testing
from destral.transaction import Transaction

import unittest

class ResUsersTests(testing.OOTestCase):

    def setUp(self):
        self.pool = self.openerp.pool
        self.imd = self.pool.get('ir.model.data')
        self.res_users = self.pool.get('res.users')
        self.res_partner = self.pool.get('res.partner')
        self.res_partner_address = self.pool.get('res.partner.address')
        self.wiz_o = self.pool.get('wizard.create.staff.users')

        self.txn = Transaction().start(self.database)

        self.cursor = self.txn.cursor
        self.uid = self.txn.user

    def tearDown(self):
        self.txn.stop()

    def reference(self, module, id):
        return self.imd.get_object_reference(
            self.cursor, self.uid, module, id,
        )[1]

    def test___is_user_staff__user_is_staff(self):
        user_id = self.res_users.search(
            self.cursor,
            self.uid,
            [('login', '=', 'matahari')]
        )[0]

        is_staff = self.res_users._is_user_staff(self.cursor, self.uid, self.res_users, user_id)

        self.assertTrue(is_staff)

    def test___is_user_staff__user_is_not_staff(self):
        user_id = self.res_users.search(
            self.cursor,
            self.uid,
            [('login', '=', 'lamaali')]
        )[0]

        is_staff = self.res_users._is_user_staff(self.cursor, self.uid, self.res_users, user_id)

        self.assertFalse(is_staff)

    def test__ovrepre_provisioning_data__base_case(self):
        # User has no address and no partner with such VAT exists
        user_id = self.reference('som_ov_users', 'res_users_staff') # TOD:rename to no_staff

        data = self.res_users.ovrepre_provisioning_data(self.cursor, self.uid, user_id)

        self.assertEqual(data, dict(
            vat = None,
            email = None,
        ))

    def test__ovrepre_provisioning_data__non_staff_address_linked(self):
        partner_id = self.reference(
            "som_ov_users",
            "res_partner_res_users_already_staff",
        )
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        user_id = self.reference(
            "som_ov_users",
            "res_users_already_staff",
        )
        # Remove the category
        self.res_partner.write(self.cursor, self.uid, partner_id, {'category_id': [(6, 0, [])]})

        data = self.res_users.ovrepre_provisioning_data(self.cursor, self.uid, user_id)

        self.assertEqual(data, dict(
            vat = partner.vat,
            email = partner.address[0].email,
        ))

    def test__ovrepre_provisioning_data__already_staff__gives_error(self):
        partner_id = self.reference(
            "som_ov_users",
            "res_partner_res_users_already_staff",
        )
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)
        user_id = self.reference(
            "som_ov_users",
            "res_users_already_staff",
        )

        data = self.res_users.ovrepre_provisioning_data(self.cursor, self.uid, user_id)

        self.assertEqual(data, dict(
            vat = partner.vat,
            email = partner.address[0].email,
            error = "La usuaria ja estàva com a gestora de l'Oficina Virtual de Representa",
        ))

    @unittest.skip('Wait for Fran to confime whether the fisrt or the last address is used')
    def test__ovrepre_provisioning_data__non_staff_with_linked_secondary_address(self):
        partner_id = self.reference(
            "som_ov_users",
            "res_partner_res_users_already_staff",
        )
        user_id = self.reference(
            "som_ov_users",
            "res_users_already_staff",
        )
        new_partner_address_id = self.reference(
            "som_ov_users",
            "res_partner_address_unlinked",
        )
        # Remove the category and add the new address
        LINK = 4
        SET = 6
        self.res_partner.write(self.cursor, self.uid, partner_id, {
            'category_id': [(SET, 0, [])],
            # This sets the new primary address of the partner
            # now different from the one linked in user which
            # is set as secondary now
            'address': [(LINK, new_partner_address_id)],
        })
        partner = self.res_partner.browse(self.cursor, self.uid, partner_id)

        data = self.res_users.ovrepre_provisioning_data(self.cursor, self.uid, user_id)

        self.assertEqual(data, dict(
            vat = partner.vat,
            email = "unlinked@somenergia.coop", # partner.address[0].email,
            warning = "",
        ))

