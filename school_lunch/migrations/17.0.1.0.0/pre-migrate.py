from odoo.upgrade import custom_util, util


def migrate(cr, version):
    util.remove_module(cr, "school_event")
    custom_util.activate_views(cr, "school_lunch.res_config_settings_school_lunch_form")
