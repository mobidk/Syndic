# -*- coding: utf-8 -*-

import re
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, tools, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, pycompat
from odoo.addons import decimal_precision as dp


class Location(models.Model):
    _name = 'lb.location'
    _rec_name = 'bien_loue'

    bien_loue = fields.Many2one('lb.bien', ondelete='cascade', string="Bien Loué", required=True)
    locataires = fields.Many2one('lb.bailleur', ondelete='cascade', string="Locataire", required=True)
    statut_location = fields.Selection([('inactif', 'Inactif'),('actif', 'Actif')], string="Statut", compute='update_statut', help="Statut de la location (Actif : Location en cours)")
    utilisation = fields.Selection([('utilisation1', 'Utilisation principale du locataire'),('utilisation2', 'Utilisation secondaire du locataire'),('utilisation3', 'Utilisation professionnelle')], string="Utilisation")
    date_quittancement = fields.Selection([('1', '1'),('2', '2'),('3', '3'),('4', '4'),('5', '5'),('6', '6'),('7', '7'),('8', '8'),('9', '9'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20'),('21', '21'),('22', '22'),('23', '23'),('24', '24'),('25', '25'),('26', '26'),('27', '27'),('28', '28'),('29', '29'),('30', '30'),('31', '31')], string="Date de quittancement", help="La date selon laquelle vos quittances seraient datées")
    ref_location = fields.Char(string="Identifiant", help="Identifiant de la location")
    debut_bail = fields.Date(string="Début du Bail", required=True)
    fin_bail = fields.Date(string="Fin du Bail", required=True)
    paiement = fields.Selection([('mensuel', 'Mensuel'),('bimestriel', 'Bimestriel'),('trimestriel', 'Trimestriel'),('semestriel', 'Semestriel'),('annuel', 'Annuel'),('forfaitaire', 'Forfaitaire')], string="Paiements", required=True)
    loyer_sans_charges = fields.Float(string="Loyer hors charges", related='bien_loue.prix_location', default=0.0, digits=dp.get_precision('Loyer hors charges'), required=True)
    charges_loyer = fields.Float(string="Charges", default=0.0, digits=dp.get_precision('Charges'))
    loyer_avec_charges = fields.Float(string="Loyer charges comprises", default=0.0, digits=dp.get_precision('Loyer charges comprises'), readonly=True, compute='_loyer_charges')
    frais_retard = fields.Float(string='Frais de retard (%)', default=0.0, digits=dp.get_precision('Frais de retard (%)'))
    autre_paiement = fields.Float(string='Autre Paiements', digits=dp.get_precision('Autre Paiements'))
    description_autre_paiement = fields.Text(string="Autre Paiements : Description")
    enregistrement_paiement = fields.One2many('lb.paiement', 'paiement_id', string="Paiements")
    condition_particuliere = fields.Text(string="Conditions")
    reste_a_payer = fields.Float(string="Reste à payer", default=0.0, digits=dp.get_precision('Reste à Payer'))
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('lb.location'), index=1)
    currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_currency_id')
    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Documents")
    locataire_a_jour = fields.Selection([('oui', 'Oui'),('non', 'Non')], string="Le locataire est-il à jour ?")

    _sql_constraints = [     
    ('reference_location_unique',
    'UNIQUE(ref_location)',
    "La référence doit être unique"),
    ]

    _sql_constraints = [     
    ('locatin_bien_unique',
    'UNIQUE(bien_loue)',
    "Ce bien est déjà sous location"),
    ]

	
            # Calcul du loyer
    @api.multi
    def _loyer_charges(self):
        for r in self:
            r.loyer_avec_charges = r.loyer_sans_charges + r.charges_loyer

            # Statut Location
    @api.model
    def update_statut(self):
        for r in self:
            if r.debut_bail and r.fin_bail:
                if r.debut_bail <= fields.Date.today() and r.fin_bail >= fields.Date.today():
                    r.statut_location = 'actif'
                else:
                    r.statut_location = 'inactif'

            # Calcul de la devise
    @api.multi
    def _compute_currency_id(self):
        try:
            main_company = self.sudo().env.ref('base.main_company')
        except ValueError:
            main_company = self.env['res.company'].sudo().search([], limit=1, order="id")
        for template in self:
            template.currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id
			
            # Contrat attaché

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for bien in self:
            bien.doc_count = Attachment.search_count([('res_model', '=', 'lb.location'), ('res_id', '=', bien.id)])

    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        domain = [('res_model', '=', 'lb.location'), ('res_id', 'in', self.ids)]
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Cliquez sur Créer (et non importer) pour ajouter vos contrats de location</p><p>
                    </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

    @api.constrains('debut_bail', 'fin_bail')
    def _check_debut_fin_bail(self):
        for r in self:
            if r.debut_bail > r.fin_bail:
                raise exceptions.ValidationError("La fin du bail doit être supérieur au début du bail")


class Paiement(models.Model):
    _name = 'lb.paiement'
    _rec_name = 'paiement_id'

    paiement_id = fields.Many2one('lb.location', ondelete='cascade', string="Location")
    locataire_id = fields.Many2one(related='paiement_id.locataires', string="Locataire", store=True)
    statut_location_id = fields.Selection(related='paiement_id.statut_location', string="Statut de la Location")
    fin_bail_id = fields.Date(related='paiement_id.fin_bail', string="Fin du Bail")
    date_paiement = fields.Date(string="Date de Paiement", required=True)
    periode_paye_debut = fields.Date(string="Période Payée : Début", required=True)
    periode_paye_fin = fields.Date(string="Période Payée : Fin", required=True)
    montant_paye = fields.Float(string="Montant Payé", default=0.0, digits=dp.get_precision('Montant Payé'), required=True)
    commentaire_paiement = fields.Text(string="Commentaire")
    objet_paiement = fields.Selection([('avance', 'Avance'),('loyer', 'Loyer du mois'),('pénalité', 'Pénalités'),('autre paiements', 'Autres Paiements')], string="Objet du Paiement")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('lb.location'), index=1)
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

