# -*- coding: utf-8 -*-
# from odoo import http


# class Senide(http.Controller):
#     @http.route('/senide/senide', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/senide/senide/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('senide.listing', {
#             'root': '/senide/senide',
#             'objects': http.request.env['senide.senide'].search([]),
#         })

#     @http.route('/senide/senide/objects/<model("senide.senide"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('senide.object', {
#             'object': obj
#         })
