from odoo import models
from odoo.http import request


class Website(models.Model):
    _inherit = "website"

    def _get_current_pricelist(self):
        # Lunch carts are priced from the kids' pricelist, not from the parent's pricelist
        pricelist = self._school_lunch_kids_pricelist()
        return pricelist or super()._get_current_pricelist()

    def _school_lunch_kids_pricelist(self):
        if not request:
            return self.env["product.pricelist"]
        kids = self.env["school_lunch.kid"].sudo().browse(request.session.get("mykids", [])).exists()
        pricelists = kids.pricelist_id | kids.filtered(lambda kid: not kid.pricelist_id).class_id.pricelist_id
        if len(pricelists) == 1 and pricelists._is_available_on_website(self):
            return pricelists
        return self.env["product.pricelist"]
