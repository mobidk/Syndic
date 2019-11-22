# -*- coding: utf-8 -*-

from lxml import etree

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo.tools.safe_eval import safe_eval
from odoo.addons import decimal_precision as dp

class Bien(models.Model):
    _name = 'lb.bien'
    _rec_name = 'type_id'


	        # Get default country
    @api.model
    def _get_default_country(self):
        country = self.env['res.country'].search([('code', '=', 'MA')], limit=1)
        return country

    bailleur_id = fields.Many2one('lb.bailleur', ondelete='cascade', string="propriétaire", store=True)
    type_id = fields.Many2one('lb.type', ondelete='cascade', string="Type")
    reference = fields.Char(string="Référence du Bien")
    prix_location = fields.Float(string="Prix de la location (hors charges)", default=0.0, digits=dp.get_precision('Prix de la location'))
    rue = fields.Char()
    description = fields.Text(string="Description")
    superficie = fields.Integer(string="Superficie")
    code_postale = fields.Char(string="Code Postal")
    ville = fields.Many2one('lb.ville')
    quartier = fields.Many2one('lb.quartier')
    pays = fields.Many2one('res.country', string="Pays", default=_get_default_country)
    notes = fields.Text(string="Notes")
    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Documents")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('lb.location'), index=1)
    currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_currency_id')

    _sql_constraints = [     
    ('reference_unique',
    'UNIQUE(reference)',
    "La référence du bien doit être unique"),
    ]


            # 2 fonctions pour l'image attaché

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for bien in self:
            bien.doc_count = Attachment.search_count([('res_model', '=', 'lb.bien'), ('res_id', '=', bien.id)])

    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        domain = [('res_model', '=', 'lb.bien'), ('res_id', 'in', self.ids)]
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Cliquez sur créer (et non importer) pour ajouter les images associées à vos biens.</p><p>
                    </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

            # Calcul de la devise

    @api.multi
    def _compute_currency_id(self):
        try:
            main_company = self.sudo().env.ref('base.main_company')
        except ValueError:
            main_company = self.env['res.company'].sudo().search([], limit=1, order="id")
        for template in self:
            template.currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id

class Type(models.Model):
    _name = 'lb.type'
    _rec_name = 'type'

    type = fields.Char(string="Type")
