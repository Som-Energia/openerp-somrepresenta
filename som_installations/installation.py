# -*- coding: utf-8 -*-
from osv import osv
from som_users import partner

class Installation(osv.osv):

    _name = 'installation'
    _inherit = 'giscere.instalacio'

    def get_installation_by(self, cursor, uid, cif):
        partner_obj = self.pool.get('partner')
        partner = partner_obj.get_partner(cursor, uid, cif)
        if partner:
            return 'User found'
        else:
            return 'User not found'


Installation()