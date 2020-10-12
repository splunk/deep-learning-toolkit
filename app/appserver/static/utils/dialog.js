var appName = window.location.pathname.match(/..-..\/app\/(?<app>[^\/]+)/).groups.app;

define([
    'underscore',
    Splunk.util.make_url(`/static/app/${appName}/utils/modal.js`),
    Splunk.util.make_url(`/static/app/${appName}/utils/parsing.js`),
], function (_, Modal, parsing) {
    return function () {
        return {
            makeid: function (length) {
                var result = '';
                var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
                var charactersLength = characters.length;
                for (var i = 0; i < length; i++) {
                    result += characters.charAt(Math.floor(Math.random() * charactersLength));
                }
                return result;
            },
            showErrorDialog(title, err, button) {
                if (title == null || title == undefined || title == "") {
                    title = "Error Occurred";
                }
                const errorText = parsing.parseError(err);
                const modal = new Modal(this.makeid(30), {
                    title: title,
                    backdrop: 'static',
                    keyboard: false,
                    destroyOnHide: true,
                    type: 'normal',
                    button: button,
                });
                const encode = function (str) {
                    var buf = [];
                    for (var i = str.length - 1; i >= 0; i--) {
                        buf.unshift(['&#', str[i].charCodeAt(), ';'].join(''));
                    }
                    return buf.join('');
                }
                modal.body.append($('<p>' + encode(errorText) + '</p>'));
                modal.show();
                return modal;
            },
            show($el, options) {
                if (!options) options = {}
                const body = $(".body", $el);
                const bodyContainer = body.parent();
                const footer = $(".footer", $el);
                const footerContainer = footer.parent();
                const modal = new Modal(this.makeid(30), {
                    title: $el.attr("title"),
                    backdrop: 'static',
                    keyboard: false,
                    destroyOnHide: true,
                    type: 'normal',
                    closeCallback: function () {
                        bodyContainer.append(body);
                        footerContainer.append(footer);
                        if (options.close) {
                            options.close();
                        }
                    },
                });
                modal.body.append(body);
                modal.footer.append(footer);
                modal.show();
            },
        };
    }();
});