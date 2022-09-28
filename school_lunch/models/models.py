# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import uuid

class allergy(models.Model):
    _name = 'school_lunch.allergy'
    _description = 'Allergies'
    _order = "code"

    name = fields.Char(required=True)
    code = fields.Integer()


class menu(models.Model):
    _name = 'school_lunch.menu'
    _description = 'Daily Menu'
    _order = "date desc, meal_type"

    name = fields.Char("Meal Title", required=True)
    description = fields.Char()
    cook_id = fields.Many2one('res.partner', 'Cuisinier')
    weekday = fields.Selection([('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')], compute="_get_weekday")
    weekyear = fields.Integer('Week of Year', compute="_get_weekday")
    order_ids = fields.One2many('school_lunch.order', 'menu_id', string='Orders')
    date = fields.Date('Day', index=True, required=True, default=lambda self: self._default_date())
    color = fields.Integer()
    meal_type = fields.Selection([('soup', 'Soup'), ('meal', 'Meal'), ('off', 'Day Off')], 'Meal Type', default=lambda self: self._default_meal())
    allergy_ids = fields.Many2many('school_lunch.allergy', string='Allergies')
    order_count = fields.Integer('# of Orders', compute="_compute_count")
    kid_meal_type = fields.Selection([('0', 'Soup'), ('1', 'Meal'), ('off', 'Day Off')], 'Kid Meal', compute="_get_kid_meal", default=False)

    def _default_date(self):
        latest = self.search([], limit=1)
        if latest.meal_type=='meal':
            skip = {1: 2, 4: 3}.get(latest.date.weekday(), 1)
            rt = relativedelta(days=skip)
            return latest.date+rt
        else:
            return latest.date

    def _default_meal(self):
        latest = self.search([], limit=1)
        if latest.meal_type=='meal':
            return 'soup'
        else:
            return 'meal'

    @api.depends('order_ids.menu_id')
    def _compute_count(self):
        for record in self:
            record.order_count = len(record.order_ids)

    @api.depends('name', 'date')
    def name_get(self):
        result = []
        for menu in self:
            if self.env.context.get('display', 'date') == 'simple':
                result.append((menu.id, menu.name))
            elif self.env.context.get('display', 'date') == 'description':
                result.append((menu.id, menu.name + (menu.description and (' - ' + menu.description) or '')))
            else:
                result.append((menu.id, menu.date.strftime('%A, %d %b %Y') + ': ' + menu.name))
        return result

    @api.depends('date')
    def _get_weekday(self):
        for record in self:
            if not record.date:
                record.weekday = False
                record.weekyear = False
                return True
            record.weekday = str(record.date.weekday())
            record.weekyear = record.date.isocalendar()[1]

    @api.depends_context('kid')
    def _get_meal(self):
        if not self.context.get('kid'):
            self.kid_meal_id = False
        orders = self.env['school_lunch.order'].read_group([('kid_id','=',int(self.context['kid'])), ('id','in', self.ids)], ['menu_id'], ['menu_id'])
        for menu in self:
            menu.kid_meal_type = '1'


class order(models.Model):
    _name = 'school_lunch.order'
    _description = 'Orders'
    _order = "date desc, name"

    name = fields.Char('Kid Name', related='kid_id.name', store=True)
    kid_id = fields.Many2one('school_lunch.kid', 'Kid', required=True)
    class_id = fields.Many2one('school_lunch.class_name', string='Class', related="kid_id.class_id", store=True)
    menu_id = fields.Many2one('school_lunch.menu', 'Menu', required=True)
    date = fields.Date('Day', related='menu_id.date', index=True, store=True)
    meal_type = fields.Selection(related="menu_id.meal_type", string='Meal Type', store=True)
    color = fields.Integer('Color', compute="_get_color")
    sale_line_id = fields.Many2one('sale.order.line', 'Sale Order Line', ondelete="cascade")
    state = fields.Selection([('draft','Draft'), ('confirmed','Confirmed')], 'State', default='draft')
    class_type = fields.Selection(related='class_id.class_type', string='Class Type', store=True)


    @api.depends('meal_type')
    def _get_color(self):
        for order in self:
            order.color = {
                'meal': 2,
                'soup': 3,
                'off': 4,
            }.get(order.meal_type, 1)

    def order_create(self, data):
        pass


class class_name(models.Model):
    _name = 'school_lunch.class_name'
    _description = 'Class'
    _order = "name"

    name = fields.Char('Class Name', required=True)
    class_type = fields.Selection([('0', 'Maternelle'), ('1', 'Primaire'), ('2', 'Secondaire'), ('3', 'Other')], string='Class Type')
    active = fields.Boolean('Active', default=True)
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist")


class kid(models.Model):
    _name = 'school_lunch.kid'
    _description = 'Kid'
    _order = "name"

    firstname = fields.Char('Firstname', required=True)
    lastname = fields.Char('Lastname', required=True)
    name = fields.Char('Name', compute="_fullname_get", store=True)
    shortname = fields.Char('Short Name', compute="_shortname_get")
    parent_ids = fields.Many2many('res.partner', 'school_lunch_kid_partner_rel', 'kid_id', 'partner_id', "Parents")
    allergy_ids = fields.Many2many('school_lunch.allergy', string='Allergies')
    class_id = fields.Many2one('school_lunch.class_name', 'Class', required=True)
    unblock_date = fields.Date('Allow Order Until')
    uuid = fields.Char('UUID', default=lambda x: str(uuid.uuid4()), copy=False)
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist")
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('uuid_uniq', 'unique(uuid)', 'UUID field must be unique per kid!'),
    ]

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

class partner(models.Model):
    _inherit = 'res.partner'

    kid_ids = fields.Many2many('school_lunch.kid', 'school_lunch_kid_partner_rel', 'partner_id', 'kid_id', 'Kids')
    lunch_url = fields.Char('Lunch URL', compute="_get_lunch_url")

    @api.depends('kid_ids.uuid')
    def _get_lunch_url(self):
        for partner in self:
            if not partner.kid_ids:
                partner.lunch_url = False
                continue
            base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            partner.lunch_url = base + '/school/kid/add/' + ','.join(partner.kid_ids.mapped('uuid')) + '/' + str(partner.id)

    def school_lunch_mail(self):
        return self._school_lunch_mail(force_send=True)

    def _school_lunch_mail(self, force_send=False):
        for partner in self:
            template = self.env.ref("school_lunch.mail_template_school_lunch")
            template.send_mail(partner.id, force_send=force_send)
        return True

