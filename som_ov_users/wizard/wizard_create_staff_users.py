# -*- coding: utf-8 -*-
from osv import osv, fields

class WizardCreateStaffUsers(osv.osv_memory):

    """Classe per gestionar la creació del usuaris staff
    """

    _name = "wizard.create.staff.users"

    def action_create_staff_users(self, cursor, uid, ids, context=None):
        if context is None:
            context = {}
        
        user_obj = self.pool.get("res.users")
        address_obj = self.pool.get("res.partner.address")
        partner_obj = self.pool.get("res.partner")

        user_id = context.get("active_id")

        import pudb; pu.db
        if user_id:
            user = user_obj.browse(cursor, uid, user_id)
            if not user.address_id:
                address_id = address_obj.create(cursor, uid, {'name': user.name})
                user_obj.write(cursor, uid, user_id, {'address_id': address_id})
            else:
                address = user.address_id
                email = address.get('email', 'email_pasao')


    _columns = {
        'state': fields.char('State', size=16),
        'info': fields.text('Info', size=4000),
        'email': fields.text('Email', size=30),
        'user_to_staff': fields.many2one('res.users', 'Usuaria', required=True),
    }

    _defaults = {
        'state': lambda *a: 'init',
    }       

WizardCreateStaffUsers()
