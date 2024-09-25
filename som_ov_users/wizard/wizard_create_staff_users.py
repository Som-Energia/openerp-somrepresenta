# -*- coding: utf-8 -*-
from osv import osv, fields

class WizardCreateStaffUsers(osv.osv_memory):

    _name = "wizard.create.staff.users"

    def default_get(self, cursor, uid, fields, context=None):
        res = super(WizardCreateStaffUsers, self).default_get(cursor, uid, fields, context)

        active_ids = context.get('active_ids')

        res_user_id = active_ids[0] if active_ids else None
        # TODO: Handle None

        user_obj = self.pool.get("res.users")
        init_data = user_obj.init_wizard_to_turn_into_representation_staff(cursor, uid, res_user_id)

        res.update({
            'user_to_staff': res_user_id,
        }, **init_data)

        return res

    def _update_wizard_status(self, cursor, uid, ids, state, info=''):
        values = {
            'state': state,
            'info': info,
        }
        self.write(cursor, uid, ids, values)

    def _create_partner_and_address(self, cursor, uid, wizard_data):
        partner_obj = self.pool.get("res.partner")
        address_obj = self.pool.get("res.partner.address")
        imd_obj = self.pool.get("ir.model.data")

        cat_staff_id = imd_obj.get_object_reference(
            cursor, uid, "som_ov_users", "res_partner_category_ovrepresenta_staff"
        )[1]

        partner_data = {
            'name': wizard_data.user_to_staff.name,
            'vat': self._validate_vat(cursor, uid, wizard_data.vat),
            'lang': 'ca_ES',
            "category_id": [(6, 0, [cat_staff_id])],
        }
        partner_id = partner_obj.create(cursor, uid, partner_data)

        address_data = {
            'name': wizard_data.user_to_staff.name,
            'email': wizard_data.email,
            'partner_id': partner_id,
            'street': 'Carrer Pic de Peguera, 9',
            'zip': '17002',
            'city': 'Girona',
            'state_id': 20,
        }
        address_id = address_obj.create(cursor, uid, address_data)

        return address_id

    def _validate_vat(self, cursor, uid, vat):
        partner_obj = self.pool.get("res.partner")
        if not partner_obj.is_vat(vat) or vat[:2] != 'ES':
            raise osv.except_osv('Error validant el VAT!', 'El VAT no és vàlid')
        return vat.upper()

    def action_create_staff_users(self, cursor, uid, ids, context=None):
        if context is None:
            context = {}

        user_obj = self.pool.get("res.users")

        wizard_data = self.browse(cursor, uid, ids[0])
        user_id = wizard_data.user_to_staff.id

        if user_id:
            user = user_obj.browse(cursor, uid, user_id)
            if not user.read():
                self._update_wizard_status(cursor, uid, ids, 'done', "No s'ha trobat cap usuaria")
                return True

            if not user['address_id']:
                address_id = self._create_partner_and_address(cursor, uid, wizard_data)
                user_obj.write(cursor, uid, user_id, {'address_id': address_id})
                self._update_wizard_status(
                    cursor, uid, ids, 'done',
                    "S'ha creat la usuaria gestora per l'Oficina Virtual de Representació"
                )
                return True

            if user['address_id']:
                self._update_wizard_status(
                    cursor, uid, ids, 'done',
                    "Aquesta usuaria ja és gestora de l'Oficina Virtual de Representació"
                )
                return True

        self._update_wizard_status(cursor, uid, ids, 'done', "No s'ha trobat cap usuaria")
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
