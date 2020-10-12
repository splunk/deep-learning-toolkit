const appName = window.location.pathname.match(/..-..\/app\/(?<app>[^\/]+)/).groups.app;

require([
    'jquery',
    'splunkjs/mvc/simplexml/ready!',
],
    function ($) {

        const get = function (el, name) {
            var values = $(el).attr("data-saas-" + name);
            if (!values) {
                values = "";
            }
            values = values.split(",");
            values = values.filter(function (v) {
                return v;
            });
            return values;
        };

        const has = function (el, name) {
            return get(el, name).length > 0;
        };

        const add = function (el, name, value) {
            var values = get(el, name);
            values = values.filter(function (v) {
                return v != value;
            });
            values.push(value);
            $(el).attr("data-saas-" + name, values.join(","))
        };

        const remove = function (el, name, value) {
            var values = get(el, name);
            values = values.filter(function (v) {
                return v != value;
            });
            $(el).attr("data-saas-" + name, values.join(","))
        };

        const addShow = function (el, value) {
            return add(el, "show", value);
        };

        const removeShow = function (el, value) {
            return remove(el, "show", value);
        };

        const hasShow = function (el) {
            return has(el, "show");
        };

        const addHide = function (el, value) {
            return add(el, "hide", value);
        };

        const removeHide = function (el, value) {
            return remove(el, "hide", value);
        }

        const hasHide = function (el) {
            return has(el, "hide");
        };

        const showOrHide = function (el) {
            if (hasHide(el)) {
                $(el).css("display", "none");
            }
            else if (hasShow(el)) {
                $(el).css("display", "");
            }
            else if (hasShow(el)) {
                $(el).css("display", "none");
            }
        };

        $("splunk-radio-input").change(function () {
            const input = $(this);
            const value = input.attr("value");
            const name = input.attr("name");

            $("." + name).each(function () {
                removeShow(this, name);
                addHide(this, name);
            });
            $("." + name + "." + value).each(function () {
                removeHide(this, name);
                addShow(this, name);
            });
            $("." + name).each(function () {
                showOrHide(this);
            });
        }).change();
    }
);