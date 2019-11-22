# -*- coding: utf-8 -*-
from odoo import http

# class RentalAppartments(http.Controller):
#     @http.route('/rental_appartments/rental_appartments/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rental_appartments/rental_appartments/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rental_appartments.listing', {
#             'root': '/rental_appartments/rental_appartments',
#             'objects': http.request.env['rental_appartments.rental_appartments'].search([]),
#         })

#     @http.route('/rental_appartments/rental_appartments/objects/<model("rental_appartments.rental_appartments"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rental_appartments.object', {
#             'object': obj
#         })