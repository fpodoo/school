# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, exceptions, fields, models, _


class resCompany(models.Model):
    _inherit = 'res.company'

    lunch_reminder_template_id = fields.Many2one('mail.template', string="Lunch Reminder Email")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    lunch_block = fields.Integer(string="Deadline to Order", config_parameter='school_lunch.lunch_block', default=26)
    lunch_reminder = fields.Integer(string="Lunch Reminder", config_parameter='school_lunch.lunch_reminder', default=20)
    lunch_reminder_template_id = fields.Many2one('mail.template', related="company_id.lunch_reminder_template_id", string="Email Template")
