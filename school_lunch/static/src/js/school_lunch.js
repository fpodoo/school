/** @odoo-module **/

var ajax = require('web.ajax');
var core = require('web.core');

var _t = core._t;

const {Component, Store, mount, QWeb, xml} = owl;
const {useDispatch, useStore, useGetters, useRef, useState} = owl.hooks;
const {Router, RouteComponent} = owl.router;
const {whenReady} = owl.utils;

class LunchMenu extends Component {
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
        this.menus = [
            {date: '2012-01-01'}



        ]
    }

    increment() {
        this.state.value++;
    }
}
LunchMenu.template = "school_lunch.lunch_table"

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
    mount(LunchMenu, {target: document.getElementById('LunchMenu'), env});
}

whenReady(setup);
