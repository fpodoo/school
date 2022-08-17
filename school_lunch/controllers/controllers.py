# -*- coding: utf-8 -*-

from odoo import http, _
import datetime
from odoo.http import request
import time
from dateutil.relativedelta import relativedelta
from collections import defaultdict

WEEKDAYS = {
    '0': _('Monday'),
    '1': _('Tuesday'),
    '2': _('Wednesday'),
    '3': _('Thursday'),
    '4': _('Friday'),
    '5': _('Saturday'),
    '6': _('Sunday')
}

class SchoolLunch(http.Controller):
    @http.route(['/menu', '/menu/<int:date>'], auth='public', type='http', website=True)
    def menu(self, date=None, **kw):
        dt = datetime.datetime.fromtimestamp(date or time.time())
        if not date:
            try:
                cron = request.env.ref('school_lunch.school_menu_reminder')
                if dt.day >= (cron.active and cron.nextcall.day or 1):
                    dt += relativedelta(months=1)
            except:
                pass
        return http.request.render('school_lunch.menu', {
            'date': dt,
            'timestamp': int(dt.timestamp()),
            'dmonth': relativedelta(months=1),
            'kids': request.env['school_lunch.kid'].browse(request.session.get('mykids', [])),
        })

    @http.route(['/menu/agenda', '/menu/agenda/<int:date>'], auth='public', type='http', website=True)
    def menu_agenda(self, date=None, **kw):
        dt = datetime.datetime.fromtimestamp(date or time.time())
        dt_from = dt + relativedelta(day=1)
        dt_to = dt + relativedelta(day=1, months=1) - datetime.timedelta(days=1)


        menus = request.env['school_lunch.menu'].search([('date','>=', dt_from.strftime('%Y-%m-%d')), ('date', "<=", dt_to.strftime('%Y-%m-%d'))], order="date asc, meal_type desc")
        allergy_ids = set([al.id for m in menus for al in m.allergy_ids])
        allergies = request.env['school_lunch.allergy'].browse(list(allergy_ids))

        calendar = defaultdict(lambda : defaultdict(list))
        weekdays = list(set([menu.date.weekday() for menu in menus]))
        latest = None
        weekdays.sort()
        for menu in menus:
            calendar[menu.date.isocalendar()[1]][menu.date.weekday()].append( menu )
            latest = menu.date.day
        return http.request.render('school_lunch.website_menu_calendar', {
            'allergies': allergies,
            'calendar': calendar,
            'dmonth': relativedelta(months=1),
            'weekdays': weekdays,
            'latest_day': latest,
            'date': dt
        })

    @http.route(['/school/kids'], auth='public', type='http', website=True)
    def school_kids(self, date=None, **kw):
        if request.env.company.lunch_signin:
            return request.redirect('/menu')
        request.env['school_lunch.class_name'].search([])
        classes = request.env['school_lunch.class_name'].search([])
        kids = request.env['school_lunch.kid'].search([])
        my_kids = request.env['school_lunch.kid'].browse(request.session.get('mykids', []))
        return http.request.render('school_lunch.kids', {
            'classes': classes,
            'kids': kids,
            'my_kids': my_kids,
        })

    @http.route(['/school/kid/add'], auth='public', type='http', website=True, methods=["POST"])
    def school_kid_add(self, kid_id=None, **kw):
        if request.env.company.lunch_signin:
            return request.redirect('/menu')
        if not kid_id:
            return request.redirect('/school/kids')
        kid_id = int(kid_id)
        d = request.session.get('mykids', [])
        if kid_id not in d:
            d.append(int(kid_id))
        request.session['mykids'] = d
        return request.redirect('/school/kids')

    @http.route(['/school/kid/add/<string:uuids>', '/school/kid/add/<string:uuids>/<int:partner_id>'], auth='public', type='http', website=True)
    def school_kid_add(self, uuids, partner_id=None, **kw):
        kids = request.env['school_lunch.kid'].search([('uuid', 'in', uuids.split(','))]).sudo()
        request.session['mykids'] = kids.mapped('id')
        for k in kids:
            for parent in k.parent_ids:
                if parent.id == partner_id:
                    request.session['school_partner_id'] = partner_id
        return request.redirect('/menu')

    @http.route(['/school/kid/remove/<int:kid_id>'], auth='public', type='http', website=True)
    def school_kid_remove(self, kid_id, **kw):
        d = request.session.get('mykids', [])
        d.remove(int(kid_id))
        request.session['mykids'] = d
        return request.redirect('/school/kids')

    @http.route(['/school/order_set'], type="json", auth="public", website=True, methods=["POST"])
    def school_order_set(self, orders, **kwargs):
        if not orders:
            return False
        sale_order = request.website.sale_get_order(force_create=True)
        if request.session.get('school_partner_id'):
            sale_order.partner_id = request.session['school_partner_id']
            sale_order.partner_invoice_id = request.session['school_partner_id']
            sale_order.partner_shipping_id = request.session['school_partner_id']
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)
        sale_order.order_line = sale_order.order_line.filtered(lambda line: not line.lunch_ids)

        menus = request.env['school_lunch.menu'].browse(map(int, orders.keys()))
        meals = {}            # {meal_type: [(menu_id, kid_id)] }
        for menu in menus:
            for kid in orders[str(menu.id)]:
                product = request.env.ref('school_lunch.product_'+menu.meal_type).sudo()
                price = product.lst_price
                kid_o = request.env['school_lunch.kid'].browse(kid)
                pricelist = kid_o.pricelist_id or kid_o.class_id.pricelist_id
                if pricelist:
                    result = pricelist.get_product_price(product, 1, False)
                    price = result
                key = (menu.meal_type, product, price)
                meals.setdefault(key, [])
                meals[key].append((menu.id, kid))

        for (meal_type, product, price), orders in meals.items():
            so = sale_order.sudo()
            line_id = request.env['sale.order.line'].sudo().create({
                'product_id': product.id,
                'tax_id': product.taxes_id,
                'name': product.name,
                'product_uom_qty': len(orders),
                'product_uom': product.uom_id.id,
                'price_unit': price,
                'order_id': so.id
            })
            for order in orders:
                request.env['school_lunch.order'].sudo().create({
                    'sale_line_id': line_id.id,
                    'menu_id': order[0],
                    'kid_id': order[1]
                })

        return True

    @http.route(['/school/order_prepare'], type="json", auth="public", website=True, methods=["POST"])
    def school_order_prepare(self, date=None, **kwargs):
        max_day = request.env.company.lunch_block
        cron = request.env.ref('school_lunch.school_menu_reminder')
        alert_day = cron.sudo().active and cron.sudo().nextcall.day or 20

        now = datetime.datetime.now()
        max_date = now + relativedelta(months = (now.day <= max_day) and 1 or 2, day=1)

        date = datetime.datetime.fromtimestamp(date and int(date) or max_date.timestamp())
        dt_from = date + relativedelta(day=1)
        dt_to = date + relativedelta(day=1, months=1) - datetime.timedelta(days=1)
        kids = request.env['school_lunch.kid'].browse(request.session.get('mykids', []))
        kid_ids = kids.ids

        menus = request.env['school_lunch.menu'].search([('date','>=', dt_from.strftime('%Y-%m-%d')), ('date', "<=", dt_to.strftime('%Y-%m-%d'))], order="date, meal_type")
        allergy_ids = set([al.id for m in menus for al in m.allergy_ids])
        allergies = request.env['school_lunch.allergy'].search([('id', 'in', list(allergy_ids))])

        unblock = False
        for kid in kids:
            if kid.unblock_date and kid.unblock_date >= datetime.date.today():
                unblock = True
        signin = request.env.company.lunch_signin
        result = {
            'kids': [{'id': kid.id, 'shortname': kid.shortname} for kid in kids],
            'allergies': [{'id': al.id, 'name': al.name, 'code': al.code} for al in allergies],
            'readonly': (date<=max_date) and not unblock,
            'dt_block': max_day,
            'signin': signin,
            'dt_alert': alert_day,
            'menus': []
        }
        FMT = lambda menu: WEEKDAYS.get(menu.weekday, '') + ' ' + menu.date.strftime('%d')
        for menu in menus:
            if (not len(result['menus'])) or (result['menus'][-1]['date'] != FMT(menu)):
                result['menus'].append({
                    'date': FMT(menu),
                    'day_of_week': menu.date.weekday()+1,
                    'meals': []
                })
            menu = menu.sudo()
            orders = menu.order_ids.filtered(lambda order: order.kid_id.id in kid_ids)
            menu_kids = orders.filtered(lambda order: order.state=='draft').mapped('kid_id.id')
            ordered_kids = orders.filtered(lambda order: order.state=='confirmed').mapped('kid_id.id')
            result['menus'][-1]['meals'].append({
                'id': menu.id,
                'meal_type': menu.meal_type,
                'state': 'active',
                'name': menu.name,
                'description': menu.description,
                'allergies': [{'id': a.id, 'name': a.name, 'code': a.code} for a in menu.allergy_ids],
                'kids': menu_kids,
                'kids_ordered': ordered_kids
            } )
        return result

    @http.route(['/school/classes_get'], type="json", auth="public", website=True, methods=["POST"])
    def school_classes_get(self, class_id=None, **kwargs):
        classes = request.env['school_lunch.class_name'].search([])
        if not class_id:
            class_id = classes[0].id
        kids = request.env['school_lunch.kid'].search([('class_id','=',int(class_id))])
        result = {
            'classes': [{'id': c.id, 'name': c.name} for c in classes],
            'kids': [{'id': k.id, 'shortname': k.shortname} for k in kids]
        }
        return result
