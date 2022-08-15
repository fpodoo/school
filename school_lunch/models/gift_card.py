# -*- coding: utf-8 -*-

from odoo import models, fields, api

class gift_card(models.Model):
    _inherit = 'gift.card'

    comment = fields.Text('Comment')
    is_sent = fields.Boolean('Is Sent', default=False)

