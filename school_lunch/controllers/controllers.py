# -*- coding: utf-8 -*-

from odoo import http
import datetime
from odoo.http import request
import time
from dateutil.relativedelta import relativedelta


class SchoolLunch(http.Controller):
    @http.route(['/menu', '/menu/<int:date>'], auth='public', type='http', website=True)
    def list(self, date=None, **kw):
        date = datetime.datetime.fromtimestamp(date or time.time())

        dt_from = date + relativedelta(day=1)
        dt_to = date + relativedelta(day=1, months=1) - datetime.timedelta(days=1)

        menus = request.env['school_lunch.menu'].search([('date','>=', dt_from.strftime('%Y-%m-%d')), ('date', "<=", dt_to.strftime('%Y-%m-%d'))])
        return http.request.render('school_lunch.menu', {
            'date': date,
            'menus': menus,
            'dmonth': relativedelta(months=1)
        })

