# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.tools import float_compare, pycompat
from odoo.exceptions import ValidationError
from odoo.osv import expression

from odoo.addons import decimal_precision as dp


class Bailleur(models.Model):
    _name = 'lb.bailleur'
    _rec_name = 'nom'

	        # Get default country
    @api.model
    def _get_default_country(self):
        country = self.env['res.country'].search([('code', '=', 'MA')], limit=1)
        return country

    nom = fields.Char(string="Nom", required=True)
    civilite = fields.Selection([('m.', 'M.'),('mme', 'Mme'),('mlle', 'Mlle'),('m. et mme','M. et Mme')], string="Civilité") 
    email = fields.Char(string="E-mail", required=True)
    telephone = fields.Char(string="Téléphone", required=True)
    rue = fields.Char()
    code_postale = fields.Char(string="Code Postal")
    ville = fields.Char(string="Ville")
    pays_id = fields.Many2one('res.country', string='Pays', default=_get_default_country, ondelete='restrict')
    poste_occupe = fields.Char(string="Poste occupé", help="Activité professionelle du propriétaire")
