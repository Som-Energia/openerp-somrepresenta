# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from destral import testing
from destral.transaction import Transaction
from som_users.exceptions import FailSendEmail

from som_users.exceptions import FailSendEmail

import mock

class WizardCreateChangePasswordTests(testing.OOTestCase):

    def setUp(self):
        self.pool = self.openerp.pool
        self.res_partner = self.pool.get('res.partner')
        self.wiz_o = self.pool.get('wizard.create.change.password')

        self.txn = Transaction().start(self.database)

        self.cursor = self.txn.cursor
        self.uid = self.txn.user

    def tearDown(self):
        self.txn.stop()

    @mock.patch("som_users.wizard.wizard_create_change_password.WizardCreateChangePassword.save_password")
    def test__action_create_change_password__OK(self, mock_save_password):
        partner_id = self.res_partner.search(
            self.cursor,
            self.uid,
            [('vat', '=', 'ES48591264S')]
        )

        context = {'active_ids': partner_id}
        wiz_id = self.wiz_o.create(self.cursor, self.uid, {}, context=context)

        mock_save_password.return_value = True

        self.wiz_o.action_create_change_password(self.cursor, self.uid, [wiz_id], context=context)

        wiz = self.wiz_o.read(self.cursor, self.uid, [wiz_id])[0]

        self.assertEqual(wiz['state'], 'done')
        self.assertEqual(wiz['info'], 'Contrassenyes generades')

    @mock.patch("som_users.wizard.wizard_create_change_password.WizardCreateChangePassword.send_password_email")
    @mock.patch("som_users.wizard.wizard_create_change_password.WizardCreateChangePassword.save_password")
    def test__action_create_change_password__KO_cannot_save_password(self, mock_save_password, mock_send_password_email):
        partner_id = self.res_partner.search(
            self.cursor,
            self.uid,
            [('vat', '=', 'ES48591264S')]
        )

        context = {'active_ids': partner_id}
        wiz_id = self.wiz_o.create(self.cursor, self.uid, {}, context=context)

        mock_save_password.return_value = False

        self.wiz_o.action_create_change_password(self.cursor, self.uid, [wiz_id], context=context)

        wiz = self.wiz_o.read(self.cursor, self.uid, [wiz_id])[0]

        self.assertEqual(wiz['state'], 'done')
        self.assertEqual(wiz['info'], '{}: \n {} ({})\n'.format(
            'Error generant contrassenyes pels següents partners',
            int(partner_id[0]),
            'Contrassenya no generada'
            )
        )
        mock_send_password_email.assert_not_called()

    @mock.patch("som_users.wizard.wizard_create_change_password.WizardCreateChangePassword.send_password_email")
    @mock.patch("som_users.wizard.wizard_create_change_password.WizardCreateChangePassword.save_password")
    def test__action_create_change_password__KO_cannot_send_password_email(self, mock_save_password, mock_send_password_email):
        partner_id = self.res_partner.search(
            self.cursor,
            self.uid,
            [('vat', '=', 'ES48591264S')]
        )

        context = {'active_ids': partner_id}
        wiz_id = self.wiz_o.create(self.cursor, self.uid, {}, context=context)

        mock_save_password.return_value = True
        
        def send_password_email(cursor, uid, partner_id):
            raise FailSendEmail('Error text')

        mock_send_password_email.side_effect = send_password_email

        self.wiz_o.action_create_change_password(self.cursor, self.uid, [wiz_id], context=context)

        wiz = self.wiz_o.read(self.cursor, self.uid, [wiz_id])[0]

        self.assertEqual(wiz['state'], 'done')
        self.assertEqual(wiz['info'], '{}: \n {} ({})\n'.format(
            'Error generant contrassenyes pels següents partners',
            int(partner_id[0]),
            "Error al generar/enviar l'email")
        )

    @mock.patch("som_users.wizard.wizard_create_change_password.WizardCreateChangePassword.save_password")
    def test__action_create_change_password__multiple_partners__OK(self, mock_save_password):
        partner_ids = self.res_partner.search(
            self.cursor,
            self.uid,
            [('active', '=', True)]
        )

        context = {'active_ids': partner_ids}
        wiz_id = self.wiz_o.create(self.cursor, self.uid, {}, context=context)

        mock_save_password.return_value = True

        self.wiz_o.action_create_change_password(self.cursor, self.uid, [wiz_id], context=context)

        wiz = self.wiz_o.read(self.cursor, self.uid, [wiz_id])[0]

        self.assertEqual(wiz['state'], 'done')
        self.assertEqual(wiz['info'], 'Contrassenyes generades')

    @mock.patch("som_users.wizard.wizard_create_change_password.WizardCreateChangePassword.send_password_email")
    @mock.patch("som_users.wizard.wizard_create_change_password.WizardCreateChangePassword.save_password")
    def test__action_create_change_password__multiple_partners__KO_cannot_save_password(self, mock_save_password, mock_send_password_email):
        partner_ids = self.res_partner.search(
            self.cursor,
            self.uid,
            [('active', '=', True)]
        )

        context = {'active_ids': partner_ids}
        wiz_id = self.wiz_o.create(self.cursor, self.uid, {}, context=context)

        mock_save_password.return_value = False

        self.wiz_o.action_create_change_password(self.cursor, self.uid, [wiz_id], context=context)

        wiz = self.wiz_o.read(self.cursor, self.uid, [wiz_id])[0]

        self.assertEqual(wiz['state'], 'done')
        self.assertEqual(wiz['info'], '{}: \n {}'.format(
            'Error generant contrassenyes pels següents partners',
            ','.join(['{} ({})\n'.format(str(int(x)),'Contrassenya no generada') for x in partner_ids])
            )
        )

    @mock.patch("som_users.wizard.wizard_create_change_password.WizardCreateChangePassword.send_password_email")
    @mock.patch("som_users.wizard.wizard_create_change_password.WizardCreateChangePassword.save_password")
    def test__action_create_change_password__multiple_partners__KO_cannot_save_password__even_partner_id(self, mock_save_password, mock_send_password_email):
        partner_ids = self.res_partner.search(
            self.cursor,
            self.uid,
            [('active', '=', True)]
        )

        context = {'active_ids': partner_ids}
        wiz_id = self.wiz_o.create(self.cursor, self.uid, {}, context=context)

        def save_password(cursor, uid, partner_id, password):
            if partner_id % 2 == 0:
                return False
            return True            

        mock_save_password.side_effect = save_password

        self.wiz_o.action_create_change_password(self.cursor, self.uid, [wiz_id], context=context)

        wiz = self.wiz_o.read(self.cursor, self.uid, [wiz_id])[0]

        self.assertEqual(wiz['state'], 'done')
        self.assertEqual(wiz['info'], '{}: \n {}'.format(
            'Error generant contrassenyes pels següents partners',
            ','.join(['{} ({})\n'.format(str(int(x)),'Contrassenya no generada') for x in partner_ids if x % 2 == 0])
            )
        )

    @mock.patch("som_users.wizard.wizard_create_change_password.WizardCreateChangePassword.send_password_email")
    @mock.patch("som_users.wizard.wizard_create_change_password.WizardCreateChangePassword.save_password")
    def test__action_create_change_password__KO_cannot_send_password_email__even_partner_id(self, mock_save_password, mock_send_password_email):
        partner_ids = self.res_partner.search(
            self.cursor,
            self.uid,
            [('active', '=', True)]
        )

        context = {'active_ids': partner_ids}
        wiz_id = self.wiz_o.create(self.cursor, self.uid, {}, context=context)

        mock_save_password.return_value = True
        
        def send_password_email(cursor, uid, partner_id):
            if int(partner_id.id) % 2 == 0:
                raise FailSendEmail('Error text')

        mock_send_password_email.side_effect = send_password_email

        self.wiz_o.action_create_change_password(self.cursor, self.uid, [wiz_id], context=context)

        wiz = self.wiz_o.read(self.cursor, self.uid, [wiz_id])[0]

        self.assertEqual(wiz['state'], 'done')
        self.assertEqual(wiz['info'], '{}: \n {}'.format(
            'Error generant contrassenyes pels següents partners',
            ','.join(['{} ({})\n'.format(str(int(x)),"Error al generar/enviar l'email") for x in partner_ids if x % 2 == 0])
            )
        )

    def test__save_password__OK(self):
        partner_id = self.res_partner.search(
            self.cursor,
            self.uid,
            [('vat', '=', 'ES48591264S')]
        )
        context = {'active_ids': partner_id}
        # wiz_id = self.wiz_o.create(self.cursor, self.uid, {}, context=context)
        password = 'test-password'

        result = self.wiz_o.save_password(self.cursor, self.uid, partner_id, password)

        self.assertTrue(result)
