from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    lunch_ids = fields.One2many("school_lunch.order", "sale_line_id", "Lunch Orders")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    kid_id = fields.Many2one("school_lunch.kid", string="Oldest Kid", compute="_compute_first_kid", store=True)
    kid_ids = fields.Many2many("school_lunch.kid", string="Kids", related="partner_id.kid_ids")

    @api.depends("partner_id.kid_ids")
    def _compute_first_kid(self):
        for order in self:
            kids = order.partner_id.kid_ids
            if order.partner_id.kid_ids:
                kids = sorted(kids, key=lambda x: (x.class_id.name, x.name))
                order.kid_id = kids[-1]
            else:
                order.kid_id = False
        return True

    def _action_confirm(self):
        for order in self:
            for line in order.order_line:
                if line.lunch_ids:
                    if line.product_uom_qty > len(line.lunch_ids):
                        raise "Can not order more meals than reserved in the lunch"
                    qty = int(line.product_uom_qty)
                    line.lunch_ids[:qty].write({"state": "confirmed"})
                    line.lunch_ids[qty:].write({"sale_line_id": False})
        return super()._action_confirm()

    def _action_cancel(self):
        for order in self:
            for line in order.order_line:
                line.lunch_ids.unlink()
        return super()._action_cancel()

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, *args, **kwargs):
        if line_id:
            line = self.env["sale.order.line"].browse(line_id)
            if line.lunch_ids:
                if set_qty or (add_qty is not None):
                    return {"line_id": line.id, "quantity": line.product_uom_qty, "option_ids": []}
        return super()._cart_update(product_id, line_id, add_qty, set_qty, *args, **kwargs)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _is_add_to_cart_allowed(self):
        self.ensure_one()
        for mt in ("soup", "meal"):
            if self.id == self.env.ref("school_lunch.product_" + mt).id:
                return True
        return super()._is_add_to_cart_allowed()
