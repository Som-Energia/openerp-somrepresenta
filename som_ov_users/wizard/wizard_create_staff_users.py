# -*- coding: utf-8 -*-
from osv import osv, fields

class WizardCreateStaffUsers(osv.osv_memory):

    _name = "wizard.create.staff.users"
    _cached_default_values = None

    def default_get(self, cursor, uid, fields, context=None):
        res = super(WizardCreateStaffUsers, self).default_get(cursor, uid, fields, context)

        active_ids = context.get('active_ids')

        res_user_id = active_ids[0] if active_ids else None
        # TODO: Handle None

        if self._cached_default_values is None:  # Ensure we only call init_wizard_create_staff once
            user_obj = self.pool.get("res.users")
            init_data = user_obj.init_wizard_create_staff(cursor, uid, res_user_id)
            self._cached_default_values = res

            res.update({
                'user_to_staff': res_user_id,
            }, **init_data)

        res.update({
            'user_to_staff': res_user_id,
        })

        return res

    def _update_wizard_status(self, cursor, uid, ids, info=''):
        values = {
            'state': 'done',
            'info': info,
        }
        self.write(cursor, uid, ids, values)

    def _validate_vat(self, cursor, uid, vat):
        partner_obj = self.pool.get("res.partner")
        if not partner_obj.is_vat(vat) or vat[:2] != 'ES':
            raise osv.except_osv('Error validant el VAT!', 'El VAT no és vàlid')
        return vat.upper()

    def action_create_staff_users(self, cursor, uid, ids, context=None):
        if context is None: context = {}
        user_obj = self.pool.get("res.users")
        wizard_data = self.browse(cursor, uid, ids[0])
        user_id = wizard_data.user_to_staff.id

        if user_id:
            user = user_obj.browse(cursor, uid, user_id)
            if not user.read():
                self._update_wizard_status(cursor, uid, ids, "No s'ha trobat cap usuaria")
                return True

            process_create_staff_result = user_obj.process_wizard_create_staff(
                cursor, uid, user, wizard_data.vat, wizard_data.email
            )

            self._update_wizard_status(
                cursor, uid, ids, process_create_staff_result.get('info', '')
            )
            return True

        self._update_wizard_status(cursor, uid, ids, "No s'ha trobat cap usuaria")
        return True

    _columns = {
        'state': fields.char('State', size=16),
        'info': fields.text('Info', size=4000),
        'user_to_staff': fields.many2one('res.users', 'Usuaria', required=True),
        'vat': fields.char('VAT', size=20),
        'email': fields.char('Email', size=100),
        'init_error': fields.boolean('Init Error'),
        'init_message': fields.text('Init Message', size=4000),
    }

    _defaults = {
        'state': lambda *a: 'init',
        'init_message': lambda *a: '',
    }

WizardCreateStaffUsers()
