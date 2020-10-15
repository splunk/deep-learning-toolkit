define(
    [
       'jquery',
       'underscore',
       'views/shared/PopTart',
     ],
    function (
        $,
        _,
        PopTartView) {
        var defaults = {
            button: true,
            showOpenActions: true,
            deleteRedirect: false
        };
        return PopTartView.extend({
            className: 'dropdown-menu other-menu',
            initialize: function (rowData) {
                PopTartView.prototype.initialize.apply(this, arguments);
                _.defaults(this.options, defaults);
                this._actionModel = !this.collection ? {} : this.collection,this._actionModel.enabledisable = this._actionModel.status == 'deployed' ? "disable" : "enable";
                this._menuModel = {
                    allowDeleteAlgo: !this.collection ? false : typeof(this.collection.type)==='string' && this.collection.type =='algorithms',
                    allowDeleteDeployment: !this.collection ? false : typeof(this.collection.type)==='string' && this.collection.type =='deployments',
                    allowEditDeployment: !this.collection ? false : typeof(this.collection.type)==='string' && this.collection.type =='deployments',
                    allowToggleStatusDeployment:  !this.collection ? false : typeof(this.collection.type)==='string' && this.collection.type =='deployments',
                    allowRestartDeployment: !this.collection ? false : typeof(this.collection.type)==='string' && this.collection.type =='deployments',
                    allowAddDeployment: !this.collection ? false : typeof(this.collection.type)==='string' && this.collection.type =='algorithms',
                    allowAddMethod: !this.collection ? false : typeof(this.collection.type)==='string' && this.collection.type =='algorithms',
                    allowEditAlgorithm: !this.collection ? false : typeof(this.collection.type)==='string' && this.collection.type =='algorithms',
                    allowDeleteMethod: !this.collection ? false : typeof(this.collection.type)==='string' && this.collection.type =='methods',
                    allowDeleteEnvironment:!this.collection ? false : typeof(this.collection.type)==='string' && this.collection.type =='environments',
                    allowEditEnvironment:!this.collection ? false : typeof(this.collection.type)==='string' && this.collection.type =='environments',
                    textEnableDisable: this._actionModel.status == 'deployed' ? "Disable" : "Enable"
                };
            },
            events: {
                'click a.delete-algorithm': function (e) {
                    e.preventDefault();
                    this._triggerControllerEvent('action:delete-algorithm',this,this._actionModel);
                },
                'click a.toggle-status': function (e) {
                    e.preventDefault();
                    this._triggerControllerEvent('action:toggle-status',this,this._actionModel);
                },
                'click a.delete-deployment': function (e) {
                    e.preventDefault();
                    this._triggerControllerEvent('action:delete-deployment',this,this._actionModel);
                },
                'click a.restart-deployment': function (e) {
                    e.preventDefault();
                    this._triggerControllerEvent('action:restart-deployment',this,this._actionModel);
                },
                'click a.add-deployment': function (e) {
                    e.preventDefault();
                    this._triggerControllerEvent('action:add-deployment',this,this._actionModel);
                },
                'click a.add-method': function (e) {
                    e.preventDefault();
                    this._triggerControllerEvent('action:add-method',this,this._actionModel);
                },
                'click a.delete-environment': function (e) {
                    e.preventDefault();
                    this._triggerControllerEvent('action:delete-environment',this,this._actionModel);
                },
                'click a.delete-method': function (e) {
                    e.preventDefault();
                    this._triggerControllerEvent('action:delete-method',this,this._actionModel);
                },
                'click a.edit-deployment': function (e) {
                    e.preventDefault();
                    this._triggerControllerEvent('action:edit-deployment',this,this._actionModel);
                },
                'click a.edit-algorithm': function (e) {
                    e.preventDefault();
                    this._triggerControllerEvent('action:edit-algorithm',this,this._actionModel);
                },
                'click a.edit-environment': function (e) {
                    e.preventDefault();
                    this._triggerControllerEvent('action:edit-environment',this,this._actionModel);
                }
            },
            _triggerControllerEvent: function () {
                this.hide();
                this.model.controller.trigger.apply(this.model.controller, arguments);
            },
            render: function () {
                this.$el.html(PopTartView.prototype.template_menu);
                this.$el.append(this.compiledTemplate(this._menuModel));
                return this;
            },
            isEmpty: function () {
                return !_.some(_.values(this._menuModel));
            },
            template: '\
                    <ul class="first-group">\
                        <% if (allowToggleStatusDeployment) { %>\
                            <li><a href="#" class="toggle-status"><%- textEnableDisable %></a></li>\
                        <% } %>\
                        <% if (allowAddDeployment) { %>\
                            <li><a href="#" class="add-deployment"><%- _("Add Deployment").t() %></a></li>\
                        <% } %>\
                        <% if (allowAddMethod) { %>\
                            <li><a href="#" class="add-method"><%- _("Add Method").t() %></a></li>\
                        <% } %>\
                        <% if (allowEditDeployment) { %>\
                            <li><a href="#" class="edit-deployment"><%- _("Edit Settings").t() %></a></li>\
                        <% } %>\
                        <% if (allowEditAlgorithm) { %>\
                            <li><a href="#" class="edit-algorithm"><%- _("Edit Settings").t() %></a></li>\
                        <% } %>\
                        <% if (allowEditEnvironment) { %>\
                            <li><a href="#" class="edit-environment"><%- _("Edit Settings").t() %></a></li>\
                        <% } %>\
                        <% if (allowRestartDeployment) { %>\
                            <li><a href="#" class="restart-deployment"><%- _("Restart").t() %></a></li>\
                        <% } %>\
                    </ul>\
                    <ul class="second-group">\
                    <% if (allowDeleteAlgo) { %>\
                        <li><a href="#" class="delete-algorithm"><%- _("Delete").t() %></a></li>\
                        <% } %>\
                        <% if (allowDeleteMethod) { %>\
                        <li><a href="#" class="delete-method"><%- _("Delete").t() %></a></li>\
                        <% } %>\
                        <% if (allowDeleteEnvironment) { %>\
                            <li><a href="#" class="delete-environment"><%- _("Delete").t() %></a></li>\
                        <% } %>\
                        <% if (allowDeleteDeployment) { %>\
                        <li><a href="#" class="delete-deployment"><%- _("Delete Deployment").t() %></a></li>\
                        <% } %>\
                    </ul>\
            '
        });
    }
);
