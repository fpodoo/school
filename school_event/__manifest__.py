{
    "name": "school_event",
    "summary": """
        School Event
    """,
    "description": """
        Adaptation of event module to avoid asking email on pariticpants
    """,
    "author": "Fabien Pinckaers, Odoo PS",
    "website": "https://www.odoo.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "17.0.1.0.0",
    "depends": ["website_event_questions"],
    "license": "OEEL-1",
    "data": [
        "views/views.xml",
    ],
}
