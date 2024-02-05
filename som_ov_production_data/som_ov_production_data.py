# -*- coding: utf-8 -*-
from osv import osv

from datetime import datetime
from collections import defaultdict

from som_ov_users.decorators import www_entry_point


class SomOvProductionData(osv.osv_memory):

    _name = "som.ov.production.data"

    def _get_current_date():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    DEFAULT_FIRST_TIMESTAMP = _get_current_date()
    DEFAULT_LAST_TIMESTAMP = None
    MEASURE_MATURITY_LEVELS = ('H2', 'H3', 'HP', 'HC')

    @www_entry_point()
    def measures(
        self, cursor, uid,
        username,
        first_timestamp=DEFAULT_FIRST_TIMESTAMP,
        last_timestamp=DEFAULT_LAST_TIMESTAMP,
        context=None
    ):

        if context is None:
            context = {}

        contracts = self._get_user_contracts(cursor, uid, username, context)
        production_measures = dict(data=[
            self._get_production_measures(cursor, contract, first_timestamp, last_timestamp)
            for contract in contracts
        ])

        return production_measures

    def _get_user_contracts(self, cursor, uid, username, context):
        installation_obj = self.pool.get('som.ov.installations')
        return installation_obj.get_user_contracts(cursor, uid, username, context)

    def _get_production_measures(self, cursor, contract, first_timestamp, last_timestamp):
        cursor.execute(
            '''
                WITH filtered_data AS (
                    SELECT
                        "timestamp",
                        ae,
                        maturity,
                        type_measure
                    FROM
                        giscere_mhcil
                    WHERE
                        cil = %s
                        AND "timestamp" BETWEEN %s AND %s -- parametrized
                    ),
                    filled_data AS (
                    SELECT
                        generate_series AS "timestamp",
                        NULL AS ae,
                        NULL AS maturity,
                        NULL AS type_measure
                    FROM
                        generate_series(
                            %s,
                            %s,
                            INTERVAL '1 HOUR'
                        )
                    WHERE
                        generate_series NOT IN (SELECT "timestamp" FROM filtered_data)
                    ),
                    final_data AS (
                    SELECT
                        COALESCE(fd."timestamp", fd2."timestamp") AS "timestamp",
                        COALESCE(fd.ae, NULL) AS ae, -- Modified this line to return NULL instead of 0
                        COALESCE(fd.maturity, fd2.maturity) AS maturity,
                        COALESCE(fd.type_measure, fd2.type_measure) AS type_measure
                    FROM
                        filtered_data fd
                    FULL JOIN
                        filled_data fd2 ON fd."timestamp" = fd2."timestamp"
                    ),
                    ranked_data AS (
                    SELECT
                        *,
                        RANK() OVER (PARTITION BY "timestamp" ORDER BY
                        CASE
                            WHEN maturity = 'H2' THEN 1
                            WHEN maturity = 'H3' THEN 2
                            WHEN maturity = 'HP' THEN 3
                            WHEN maturity = 'HC' THEN 4
                            ELSE 5
                        END
                        ) AS maturity_rank
                    FROM
                        final_data
                    )
                    SELECT
                    JSON_BUILD_OBJECT(
                        'contract_name', %s,
                        'first_timestamp', (SELECT MIN("timestamp") FROM ranked_data),
                        'last_timestamp', (SELECT MAX("timestamp") FROM ranked_data),
                        'estimated', ARRAY_AGG(CASE WHEN type_measure IN ('E', 'M') THEN true ELSE false END ORDER BY "timestamp" ASC),
                        'measured', ARRAY_AGG(ae ORDER BY "timestamp" ASC),
                        'maturity', ARRAY_AGG(maturity ORDER BY "timestamp" ASC)
                    ) AS data
                    FROM
                        ranked_data
                    WHERE
                    maturity_rank = 1;
            ''',
            (contract.cil.name, first_timestamp, last_timestamp, first_timestamp, last_timestamp, contract.name)
        )

        return cursor.fetchall()


SomOvProductionData()
