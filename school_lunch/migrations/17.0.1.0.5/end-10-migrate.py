from odoo.upgrade import util


def migrate(cr, _):
    env = util.env(cr)
    records_to_compute = env["school_lunch.order"].search([("date_end_gantt", "=", False)])
    util.recompute_fields(cr, "school_lunch.order", ["date_end_gantt"], ids=records_to_compute.ids)
