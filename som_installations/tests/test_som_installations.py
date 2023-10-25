# -*- coding: utf-8 -*-
from destral import testing
from destral.transaction import Transaction

from .. import installation

class SomInstallationsTests(testing.OOTestCase):

    def setUp(self):
        self.pool = self.openerp.pool
        self.imd = self.pool.get('ir.model.data')
        self.installation = self.pool.get('installation')

        self.txn = Transaction().start(self.database)

        self.cursor = self.txn.cursor
        self.uid = self.txn.user

    def tearDown(self):
        self.txn.stop()

    def test__get_installation__user_not_exists(self):
        an_invalid_partner_vat = 123
        import pudb; pu.db
        result = self.installation.get_installation_by(self.cursor, self.uid, an_invalid_partner_vat)

        self.assertEqual(result, 'User not found')