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
            for line in order:
                line.lunch_ids.unlink()

