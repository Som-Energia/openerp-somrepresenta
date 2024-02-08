# -*- coding: utf-8 -*-
from destral import testing
from destral.transaction import Transaction

from .. import som_ov_production_data


class SomOvProductionDataTests(testing.OOTestCase):

    base_username = 'ESW2796397D'
    username_without_contracts = 'ES36464471H'

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

    def reference(self, module, id):
        return self.imd.get_object_reference(
            self.cursor, self.uid, module, id,
        )[1]

    def test__measures__base(self):
        result = self._sut(
            username=self.base_username,
            first_timestamp_utc='2022-01-01T00:00:00Z',
            last_timestamp_utc='2022-01-01T01:00:00Z',
        )

        expected_result = {
            'contract_name': '100',
            'estimated': [False, True],
            'first_timestamp_utc': '2022-01-01T00:00:00Z',
            'last_timestamp_utc': '2022-01-01T01:00:00Z',
            'maturity': ['H2', 'H3'],
            'measure_kwh': [80.0, 22.0],
            'foreseen_kwh': [10.0, 22.0],
        }
        self.assertNotIn('error', result, str(result))
        self.assertEqual(result['data'][0], expected_result)
        self.assertEqual(len(result['data']), 3)

    def test__measures__gaps_filled_with_none(self):
        result = self._sut(
            username=self.base_username,
            first_timestamp_utc='2021-12-31T23:00:00Z',
            last_timestamp_utc='2022-01-01T02:00:00Z',
        )

        expected_result = {
            'contract_name': '100',
            'estimated': [None, False, True, None],
            'first_timestamp_utc': '2021-12-31T23:00:00Z',
            'last_timestamp_utc': '2022-01-01T02:00:00Z',
            'maturity': [None, 'H2', 'H3', None],
            'measure_kwh': [None, 80.0, 22.0, None],
            'foreseen_kwh': [None, 10.0, 22.0, None],
        }
        self.assertNotIn('error', result, str(result))
        self.assertEqual(result['data'][0], expected_result)
        self.assertEqual(len(result['data']), 3)

    def test__measures__no_such_user(self):
        result = self._sut(
            username='username_not_exists',
            first_timestamp_utc='2022-01-01T00:00:00Z',
            last_timestamp_utc='2022-01-01T01:00:00Z',
        )

        self.assertEqual(result, dict(
            code='NoSuchUser',
            error='User does not exist',
            trace=result.get('trace', 'NO TRACE AVAILABLE'),
        ))

    def test__measures__no_data(self):
        result = self._sut(
            username=self.base_username,
            first_timestamp_utc='2018-12-31T23:00:00Z',
            last_timestamp_utc='2019-01-01T02:00:00Z',
        )

        expected_result = {
            'contract_name': '100',
            'estimated': [None, None, None, None],
            'first_timestamp_utc': '2018-12-31T23:00:00Z',
            'last_timestamp_utc': '2019-01-01T02:00:00Z',
            'maturity': [None, None, None, None],
            'measure_kwh': [None, None, None, None],
            'foreseen_kwh': [None, None, None, None],
        }
        self.assertNotIn('error', result, str(result))
        self.assertEqual(result['data'][0], expected_result)
        self.assertEqual(len(result['data']), 3)

    def test__measures__crossed_dates(self):
        result = self._sut(
            username=self.base_username,
            first_timestamp_utc='2018-12-31T23:00:00Z',
            last_timestamp_utc='2016-01-01T02:00:00Z'
        )

        expected_result = {
            'contract_name': '100',
            'estimated': [],
            'first_timestamp_utc': '2018-12-31T23:00:00Z',
            'last_timestamp_utc': '2016-01-01T02:00:00Z',
            'maturity': [],
            'measure_kwh': [],
            'foreseen_kwh': [],
        }
        self.assertNotIn('error', result, str(result))
        self.assertEqual(result['data'][0], expected_result)
        self.assertEqual(len(result['data']), 3)

    def test__measures__user_without_contracts(self):
        result = self._sut(
            username=self.username_without_contracts,
            first_timestamp_utc='2022-01-01T00:00:00Z',
            last_timestamp_utc='2022-01-01T01:00:00Z',
        )

        self.assertNotIn('error', result, str(result))
        self.assertEqual(len(result['data']), 0)

    def test__measures__installation_without_forecast_code(self):
        installation_obj = self.pool.get('giscere.instalacio')
        installation_id  = self.reference(
            'som_ov_installations',
            'giscere_instalacio_0',
        )
        installation_obj.write(self.cursor, self.uid, installation_id, dict(codi_previsio=None))

        result = self._sut(
            username=self.base_username,
            first_timestamp_utc='2022-01-01T00:00:00Z',
            last_timestamp_utc='2022-01-01T01:00:00Z',
        )

        expected_result = {
            'contract_name': '100',
            'estimated': [False, True],
            'first_timestamp_utc': '2022-01-01T00:00:00Z',
            'last_timestamp_utc': '2022-01-01T01:00:00Z',
            'maturity': ['H2', 'H3'],
            'measure_kwh': [80.0, 22.0],
            'foreseen_kwh': [None, None], # THIS CHANGES
        }
        self.assertNotIn('error', result, str(result))
        self.assertEqual(result['data'][0], expected_result)

    def test__mesasures__time_series(self):
        result = self._sut(
            username=self.base_username,
            first_timestamp_utc='2020-01-01T00:00:00Z',
            last_timestamp_utc='2024-01-01T00:00:00Z',
        )

        expected_timestamp_range_total_hours_ = 35065
        self.assertNotIn('error', result, str(result))
        self.assertEqual(len(result['data'][0]['estimated']), expected_timestamp_range_total_hours_)
        self.assertEqual(len(result['data'][0]['measure_kwh']), expected_timestamp_range_total_hours_)
        self.assertEqual(len(result['data'][0]['foreseen_kwh']), expected_timestamp_range_total_hours_)

    def _sut(self, username, first_timestamp_utc, last_timestamp_utc):
        return self.production_data.measures(
            self.cursor, self.uid,
            username=username,
            first_timestamp_utc=first_timestamp_utc,
            last_timestamp_utc=last_timestamp_utc,
            context=None
        )
