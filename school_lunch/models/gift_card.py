from odoo import api, fields, models


class gift_card(models.Model):
    _inherit = "gift.card"

    comment = fields.Text("Comment")
    is_sent = fields.Boolean("Is Sent", default=False)
