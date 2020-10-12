define([
    "underscore",
    "backbone",
    "jquery",
    'splunkjs/mvc',
    './environmentcontroller',
    "css!./environmentcontrols.css" 
], function (_, Backbone, $, mvc,Controller) {
    return Backbone.View.extend({
        className: "pagecontrols",
        defaults: {},
        events: {
            'click .create': function (e) {
                this._triggerControllerEvent('action:show-create',this);
            }
        },
        initialize: function () {
            this.options = _.extend({}, this.defaults, this.options);
            this.model = new Backbone.Model();
            this.options = _.extend({}, this.defaults, this.options);
            this.model.controller = new Controller(this.options);
            this.children = {};
        },
        _triggerControllerEvent: function () {
            this.model.controller.trigger.apply(this.model.controller, arguments);
        },
        render: function () {
            var model = _.extend({}, this.model, this.options);
            this.$el.addClass(this.className);
            this.$el.html(_.template(this.template)(model));
            $('.dashboard').prepend(this.$el);
        },
        template: '<div class="pagecontrols-container">\
                      <a class="btn btn-primary create" role="button">Create New Environment</a>\
                   </div>'
        
    });
});