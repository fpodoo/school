# -*- coding: utf-8 -*-
# from odoo import http


# class SchoolLunch(http.Controller):
#     @http.route('/school_lunch/school_lunch', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/school_lunch/school_lunch/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('school_lunch.listing', {
#             'root': '/school_lunch/school_lunch',
#             'objects': http.request.env['school_lunch.school_lunch'].search([]),
#         })

#     @http.route('/school_lunch/school_lunch/objects/<model("school_lunch.school_lunch"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('school_lunch.object', {
#             'object': obj
#         })
