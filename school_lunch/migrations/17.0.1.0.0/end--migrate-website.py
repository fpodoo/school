from odoo.upgrade import util


def migrate(cr, _):

    view = util.env(cr).ref("website.header_text_element")

    util.replace_in_all_jsonb_values(
        cr,
        "ir_ui_view",
        "arch_db",
        "+1 (650) 555-0111",
        "+32 81 56 97 73",
        extra_filter=cr.mogrify("t.id = %s", [view.id]).decode(),
    )

    # homepage: id=740, cowed_id=748
    util.reset_cowed_views(cr, "website.homepage")
    website_page = util.env(cr)["website.page"].search([("view_id", "=", 740)])
    website_page.copy({"website_id": 1, "view_id": 748, "is_published": True})

    cr.execute(
        """
        UPDATE website_page
        SET is_published = true
        WHERE url='/home'
    """
    )
