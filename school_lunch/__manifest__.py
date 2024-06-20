{
    "name": "school_lunch",
    "summary": """
        School Lunch
    """,
    "description": """
        Module to order lunch at school.
    """,
    "author": "Fabien Pinckaers, Odoo PS",
    "website": "https://www.odoo.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Lunch",
    "version": "17.0.1.0.7",
    # any module necessary for this one to work correctly
    "depends": ["website_sale_loyalty"],
    "license": "OEEL-1",
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "data/school_lunch_email.xml",
        "data/school_lunch.allergy.csv",
        "data/school_lunch.xml",
        "views/views.xml",
        "views/loyalty_card_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
        "views/sale_order_views.xml",
        "views/templates.xml",
        "wizards/guest_reservation.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
        "demo/school_lunch.kid.csv",
    ],
    "cloc_exclude": ["**/*"],
    "assets": {
        "web.assets_backend": [
            "school_lunch/static/src/scss/school_lunch_backend.scss",
        ],
        "web.assets_frontend": [
            "school_lunch/static/src/js/*.js",
            "school_lunch/static/src/scss/school_lunch.scss",
        ],
        "web.assets_qweb": [],
    },
}
