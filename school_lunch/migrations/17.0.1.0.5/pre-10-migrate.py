from odoo.upgrade import util


def migrate(cr, _):
    util.ensure_xmlid_match_record(cr, "school_lunch.class_name_guest", "school_lunch.class_name", {"name": "Invité"})
