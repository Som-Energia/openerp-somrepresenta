# -*- coding: utf-8 -*-
from osv import osv, fields
from tools.translate import _


class ResUsers(osv.osv):
    _inherit = 'res.users'

    def _fnt_is_staff(self, cursor, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = dict.fromkeys(ids, False)

        for res_user_id in ids:
            res[res_user_id] = self._is_user_staff(cursor, uid, res_user_id)

        return res

    def _validate_vat(self, cursor, uid, vat):
        partner_obj = self.pool.get("res.partner")
        if not partner_obj.is_vat(vat) or vat[:2] != 'ES':
            raise osv.except_osv('Error validant el VAT!',
                                 'El VAT no és vàlid')
        return vat.upper()

    def create_partner_and_address(self, cursor, uid, user_id, name, vat, email):
        partner_obj = self.pool.get("res.partner")
        address_obj = self.pool.get("res.partner.address")
        imd_obj = self.pool.get("ir.model.data")

        cat_staff_id = imd_obj.get_object_reference(
            cursor, uid, "som_ov_users", "res_partner_category_ovrepresenta_staff"
        )[1]

        partner_data = {
            'name': name,
            'vat': self._validate_vat(cursor, uid, vat),
            'lang': 'ca_ES',
            "category_id": [(6, 0, [cat_staff_id])],
        }
        partner_id = partner_obj.create(cursor, uid, partner_data)

        address_data = {
            'name': name,
            'email': email,
            'partner_id': partner_id,
            'street': 'Carrer Pic de Peguera, 9',
            'zip': '17002',
            'city': 'Girona',
            'state_id': 20,
        }
        address_id = address_obj.create(cursor, uid, address_data)
        self.write(cursor, uid, user_id, {'address_id': address_id})

        return partner_id, address_id

    def process_wizard_to_turn_into_representation_staff(self, cursor, uid, user, vat, email):
        name = user.name
        partner_id, address_id = self.create_partner_and_address(
            cursor, uid, user.id, name, vat, email)

        return dict(
            partner_id=partner_id,
            address_id=address_id,
            info="La usuària ha estat convertida en gestora de l'Oficina Virtual de Representa",
        )

    def init_wizard_to_turn_into_representation_staff(self, cursor, uid, res_user_id):
        user = self.browse(cursor, uid, res_user_id)

        def error(message, **kwargs):
            return dict(init_message=message, init_error=True, **kwargs)

        def warning(message, **kwargs):
            return dict(init_message=message, init_error=False, **kwargs)

        if not user.address_id:
            return dict(
                vat = None,
                email = None,
            )

        if not user.address_id.partner_id:
            return error(
                "La usuària té una adreça que no està vinculada a cap persona"
            )

        vat = user.address_id.partner_id.vat
        email = user.address_id.partner_id.address[0].email

        if user.is_staff:
            return error(
                "La usuaria ja estàva com a gestora de l'Oficina Virtual de Representa",
                vat=vat,
                email=email,
            )

        if not vat:
            return error(
                "La persona vinculada per l'adreça de la usuària no té VAT",
            )

        if not email:
            return error(
                "L'adreça primària de la persona vinculada a la usuària no té email",
            )

        res_partner_obj = self.pool.get('res.partner')
        number_of_partners_with_vat = res_partner_obj.search_count(cursor, uid, [
            ('vat', '=', vat),
        ])

        if number_of_partners_with_vat > 1:
            return error(
                "El VAT de la persona vinculada a la usuària, {vat}, està assignat a més persones".format(vat=vat),
            )

        if user.address_id.id != user.address_id.partner_id.address[0].id:
            return warning(
                (
                    "L'adreça vinculada a la usuària, {linked}, "
                    "no serà la que es fará servir a la OV sinó "
                    "la de l'adreça principal de la persona {primary}"
                ).format(
                    linked = user.address_id.email,
                    primary = email,
                ),
                vat=vat,
                email=email,
            )

        return dict(
            vat = vat,
            email = email,
        )

    def _is_user_staff(self, cursor, uid, res_user_id):
        imd_obj = self.pool.get("ir.model.data")
        res_user = self.browse(cursor, uid, res_user_id)
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

        for res_user_id in ids:
            is_staff = self._is_user_staff(cursor, uid, res_user_id)
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
