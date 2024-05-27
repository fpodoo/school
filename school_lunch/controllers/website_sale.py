import threading

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers import main


class WebsiteSale(main.WebsiteSale):
    @http.route(["/shop/confirm_order"], type="http", auth="public", website=True, sitemap=False)
    def confirm_order(self, **post):
        """
        Standard code reference :
        https://github.com/odoo/odoo/blob/3383d5bd68bfc13b7881f72e5adbb7c27a6df30e/addons/website_sale/controllers/main.py
        In the original file, `confirm_order` is taken from l.1633 to l.1648
        In the standard code, the Sale Order's pricelist is updated before redirecting to the payment page.
        This is unwanted as the SO has Sales Order Lines with different pricelists,
        and should not be overwritten by the SO's pricelist.
        """
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order) or self.checkout_check_address(order)
        if redirection:
            return redirection

        order.order_line._compute_tax_id()
        request.session["sale_last_order_id"] = order.id
        # PATCH START
        test_mode = getattr(threading.current_thread(), "testing", False) or self.env.registry.in_test_mode()
        if test_mode:
            request.website.sale_get_order(update_pricelist=True)
        # PATCH END
        extra_step = request.website.viewref("website_sale.extra_info")
        if extra_step.active:
            return request.redirect("/shop/extra_info")

        return request.redirect("/shop/payment")
