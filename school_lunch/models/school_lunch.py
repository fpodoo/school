import uuid

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.tools import format_date


class Allergy(models.Model):
    _name = "school_lunch.allergy"
    _description = "Allergies"
    _order = "code"

    name = fields.Char(required=True)
    code = fields.Integer()


class Menu(models.Model):
    _name = "school_lunch.menu"
    _description = "Daily Menu"
    _order = "date desc, meal_type"

    name = fields.Char("Meal Title", required=True)
    description = fields.Char()
    cook_id = fields.Many2one("res.partner", "Cuisinier")
    weekday = fields.Selection(
        [
            ("0", "Monday"),
            ("1", "Tuesday"),
            ("2", "Wednesday"),
            ("3", "Thursday"),
            ("4", "Friday"),
            ("5", "Saturday"),
            ("6", "Sunday"),
        ],
        compute="_compute_weekday",
    )
    weekyear = fields.Integer("Week of Year", compute="_compute_weekday")
    order_ids = fields.One2many("school_lunch.order", "menu_id", string="Orders")
    date = fields.Date("Day", index=True, required=True, default=lambda self: self._default_date())
    color = fields.Integer()
    meal_type = fields.Selection(
        [("soup", "Soup"), ("meal", "Meal"), ("off", "Day Off")], "Meal Type", default=lambda self: self._default_meal()
    )
    allergy_ids = fields.Many2many("school_lunch.allergy", string="Allergies")
    order_count = fields.Integer("# of Orders", compute="_compute_order_count")
    kid_meal_type = fields.Selection(
        [("0", "Soup"), ("1", "Meal"), ("off", "Day Off")], "Kid Meal", compute="_compute_kid_meal_type", default=False
    )

    def _default_date(self):
        latest = self.search([], limit=1)
        if latest.meal_type == "meal":
            skip = {1: 2, 4: 3}.get(latest.date.weekday(), 1)
            rt = relativedelta(days=skip)
            return latest.date + rt
        else:
            return latest.date

    def _default_meal(self):
        latest = self.search([], limit=1)
        if latest.meal_type == "meal":
            return "soup"
        else:
            return "meal"

    @api.depends("order_ids.menu_id")
    def _compute_order_count(self):
        for record in self:
            record.order_count = len(record.order_ids)

    @api.depends("name", "date")
    def _compute_display_name(self):
        for menu in self:
            name = menu.name if menu.name else _("New Menu")
            if self.env.context.get("display") == "simple":
                menu.display_name = name
            elif self.env.context.get("display") == "description":
                menu.display_name = f"{name} - {menu.description}" if menu.description else name
            else:
                menu.display_name = f"{format_date(self.env, menu.date, date_format='EEEE, dd MMM yyyy')}: {name}"

    @api.depends("date")
    def _compute_weekday(self):
        for record in self:
            if not record.date:
                record.weekday = False
                record.weekyear = False
                return True
            record.weekday = str(record.date.weekday())
            record.weekyear = record.date.isocalendar()[1]

    @api.depends_context("kid")
    def _compute_kid_meal_type(self):
        if not self.context.get("kid"):
            self.kid_meal_id = False
        self.env["school_lunch.order"].read_group(
            [("kid_id", "=", int(self.context["kid"])), ("id", "in", self.ids)], ["menu_id"], ["menu_id"]
        )
        for menu in self:
            menu.kid_meal_type = "1"


class Order(models.Model):
    _name = "school_lunch.order"
    _description = "Orders"
    _order = "date desc, name"

    name = fields.Char("Kid Name", related="kid_id.name", store=True)
    kid_id = fields.Many2one("school_lunch.kid", "Kid", required=True)
    class_id = fields.Many2one("school_lunch.class_name", string="Class", related="kid_id.class_id", store=True)
    menu_id = fields.Many2one("school_lunch.menu", "Menu", required=True)
    date = fields.Date("Day", related="menu_id.date", index=True, store=True)
    date_end_gantt = fields.Datetime("Day End Gantt", compute="_compute_date_end_gantt", search=False, store=True)
    meal_type = fields.Selection(related="menu_id.meal_type", string="Meal Type", store=True)
    color = fields.Integer("Color", compute="_compute_color")
    sale_line_id = fields.Many2one("sale.order.line", "Sale Order Line", ondelete="cascade")
    state = fields.Selection([("draft", "Draft"), ("confirmed", "Confirmed")], "State", default="draft")
    class_type = fields.Selection(related="class_id.class_type", string="Class Type", store=True)

    def _compute_date_end_gantt(self):
        for order in self:
            order.date_end_gantt = order.date + relativedelta(hours=1)

    @api.depends("meal_type")
    def _compute_color(self):
        for order in self:
            order.color = {
                "meal": 2,
                "soup": 3,
                "off": 4,
            }.get(order.meal_type, 1)

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        guest_id = self.env.ref("school_lunch.kid_guest").id
        for order in orders:
            if order.kid_id.id == guest_id:
                order.state = "confirmed"
        orders._compute_date_end_gantt()
        return orders


class ClassName(models.Model):
    _name = "school_lunch.class_name"
    _description = "Class"
    _order = "name"

    name = fields.Char("Class Name", required=True)
    class_type = fields.Selection(
        [("0", "Maternelle"), ("1", "Primaire"), ("2", "Secondaire"), ("3", "Other")], string="Class Type"
    )
    active = fields.Boolean("Active", default=True)
    pricelist_id = fields.Many2one("product.pricelist", string="Pricelist")


class Kid(models.Model):
    _name = "school_lunch.kid"
    _description = "Kid"
    _order = "name"

    firstname = fields.Char("Firstname", required=True)
    lastname = fields.Char("Lastname", required=True)
    name = fields.Char("Name", compute="_compute_fullname", store=True)
    shortname = fields.Char("Short Name", compute="_compute_shortname")
    parent_ids = fields.Many2many("res.partner", "school_lunch_kid_partner_rel", "kid_id", "partner_id", "Parents")
    allergy_ids = fields.Many2many("school_lunch.allergy", string="Allergies")
    class_id = fields.Many2one("school_lunch.class_name", "Class", required=True)
    unblock_date = fields.Date("Allow Order Until")
    uuid = fields.Char("UUID", default=lambda x: str(uuid.uuid4()), copy=False)
    pricelist_id = fields.Many2one("product.pricelist", string="Pricelist")
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        ("uuid_uniq", "unique(uuid)", "UUID field must be unique per kid!"),
    ]

    @api.depends("firstname", "lastname", "class_id")
    def _compute_shortname(self):
        for kid in self:
            letter_count = 0
            firstname = kid.firstname if kid.firstname else _("New")
            lastname = kid.lastname if kid.lastname else _("Kid")
            class_name = kid.class_id.name if kid.class_id.name else _("New Class")
            while (
                len(
                    self.search(
                        [
                            ("firstname", "=", firstname),
                            ("class_id", "=", class_name),
                            ("lastname", "=like", lastname[:letter_count] + "%"),
                        ]
                    )
                )
                > 1
            ):
                if letter_count >= len(kid.lastname):
                    break
                letter_count += 1
            kid.shortname = (
                f"{firstname} {lastname[:letter_count]}. ({class_name})"
                if letter_count
                else f"{firstname} ({class_name})"
            )

    @api.depends("firstname", "lastname", "class_id")
    def _compute_fullname(self):
        for kid in self:
            firstname = kid.firstname if kid.firstname else _("New")
            lastname = kid.lastname if kid.lastname else _("Kid")
            kid.name = f"{firstname} {lastname}"
