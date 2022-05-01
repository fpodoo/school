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
    date = fields.Date('Day', index=True, required=True)
    color = fields.Integer()
    meal_type = fields.Selection([('0', 'Soup'), ('1', 'Meal'), ('2', 'Dessert'), ('off', 'Day Off')], 'Meal Type')
    allergy_ids = fields.Many2many('school_lunch.allergy', string='Allergies')

    # @api.depends('value')
    # def _value_pc(self):
    #     for record in self:
    #         record.value2 = float(record.value) / 100

