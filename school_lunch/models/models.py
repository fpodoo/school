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
    meal_type = fields.Selection([('0', 'Soup'), ('1', 'Meal'), ('off', 'Day Off')], 'Meal Type', default="1")
    allergy_ids = fields.Many2many('school_lunch.allergy', string='Allergies')
    order_count = fields.Integer('# of Orders', compute="_compute_count")
    kid_meal_type = fields.Selection([('0', 'Soup'), ('1', 'Meal'), ('off', 'Day Off')], 'Kid Meal', compute="_get_kid_meal", default=False)

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

    @api.depends_context('kid')
    def _get_meal(self):
        if not self.context.get('kid'):
            self.kid_meal_id = False

        orders = self.env['school_lunch.order'].read_group([('kid_id','=',int(self.context['kid'])), ('id','in', self.ids)], ['menu_id'], ['menu_id'])
        print(orders)
        for menu in self:
            menu.kid_meal_type = '1'


class order(models.Model):
    _name = 'school_lunch.order'
    _description = 'Orders'
    _order = "date desc, name"

    name = fields.Char('Kid Name', related='kid_id.name', store=True)
    kid_id = fields.Many2one('school_lunch.kid', 'Kid', required=True)
    menu_id = fields.Many2one('school_lunch.menu', 'Menu', required=True)
    date = fields.Date('Day', related='menu_id.date', index=True, store=True)
    meal_type = fields.Selection(related="menu_id.meal_type", string='Meal Type')

    def order_create(self, data):
        pass


class class_name(models.Model):
    _name = 'school_lunch.class_name'
    _description = 'Class'
    _order = "name"

    name = fields.Char('Class Name', required=True)
    class_type = fields.Selection([('0', 'Maternelle'), ('1', 'Primaire'), ('2', 'Secondaire'), ('3', 'Other')], string='Class Type')
    active = fields.Boolean('Active', default=True)


class kid(models.Model):
    _name = 'school_lunch.kid'
    _description = 'Kid'
    _order = "name"

    firstname = fields.Char('Firstname', required=True)
    lastname = fields.Char('Lastname', required=True)
    name = fields.Char('Name', compute="_fullname_get", store=True)
    shortname = fields.Char('Short Name', compute="_shortname_get")
    parent_id = fields.Many2one('res.partner', "Parent")
    allergy_ids = fields.Many2many('school_lunch.allergy', string='Allergies')
    class_id = fields.Many2one('school_lunch.class_name', 'Class', required=True)

    @api.depends('firstname', 'lastname', 'class_id')
    def _shortname_get(self):
        for kid in self:
            l = 0
            while len(self.search([('firstname','=',kid.firstname), ('class_id','=',kid.class_id.id), ('lastname', '=like', kid.lastname[:l]+'%')])) > 1:
                if l>=len(kid.lastname):
                    break
                l += 1
            kid.shortname = kid.firstname + ' ' + (l and (kid.lastname[:l] + '. ') or '')  + '(' + kid.class_id.name + ')'

    @api.depends('firstname', 'lastname', 'class_id')
    def _fullname_get(self):
        for kid in self:
            kid.name = kid.firstname + ' ' + kid.lastname


