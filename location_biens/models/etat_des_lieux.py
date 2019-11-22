# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from datetime import datetime
from odoo.exceptions import UserError, AccessError
from odoo.tools import float_compare, pycompat
from odoo.addons import decimal_precision as dp


class Etat_des_lieux(models.Model):
    _name = 'lb.etat_des_lieux'
    _rec_name = 'location'

    etat_des_lieux_type = fields.Selection([('entree', 'Etat des lieux d\'entrée'),('sortie', 'Etat des lieux de sortie')], string="Type", required=True)
    date_etat_des_lieux = fields.Date(string="Date", required=True)
    ref_etat_des_lieux = fields.Char(string="Identifiant", help="Identifiant unique de l'état des lieux")
    notes = fields.Text(string="Notes")
    location = fields.Many2one('lb.location', ondelete='cascade', string="Location associée", required=True)
    enregistrement_etat_des_lieux = fields.One2many('lb.enregistrement_etat_des_lieux', 'etat_des_lieux_id', string="Etat des lieux")
    etat_des_lieux_entree_associe = fields.Many2one('lb.etat_des_lieux', string="Etat des lieux d'entrée associé", domain=[('etat_des_lieux_type', '=', 'entree')])
    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Documents")	

    _sql_constraints = [     
    ('reference_unique',
    'UNIQUE(ref_etat_des_lieux)',
    "La référence doit être unique"),
    ]
            # 2 fonctions pour l'image attaché

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for etat in self:
            etat.doc_count = Attachment.search_count([('res_model', '=', 'lb.etat_des_lieux'), ('res_id', '=', etat.id)])

    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        domain = [('res_model', '=', 'lb.etat_des_lieux'), ('res_id', 'in', self.ids)]
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


class Enregistrement_Etat_des_lieux(models.Model):
    _name = 'lb.enregistrement_etat_des_lieux'

    etat_des_lieux_id = fields.Many2one('lb.etat_des_lieux', ondelete='cascade', string="Etat des lieux")
    nom_piece = fields.Char(string="Nom de la pièce", required=True)
    Etat = fields.Selection([('non vérifié.', 'Non vérifié'),('neuf', 'Neuf'),('bon etat', 'Bon état'),('etat moyen','Etat moyen'),('mauvais etat', 'Mauvais état')], string="Etat")
    commentaires = fields.Text(string="Commentaire")

	
