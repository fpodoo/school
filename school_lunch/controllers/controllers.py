# -*- coding: utf-8 -*-

from odoo import http
import datetime
from odoo.http import request
import time
from dateutil.relativedelta import relativedelta
import pprint

FMT = '%A, %d %b %Y'

class SchoolLunch(http.Controller):
    @http.route(['/menu', '/menu/<int:date>'], auth='public', type='http', website=True)
    def menu(self, date=None, **kw):
        date = datetime.datetime.fromtimestamp(date or time.time())

        dt_from = date + relativedelta(day=1)
        dt_to = date + relativedelta(day=1, months=1) - datetime.timedelta(days=1)

        menus = request.env['school_lunch.menu'].search([('date','>=', dt_from.strftime('%Y-%m-%d')), ('date', "<=", dt_to.strftime('%Y-%m-%d'))])
        allergies = request.env['school_lunch.menu'].read_group([('date','>=', dt_from.strftime('%Y-%m-%d')), ('date', "<=", dt_to.strftime('%Y-%m-%d'))], ['allergy_ids'], ['allergy_ids'])
        allergies = filter(None, list(map(lambda x: x['allergy_ids'], allergies)))
        allergies = request.env['school_lunch.allergy'].browse(map(lambda x: x[0], allergies))
        return http.request.render('school_lunch.menu', {
            'date': date,
            'menus': menus,
            'dmonth': relativedelta(months=1),
            'kids': request.env['school_lunch.kid'].browse(request.session.get('mykids', [])),
            'allergies': allergies
        })

    @http.route(['/school/kids'], auth='public', type='http', website=True)
    def school_kids(self, date=None, **kw):
        classes = request.env['school_lunch.class_name'].search([])
        kids = request.env['school_lunch.kid'].search([])
        my_kids = request.env['school_lunch.kid'].browse(request.session.get('mykids', []))
        return http.request.render('school_lunch.kids', {
            'classes': classes,
            'kids': kids,
            'my_kids': my_kids,
        })

    @http.route(['/school/kid/add'], auth='public', type='http', website=True, methods=["POST"])
    def school_kid_add(self, kid_id, **kw):
        d = request.session.get('mykids', [])
        d.append(int(kid_id))
        request.session['mykids'] = d
        return request.redirect('/menu')

    @http.route(['/school/kid/remove/<int:kid_id>'], auth='public', type='http', website=True)
    def school_kid_remove(self, kid_id, **kw):
        d = request.session.get('mykids', [])
        d.remove(int(kid_id))
        request.session['mykids'] = d
        return request.redirect('/menu')

    @http.route(['/school/order_set'], type="json", auth="public", website=True, methods=["POST"])
    def school_order_set(self, orders, **kwargs):
        if not orders:
            return False
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)
        sale_order.order_line = [(6, 0, [])]

        menus = request.env['school_lunch.menu'].browse(map(int, orders.keys()))
        meals = {}            # {meal_type: [(menu_id, kid_id)] }
        for menu in menus:
            for kid in orders[str(menu.id)]:
                meals.setdefault(menu.meal_type, [])
                meals[menu.meal_type].append((menu.id, kid))

        for meal_type, orders in meals.items():
            product_id = request.env.ref('school_lunch.product_'+meal_type)
            line_id = sale_order._cart_update(
                product_id=product_id.id,
                set_qty=len(orders)
            )['line_id']
            for order in orders:
                request.env['school_lunch.order'].create({
                    'sale_line_id': line_id,
                    'menu_id': order[0],
                    'kid_id': order[1]
                })

        return True

    @http.route(['/school/order_prepare'], type="json", auth="public", website=True, methods=["POST"])
    def school_order_prepare(self, date=None, **kwargs):

        date = datetime.datetime.fromtimestamp(date or time.time())
        dt_from = date + relativedelta(day=1)
        dt_to = date + relativedelta(day=1, months=1) - datetime.timedelta(days=1)
        kids = request.env['school_lunch.kid'].browse(request.session.get('mykids', []))
        allergies = request.env['school_lunch.allergy'].search([])


        menus = request.env['school_lunch.menu'].search([('date','>=', dt_from.strftime('%Y-%m-%d')), ('date', "<=", dt_to.strftime('%Y-%m-%d'))])
        result = {
            'kids': [{'id': kid.id, 'shortname': kid.shortname} for kid in kids],
            'allergies': [{'id': al.id, 'name': al.name} for al in allergies],
            'menus': []
        }
        for menu in menus:
            if (not len(result['menus'])) or (result['menus'][-1]['date'] != menu.date.strftime(FMT)):
                result['menus'].append({
                    'date': menu.date.strftime(FMT),
                    'day_of_week': menu.date.weekday()+1,
                    'meals': []
                })
            result['menus'][-1]['meals'].append({
                'id': menu.id,
                'meal_type': menu.meal_type,
                'state': 'active',
                'name': menu.name,
                'allergies': [{'id': a.id, 'name': a.name} for a in menu.allergy_ids],
                'kids': []
            } )
        return result

