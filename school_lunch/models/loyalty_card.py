from odoo import fields, models


class LoyaltyCard(models.Model):
    _inherit = "loyalty.card"

    comment = fields.Text("Comment")
    is_sent = fields.Boolean("Is Sent", default=False)
