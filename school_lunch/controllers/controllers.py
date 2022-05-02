# -*- coding: utf-8 -*-

from odoo import http
import datetime
import time
from dateutil.relativedelta import relativedelta


class SchoolLunch(http.Controller):
    @http.route(['/menu', '/menu/<int:date>'], auth='public', type='http', website=True)
    def list(self, date=None, **kw):
        date = datetime.datetime.fromtimestamp(date or time.time())
        return http.request.render('school_lunch.menu', {
            'date': date,
            'dmonth': relativedelta(months=1)
        })

#     @http.route('/school_lunch/school_lunch/objects/<model("school_lunch.school_lunch"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('school_lunch.object', {
#             'object': obj
#         })
