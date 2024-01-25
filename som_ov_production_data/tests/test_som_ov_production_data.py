# -*- coding: utf-8 -*-
from destral import testing
from destral.transaction import Transaction

from .. import som_ov_production_data

class SomOvProductionDataTests(testing.OOTestCase):

    def setUp(self):
        self.pool = self.openerp.pool
        self.imd = self.pool.get('ir.model.data')

        self.txn = Transaction().start(self.database)

        self.cursor = self.txn.cursor
        self.uid = self.txn.user
        self.maxDiff = None

    def tearDown(self):
        self.txn.stop()

    def test__get_production_data(self):
        self.assertTrue(True)
