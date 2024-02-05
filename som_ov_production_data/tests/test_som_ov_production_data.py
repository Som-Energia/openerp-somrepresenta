# -*- coding: utf-8 -*-
from destral import testing
from destral.transaction import Transaction

from .. import som_ov_production_data

class SomOvProductionDataTests(testing.OOTestCase):

    def setUp(self):
        self.pool = self.openerp.pool
        self.imd = self.pool.get('ir.model.data')
        self.production_data = self.pool.get('som.ov.production.data')

        self.txn = Transaction().start(self.database)

        self.cursor = self.txn.cursor
        self.uid = self.txn.user
        self.maxDiff = None

    def tearDown(self):
        self.txn.stop()

    def test__measures__base(self):
        result = self.production_data.measures(
            self.cursor, self.uid,
            username='ESW2796397D',
            first_timestamp='2022-01-01 00:00:00',
            last_timestamp='2022-01-01 02:00:00',
            context=None
        )

        expected_result = [
            (
                {
                    'contract_name': '100',
                    'estimated': [False, True, False],
                    'first_timestamp': '2022-01-01 00:00:00',
                    'last_timestamp': '2022-01-01 02:00:00',
                    'maturity': ['H2', 'H3', None],
                    'measured': [80.0, 22.0, None]
                },
            )
        ]
        self.assertEqual(result['data'][0], expected_result)
        self.assertEqual(len(result['data']), 3)
