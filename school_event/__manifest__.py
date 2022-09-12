# -*- coding: utf-8 -*-
{
    'name': "school_event",
    'summary': """
        School Event
    """,

    'description': """
        Adaptation of event module to avoid asking email on pariticpants
    """,
    'author': "Fabien Pinckaers",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.31',
    'depends': ['website_event_questions'],
    'license': 'LGPL-3',
    'data': [
        'views/views.xml',
    ],
}
