from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    kid_ids = fields.Many2many("school_lunch.kid", "school_lunch_kid_partner_rel", "partner_id", "kid_id", "Kids")
    lunch_url = fields.Char("Lunch URL", compute="_compute_lunch_url")

    @api.depends("kid_ids.uuid")
    def _compute_lunch_url(self):
        for partner in self:
            if not partner.kid_ids:
                partner.lunch_url = False
                continue
            base = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            partner.lunch_url = (
                base + "/school/kid/add/" + ",".join(partner.kid_ids.mapped("uuid")) + "/" + str(partner.id)
            )

    def school_lunch_mail(self):
        return self._school_lunch_mail(force_send=True)

    def _school_lunch_mail(self, force_send=False):
        for partner in self:
            template = self.env.ref("school_lunch.mail_template_school_lunch")
            template.send_mail(partner.id, force_send=force_send)
        return True
