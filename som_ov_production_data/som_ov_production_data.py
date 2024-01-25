# -*- coding: utf-8 -*-
from osv import osv

from som_ov_users.decorators import www_entry_point

class SomOvProductionData(osv.osv_memory):

    _name = "som.ov.production.data"

    @www_entry_point()
    def get_production_data(self, cursor, uid, cil):
        return True

SomOvProductionData()
