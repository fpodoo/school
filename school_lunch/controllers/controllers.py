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

    @http.route(['/school/get_orders'], type="json", auth="public", website=True, methods=["POST"])
    def school_orders_get(self, date=None, **kwargs):
        print('_get_order called', date, kwargs)

        date = datetime.datetime.fromtimestamp(date or time.time())
        dt_from = date + relativedelta(day=1)
        dt_to = date + relativedelta(day=1, months=1) - datetime.timedelta(days=1)
        kids = request.env['school_lunch.kid'].browse(request.session.get('mykids', []))
        allergies = request.env['school_lunch.allergy'].search([])


        menus = request.env['school_lunch.menu'].search([('date','>=', dt_from.strftime('%Y-%m-%d')), ('date', "<=", dt_to.strftime('%Y-%m-%d'))])
        print('menu', menus)

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



        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(result)
        return result

