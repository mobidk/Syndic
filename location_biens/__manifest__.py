# -*- coding: utf-8 -*-
{
    'name': "SyndicUP",


    'author': "mtilimed",
    'website': "http://www.mtilimed.ma",
    'description': """
Module pour la gestion locative des biens immobiliers
    """,


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','portal','resource','analytic'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/biens_view.xml',

        'views/locations_view.xml',
        'views/etat_des_lieux_view.xml',

        'views/bailleur_view.xml',
        'views/villes_quartiers_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
