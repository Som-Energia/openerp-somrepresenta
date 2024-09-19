# -*- coding: utf-8 -*-
from osv import osv, fields
from tools.translate import _

class ResUsers(osv.osv):
    _inherit = 'res.users'

    def _fnt_is_staff(self, cursor, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = dict.fromkeys(ids, False)
        res_user_obj = self.pool.get('res.users')

        for res_user_id in ids:
            res[res_user_id] = self._is_user_staff(cursor, uid, res_user_obj, res_user_id)

        return res

    def init_wizard_to_turn_into_representation_staff(self, cursor, uid, res_user_id):
        error = None
        user = self.browse(cursor, uid, res_user_id)

        if not user.address_id:
            return dict(
                vat = None,
                email = None,
            )

        if user.is_staff:
            error = "La usuaria ja estàva com a gestora de l'Oficina Virtual de Representa"

        vat = user.address_id.partner_id.vat
        email = user.address_id.partner_id.address[0].email

        return dict(
            dict(error=error) if error else {},
            vat = vat,
            email = email,
        )

    def _is_user_staff(self, cursor, uid, res_user_obj, res_user_id):
        imd_obj = self.pool.get("ir.model.data")
        res_user = res_user_obj.browse(cursor, uid, res_user_id)
        address_id = res_user.address_id
        if not address_id: return False
        partner = address_id.partner_id
        if not partner: return False

        staff_category_id = imd_obj.get_object_reference(
            cursor, uid, "som_ov_users", "res_partner_category_ovrepresenta_staff"
        )[1]
        return any(cat.id == staff_category_id for cat in partner.category_id)

    def _fnt_is_staff_search(self, cursor, uid, obj, name, args, context=None):
        if not context:
            context = {}
        res = []
        ids = self.search(cursor, uid, [])

        selection_value = args[0][2]
        res_user_obj = self.pool.get('res.users')

        for res_user_id in ids:
            is_staff = self._is_user_staff(cursor, uid, res_user_obj, res_user_id)
            if is_staff == selection_value:
                res.append(res_user_id)

        return [('id', 'in', res)]

    _columns = {
        'is_staff': fields.function(
            _fnt_is_staff,
            fnct_search=_fnt_is_staff_search,
            type='boolean',
            method=True,
            string=_('Gestora OV Representa'),
            store=False,
            bold=True,
        )
    }

ResUsers()
