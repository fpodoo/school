# -*- coding: utf-8 -*-
{
    'name': "school_lunch",
    'summary': """
        School Lunch
    """,

    'description': """
        Module to order lunch at school.
    """,
    'author': "Fabien Pinckaers",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.35',

    # any module necessary for this one to work correctly
    'depends': ['website_sale', 'website_sale_gift_card'],
    'license': 'LGPL-3',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/school_lunch_email.xml',
        'views/res_config_settings_views.xml',
        'data/school_lunch.allergy.csv',
        'data/school_lunch.xml',
        'views/templates.xml',
        'views/res_partner_views.xml',
        'views/gift_card_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
        'demo/school_lunch.kid.csv',
    ],
    'cloc_exclude': [
        'data/*', 'views/*'
    ],
    'assets': {
        'web.assets_backend': [
            'school_lunch/static/src/scss/school_lunch_backend.scss',

        ],
        'web.assets_frontend': [
            'school_lunch/static/src/js/*.js',
            'school_lunch/static/src/scss/school_lunch.scss',
        ],
        'web.assets_qweb': [
        ]
    }

}
