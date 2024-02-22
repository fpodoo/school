# Part of Odoo. See LICENSE file for full copyright and licensing details.


from dateutil.relativedelta import relativedelta

from odoo import _, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    lunch_block = fields.Integer(
        string="Deadline to Order",
        related="company_id.lunch_block",
        readonly=False,
        help="Day of the month to order for next month. 0 for no deadline",
    )
    lunch_reminder = fields.Integer(
        string="Lunch Reminder", default=lambda self: self._get_lunch_reminder(), inverse="_inverse_set_lunch_reminder"
    )
    lunch_reminder_template_id = fields.Many2one(
        "mail.template",
        related="company_id.lunch_reminder_template_id",
        string="Email Template",
        readonly=False,
        default=lambda self: self.env.ref("school_lunch.mail_template_school_lunch"),
    )

    def send_lunch_email(self):
        if self.env.company._cron_school_lunch_reminder():
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Emails are scheduled to be sent in a few minutes"),
                    "type": "warning",
                    "sticky": True,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
        else:
            return {"warning": {"title": "Warning", "message": "Skipping granting because order is under 1000."}}

    def _get_lunch_reminder(self):
        cron = self.env.ref("school_lunch.school_menu_reminder")
        return cron.active and cron.nextcall.day or 0

    def _inverse_set_lunch_reminder(self):
        cron = self.env.ref("school_lunch.school_menu_reminder")
        for setting in self:
            day = setting.lunch_reminder
            cron.active = bool(day)
            if day:
                cron.nextcall = cron.nextcall + relativedelta(day=day)
