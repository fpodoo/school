# -*- coding: utf-8 -*-
{
    'name': "school_lunch",
    'summary': """
        School Lunch
    """,

    'description': """
        Module to order lunch at school.
    """,
    'author': "Lena Pinckaers",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website_sale'],
    'license': 'LGPL-3',

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/school_lunch.allergy.csv',
        'data/school_lunch.class_name.csv',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
