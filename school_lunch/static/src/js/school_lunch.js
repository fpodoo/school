/** @odoo-module **/


var ajax = require('web.ajax');
var core = require('web.core');

var _t = core._t;

const {Component, Store, mount, QWeb, xml} = owl;
const {useDispatch, useStore, useGetters, useRef, useState} = owl.hooks;
const {Router, RouteComponent} = owl.router;
const {whenReady} = owl.utils;

class LunchMenu extends Component {
    toggleMenu() {
        const kid = this.props.kid.id;
        const isset = this.props.menu.kids.includes(kid);
        for (var meal of this.props.meals) {
            var index = meal.kids.indexOf(kid);
            if (index > -1)
                delete meal.kids[index];
        };
        if (! isset)
            this.props.menu.kids.push(kid);
    };
    static props = ["menu", "kid", "meals"];
}
LunchMenu.template = "school_lunch.lunch_menu"


class LunchLine extends Component {
    static props = ["menu", "kids"];
    static components = { LunchMenu };
}
LunchLine.template = "school_lunch.lunch_line"


class LunchMenuTable extends Component {
    setup() {
        this.state = useState({ value: 1 });
        this.kids = [
            {id: 1, shortname: "Charlie"},
            {id: 2, shortname: "Lena"}
        ]
        this.allergies = [
            {id: 1, name: "Lentils"},
            {id: 2, name: "Apple"}
        ]
        this.menus = useState([
            {
                date: 'Wed, 04 May 2022',
                meals: [
                    {id: 1, meal_type: "meal", state: "active", name: "Spaggethi", allergies: [{id: 2, name: "Apple"}], kids: [2]},
                    {id: 2, meal_type: "soup", state: "active", name: "Soup 1", allergies: [], kids: [1]}
                ],
            }
        ])
    }
    static components = { LunchLine }
}
LunchMenuTable.template = "school_lunch.lunch_table"




async function makeEnvironment() {
    const env = {};
    const services = Component.env.services;
    const qweb = new QWeb({translateFn: _t});
    const templates = await owl.utils.loadFile('/school_lunch/static/src/xml/lunch_menu.xml');
    qweb.addTemplates(templates);
    return Object.assign(env, {qweb, services});
}

async function setup() {
    const env = await makeEnvironment();
    mount(LunchMenuTable, {target: document.getElementById('LunchMenu'), env});
}

whenReady(setup);
