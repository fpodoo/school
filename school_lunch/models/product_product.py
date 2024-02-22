from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _is_add_to_cart_allowed(self):
        self.ensure_one()
        for mt in ("soup", "meal"):
            if self.id == self.env.ref("school_lunch.product_" + mt).id:
                return True
        return super()._is_add_to_cart_allowed()
