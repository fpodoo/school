# Part of Odoo. See LICENSE file for full copyright and licensing details.

# This module can be removed when upgrading to v16

from odoo import models



class EventRegistrationAnswer(models.Model):
    _inherit = "event.registration.answer"
    _rec_name = "value_answer_id"
