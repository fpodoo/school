from odoo import fields, models


class GuestReservationWizard(models.TransientModel):
    _name = "guest.reservation.wizard"
    _description = "Réservation des repas pour les invités"

    guest_number = fields.Integer(string="Nombre d'invités", default=1)
    menu_id = fields.Many2one("school_lunch.menu", "Menu", required=True)

    def open_guest_wizard(self):
        wizard_form = self.env.ref("school_lunch.guest_reservation_wizard_form")

        return {
            "name": ("Guest Reservation"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "guest.reservation.wizard",
            "view_id": wizard_form.id,
            "target": "new",
        }

    def process(self):
        guest_id = self.env.ref("school_lunch.kid_guest").id
        for record in self:
            for _ in range(record.guest_number):
                self.env["school_lunch.order"].create(
                    {"kid_id": guest_id, "menu_id": record.menu_id.id, "state": "confirmed"}
                )
