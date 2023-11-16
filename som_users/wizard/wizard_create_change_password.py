# -*- coding: utf-8 -*-
from osv import osv, fields
import random
import string
import requests
import json
from tools import config
from datetime import datetime

from som_users.exceptions import FailSendEmail

class WizardCreateChangePassword(osv.osv_memory):

    """Classe per gestionar el canvi de contrassenya
    """

    _name = "wizard.create.change.password"


    def default_get(self, cursor, uid, fields, context=None):
        res = super(WizardCreateChangePassword, self).default_get(cursor, uid, fields, context)

        partner_obj = self.pool.get('res.partner')
        active_ids = context.get('active_ids')

        info = '{} ({}): \n{}'.format(
            'Es generarant contrassenyes pels següents partners',
            len(active_ids),
            '\n'.join([partner_obj.read(cursor, uid, x, ['name'])['name'] for x in active_ids])
            )

        res.update({
            'initial_info': info,
        })
        return res

    def generatePassword(self):
        # Generate a list of random characters
        characters = [random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(10)]
        # Shuffle the list of characters
        random.shuffle(characters)
        # Return the shuffled list of characters as a string
        return ''.join(characters)

    def send_password_email(self, cursor, uid, partner):
        ir_model_data = self.pool.get('ir.model.data')
        power_email_tmpl_obj = self.pool.get('poweremail.templates')

        template_id = ir_model_data.get_object_reference(
            cursor, uid, 'som_users', 'email_create_change_password'
        )[1]
        template = power_email_tmpl_obj.read(cursor, uid, template_id)

        account_obj = self.pool.get('poweremail.core_accounts')

        email_from = False
        email_account_id = 'info@somenergia.coop'
        if template.get('enforce_from_account', False):
            email_from = template.get('enforce_from_account')[0]
        if not email_from:
            email_from = account_obj.search(cursor, uid, [('email_id', '=', email_account_id)])[0]

        try:
            wiz_send_obj = self.pool.get('poweremail.send.wizard')
            ctx = {
                'active_ids': [partner.id],
                'active_id': partner.id,
                'template_id': template_id,
                'src_model': 'res.partner',
                'src_rec_ids': [partner.id],
                'from': email_from,
                'state': 'single',
                'priority': '0',
            }
            params = {'state': 'single', 'priority': '0', 'from': ctx['from']}
            wiz_id = wiz_send_obj.create(cursor, uid, params, ctx)
            wiz_send_obj.send_mail(cursor, uid, [wiz_id], ctx)

        except Exception as e:
            raise FailSendEmail(e.message)


    def save_password(self, cursor, uid, partner_id, password):
        partner_o = self.pool.get("res.partner")
        try:
            nif = partner_o.read(cursor, uid, partner_id, ['vat'])['vat']
            data = {
                "username": nif,
                "password": password
            }
            headers = {
                'Accept': 'application/json',
                'X-API-KEY': config.get('api_key_ov_representa', False)
            }
            url = config.get('api_url_ov_representa', False)

            res = requests.post(url, data=json.dumps(data), headers=headers)
            return res.status_code == 200
        except Exception as e:
            return False

    def add_password_to_partner_comment(self, cursor, uid, partner_id, password):
        partner_o = self.pool.get("res.partner")
        comment = partner_o.read(cursor, uid, partner_id, ['comment'])['comment']
        key = 'generated_ov_password'

        now = datetime.now()
        new_comment = '{}:{}({})\n'.format(key, password, now)

        if comment:
            comments = comment.split('\n')

            #remove old password
            comment = [x for x in comments if not key in x]
            new_comment = '{}{}'.format(new_comment, '\n'.join(comment))

        partner_o.write(cursor, uid, partner_id, {'comment': new_comment})


    def action_create_change_password(self, cursor, uid, ids, context=None):
        if context is None:
            context = {}

        partner_ids = context.get("active_ids")
        partner_o = self.pool.get("res.partner")

        error_info = []
        for partner_id in partner_ids:
            partner = partner_o.browse(cursor, uid, partner_id)
            password = self.generatePassword()
            result = self.save_password(cursor, uid, partner_id, password)
            if not result:
                info = "{} ({})\n".format(str(int(partner_id)),'Error al guardar la contrasseya')
                error_info.append(info)
                continue
            self.add_password_to_partner_comment(cursor, uid, partner_id, password)
            try:
                self.send_password_email(cursor, uid, partner)
            except FailSendEmail as e:
                info = "{} ({})\n".format(str(int(partner_id)),"Error al generar/enviar l'email")
                error_info.append(info)
                continue

        values = {
            'state': 'done'
        }

        if error_info:
            values['info'] = "{}: \n {}".format(
                'Error generant contrassenyes pels següents partners',
                ','.join([x for x in error_info])
            )
        else:
            values['info'] = "{}".format('Contrassenyes generades')

        self.write(cursor, uid, ids, values)
        return True

    _columns = {
        'state': fields.char('State', size=16),
        'info': fields.text('Info', size=4000),
        'initial_info': fields.text('Initial info', size=4000),
    }

    _defaults = {
        'state': lambda *a: 'init',
    }

WizardCreateChangePassword()