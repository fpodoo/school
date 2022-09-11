# -*- coding: utf-8 -*-

from odoo import models, fields, api

class sale_order_line(models.Model):
    _inherit = "sale.order.line"
    lunch_ids = fields.One2many('school_lunch.order', 'sale_line_id', 'Lunch Orders')

class sale_order(models.Model):
    _inherit = "sale.order"

    def _action_confirm(self):
        for order in self:
            for line in order.order_line:
                if line.lunch_ids:
                    if line.product_uom_qty > len(line.lunch_ids):
                        raise 'Can not order more meals than reserved in the lunch'
                    qty = int(line.product_uom_qty)
                    line.lunch_ids[:qty].write({'state': 'confirmed'})
                    line.lunch_ids[qty:].write({'sale_line_id': False})

    def _action_cancel(self):
        for order in self:
            for line in order.order_line:
                line.lunch_ids.unlink()

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, *args, **kwargs):
        if line_id:
            line = self.env['sale.order.line'].browse(line_id)
            if line.lunch_ids and (set_qty or add_qty):
                if set_qty or bool(add_qty):
                    return {'line_id': line.id, 'quantity': line.product_uom_qty, 'option_ids': []}
        return super(sale_order, self)._cart_update(product_id, line_id, add_qty, set_qty, *args, **kwargs)


class product_product(models.Model):
    _inherit = "product.product"

    def _is_add_to_cart_allowed(self):
        self.ensure_one()
        for mt in ('soup', 'meal'):
            if self.id == self.env.ref('school_lunch.product_'+mt).id:
                return True
        return super(product_product, self)._is_add_to_cart_allowed()

