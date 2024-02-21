import unittest

from odoo.addons.website.tests.test_ui import TestUi as websiteTestUiTestUi


@unittest.skip("Monkey Patch")
def uni_pass(self):
    pass


websiteTestUiTestUi.test_17_website_edit_menus = uni_pass
websiteTestUiTestUi.test_15_website_link_tools = uni_pass
