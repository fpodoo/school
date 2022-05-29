odoo.define('lunch_order.lunch_order', function (require) {
"use strict";


var ajax = require('web.ajax');
var core = require('web.core');
var Widget = require('web.Widget');
var publicWidget = require('web.public.widget');

var _t = core._t;

publicWidget.registry.lunchOrder = publicWidget.Widget.extend({
    selector: '#lunch_menu',
    start: function () {
        var self=this;
        console.log('FP: Start Called');
        $('.o_choice').click(function (ev) {
            for (var el of ev.target.closest('.o_lunch_choice').children) {
                if (el != ev.target) 
                    el.classList.remove('active');
                else
                    el.classList.toggle('active');
            };
        });
    },
});


return publicWidget.registry.lunchOrder;
});
