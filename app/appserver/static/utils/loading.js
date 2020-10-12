var appName = window.location.pathname.match(/..-..\/app\/(?<app>[^\/]+)/).groups.app;

define([
    'underscore',
    Splunk.util.make_url(`/static/app/${appName}/utils/modal.js`),
], function (_, Modal) {
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
            newLoadingIndicator(options) {
                options = _.extend({
                    title: "Loading...",
                    subtitle: "Please wait.",
                }, options);
                const modal = new Modal(this.makeid(30), {
                    title: options.title,
                    backdrop: 'static',
                    keyboard: false,
                    destroyOnHide: true,
                    type: 'normal',
                    center: true,
                });
                modal.body.append($('<p></p>').text(options.subtitle));
                $(".modal-body", modal.$el).css("padding-bottom", "10px");
                modal.show();
                return modal;
            },
        };
    }();
});