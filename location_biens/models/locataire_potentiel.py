# -*- coding: utf-8 -*-

from lxml import etree

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo.tools.safe_eval import safe_eval
from odoo.addons import decimal_precision as dp


class LocatairePotentiel(models.Model):
    _name = 'lb.locataire_potentiel'
    _rec_name = 'nom'

    nom = fields.Char(string="Nom", required=True)
    company_type = fields.Selection([('particulier', 'Particulier'),('societe', 'Société')], string="Type") 
    quartier_souhaitee = fields.Many2one('lb.quartier', string="Quartier souhaité")
    budget = fields.Float(string="Budget", default=0.0, digits=dp.get_precision('Budget'))
    email = fields.Char(string="E-mail")
    telephone = fields.Char(string="Téléphone", required=True)
    civilite = fields.Selection([('m.', 'M.'),('mme', 'Mme'),('mlle', 'Mlle'),('m. et mme','M. et Mme')], string="Civilité") 
    notes = fields.Text(string="Notes")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('lb.locataire_potentiel'), index=1)
    currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_currency_id')

            # Calcul de la devise

    @api.multi
    def _compute_currency_id(self):
        try:
            main_company = self.sudo().env.ref('base.main_company')
        except ValueError:
            main_company = self.env['res.company'].sudo().search([], limit=1, order="id")
        for template in self:
            template.currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id
