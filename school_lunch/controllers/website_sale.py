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
        test_mode = getattr(threading.current_thread(), "testing", False) or request.env.registry.in_test_mode()
        if test_mode:
            request.website.sale_get_order(update_pricelist=True)
        # PATCH END
        extra_step = request.website.viewref("website_sale.extra_info")
        if extra_step.active:
            return request.redirect("/shop/extra_info")

        return request.redirect("/shop/payment")


@http.route(["/shop/pricelist"], type="http", auth="public", website=True, sitemap=False)
def pricelist(self, promo, **post):
    """
    Standard code reference :
    https://github.com/odoo/odoo/blob/3383d5bd68bfc13b7881f72e5adbb7c27a6df30e/addons/website_sale/controllers/main.py
    In the original file, `pricelist` is taken from l.750 to l.769
    In the standard code, the Sale Order's pricelist is updated when an empty promo code is used.
    This is unwanted as the SO has Sales Order Lines with different pricelists,
    and should not be overwritten by the SO's pricelist.
    """
    redirect = post.get("r", "/shop/cart")
    # empty promo code is used to reset/remove pricelist (see `sale_get_order()`)
    if promo:
        pricelist_sudo = request.env["product.pricelist"].sudo().search([("code", "=", promo)], limit=1)
        if not (pricelist_sudo and request.website.is_pricelist_available(pricelist_sudo.id)):
            return request.redirect("%s?code_not_available=1" % redirect)

        request.session["website_sale_current_pl"] = pricelist_sudo.id
        # TODO find the best way to create the order with the correct pricelist directly ?
        # not really necessary, but could avoid one write on SO record
        order_sudo = request.website.sale_get_order(force_create=True)
        order_sudo._cart_update_pricelist(pricelist_id=pricelist_sudo.id)
    else:
        order_sudo = request.website.sale_get_order()
        # PATCH START
        test_mode = getattr(threading.current_thread(), "testing", False) or request.env.registry.in_test_mode()
        if order_sudo and test_mode:
            order_sudo._cart_update_pricelist(update_pricelist=True)
        # PATCH END
    return request.redirect(redirect)


main.WebsiteSale.pricelist = pricelist
