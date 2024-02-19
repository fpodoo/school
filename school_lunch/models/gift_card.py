from odoo import fields, models


class GiftCard(models.Model):
    _inherit = "gift.card"

    comment = fields.Text("Comment")
    is_sent = fields.Boolean("Is Sent", default=False)
