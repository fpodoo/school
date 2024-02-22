from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    lunch_reminder_template_id = fields.Many2one("mail.template", string="Lunch Reminder Email")
    lunch_signin = fields.Boolean(
        "Force Sign In", help="Force users to sign in to add children in their session", default=True
    )
    lunch_block = fields.Integer(string="Deadline to Order", default=26)

    def _cron_school_lunch_reminder(self):
        menu = self.env["school_lunch.menu"]
        if not menu.search_count(
            [
                ("date", ">=", date.today() + relativedelta(months=1, day=1)),
                ("date", "<", date.today() + relativedelta(months=2, day=1)),
            ]
        ):
            return False
        partners = (
            self.env["res.partner"]
            .search([("kid_ids", "!=", False), ("email", "ilike", "%")])
            .filtered(lambda p: any(p.mapped("kid_ids.active")))
        )
        return partners._school_lunch_mail()
