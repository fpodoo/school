from odoo.upgrade import util


def migrate(cr, _):

    mail_template_xml_ids = [
        "sale.mail_template_sale_confirmation",
    ]

    for mail_template in mail_template_xml_ids:
        util.update_record_from_xml(cr, mail_template, reset_translations=True)
