# -*- coding: utf-8 -*-

from odoo import models, fields, api

class allergy(models.Model):
    _name = 'school_lunch.allergy'
    _description = 'Allergies'
    _order = "code"

    name = fields.Char(required=True)
    code = fields.Integer()


class menu(models.Model):
    _name = 'school_lunch.menu'
    _description = 'Daily Menu'
    _order = "date, meal_type"

    name = fields.Char("Meal Title", required=True)
    description = fields.Char()
    cook_id = fields.Many2one('res.partner', 'Cuisinier')
    order_ids = fields.One2many('school_lunch.order', 'menu_id', string='Orders')
    date = fields.Date('Day', index=True, required=True)
    color = fields.Integer()
    meal_type = fields.Selection([('0', 'Soup'), ('1', 'Meal'), ('off', 'Day Off')], 'Meal Type')
    allergy_ids = fields.Many2many('school_lunch.allergy', string='Allergies')
    order_count = fields.Integer('Orders', compute="_compute_count")

    @api.depends('order_ids.menu_id')
    def _compute_count(self):
        for record in self:
            record.order_count = len(record.order_ids)

    @api.depends('name', 'date')
    def name_get(self):
        result = []
        for menu in self:
            result.append((menu.id, menu.date.strftime('%A, %d %b %Y') + ': ' + menu.name))
        return result


class order(models.Model):
    _name = 'school_lunch.order'
    _description = 'Orders'
    _order = "date desc, name"

    name = fields.Char('Kid Name', required=True)
    kid_id = fields.Many2one('res.partner', "Kid")
    menu_id = fields.Many2one('school_lunch.menu', 'Menu', required=True)
    date = fields.Date('Day', related='menu_id.date', index=True, store=True)
    meal_type = fields.Selection([('0', 'Soup'), ('1', 'Meal'), ('off', 'Day Off')], related="menu_id.meal_type", string='Meal Type')



class class_name(models.Model):
    _name = 'school_lunch.class_name'
    _description = 'Class'
    _order = "name"

    name = fields.Char('Class Name', required=True)
    class_type = fields.Selection([('0', 'Maternelle'), ('1', 'Primaire'), ('2', 'Secondaire'), ('3', 'Other')], string='Class Type')


