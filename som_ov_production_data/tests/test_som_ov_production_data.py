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
            first_timestamp_utc='2022-01-01T00:00:00Z',
            last_timestamp_utc='2022-01-01T02:00:00Z',
            context=None
        )

        expected_result = {
            'contract_name': '100',
            'estimated': [False, True, None],
            'first_timestamp_utc': '2022-01-01T00:00:00Z',
            'last_timestamp_utc': '2022-01-01T02:00:00Z',
            'maturity': ['H2', 'H3', None],
            'measure_kwh': [80.0, 22.0, None],
            'foreseen_kwh': [10.0, 22.0, None],
        }
        self.assertNotIn('error', result, str(result))
        self.assertEqual(result['data'][0], expected_result)
        self.assertEqual(len(result['data']), 3)
