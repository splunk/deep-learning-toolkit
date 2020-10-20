define([
    'underscore',
    'jquery',
    './modalview',
    'splunkjs/mvc',
    './parametereditview',
    'views/datapreview/shared/Tab',
   './parametertabmodel',
    'css!./modalview.css'
    ], 
    function(_, $, Modal, mvc, ParameterEditView, Tab, TabModel) {
        return Modal.extend({
            className: Modal.CLASS_NAME,
            defaults : {
                model : {},
                learnMoreTag : "learnMore",
                title : 'Not Set'
            },
            initialize: function(options) {
                Modal.prototype.initialize.apply(this, arguments);
                this.model.activeTab = new TabModel();
                this.children.tabs = [],this.children.views = [],this.tab_collection = [];
                var that = this, i = 0;
                _.each(options.model.children,function(collection){
                    that.tab_collection.push(`tab${i}`);
                    that.children.tabs.push(new Tab({
                        tab: `tab${i++}`,
                        label: i==1 ? 'General' : _(`${collection.label}`).t(),
                        targetEntity: that.model.activeTab,
                        targetAttribute: "tab",
                        listenOnInitialize: true
                    }));
                    that.children.views.push(new ParameterEditView({
                        heading: _(collection.label).t(),
                        model: that.model,
                        collection: collection.collection,
                        enableAccordion: true
                    }));
                });
                this.activate();
            },
            events: {
                'click .revert': async function(e){
                    debugger;
                },
                'click .close,.cancel': async function(e){
                    var _self = this;
                    if (this.model && typeof(this.model.cancelhandler)=="function"){
                        if (false == await this.model.cancelhandler.call(null, e, mvc))
                        {
                            return;
                        }
                    }
                    _self.options.flashMessages.flashMsgCollection.reset();
                },
                'change .textvalue': function(e){
                    if (this.model && typeof(this.model.fieldchangehandler)=="function"){
                        if (false == this.model.fieldchangehandler.call(null, e, mvc))
                        {
                            return;
                        }
                    }
                },
                'keyup .textvalue': function(e){
                    if (this.model && typeof(this.model.fieldkeyuphandler)=="function"){
                        if (false == this.model.fieldkeyuphandler.call(null, e, mvc))
                        {
                            return;
                        }
                    }
                },
                'click .save': async function(e){
                    $('.error-container').hide();
                    this._disableToggleButton(e);
                    e.preventDefault();
                    var algoparams = [];
                    var deploymentparams = [];
                    var otherparams = [];
                    var _self = this, $e = e;
                    _self.options.flashMessages.flashMsgCollection.reset();
                    
                    _.each($('.pickervalue, .textvalue'),function(child){
                        if ($(child).hasClass('deployment')){
                            let environment = child.className.split(" ").filter(function(index) {
                                return index != 'textvalue' && index!='deployment'&& index!='splunk-view';
                            });
                            if (!deploymentparams[environment])
                                deploymentparams[environment] = [];
    
                            let state = mvc.Components.get(child.id).getState();
                            state.value && (deploymentparams[environment][child.id] = state.value);
                            state.choices && (deploymentparams[environment][child.id] = state.choices.length>0 ? state.value : null);
                        } else if ($(child).hasClass('algorithm')) {
                            var state = mvc.Components.get(child.id).getState();
                            (state.value || state.value=="") && (algoparams[child.id] = state.value);
                            state.choices && (algoparams[child.id] = state.choices.length>0 ? state.value : null);
                        } else {
                            var state = mvc.Components.get(child.id).getState();
                            (state.value || state.value=="") && (otherparams[child.id] = state.value);
                            state.choices && (otherparams[child.id] = state.choices.length>0 ? state.value : null);
                        }
                    });
                    
                    if (_self.options.flashMessages.flashMsgCollection.length > 0){
                        this._disableToggleButton($e);
                        return;
                    }
                    if (this.model && typeof(this.model.savehandler)=="function"){
                        try {
                            $('.info-container').show('fast');
                            _self.options.infoMessages.flashMsgCollection.add({
                                key: 'token-info',
                                type: 'info',
                                html: _.escape(_("Saving..... Please be patient.").t())
                            });
                            if (false == await this.model.savehandler.call(null, {algoparams:algoparams, deploymentparams:deploymentparams, otherparams:otherparams}, this)){
                                return;
                            }
                        } catch (e){
                            $('.info-container').hide('fast');
                            _self.options.infoMessages.flashMsgCollection.reset();
                            _self.options.flashMessages.flashMsgCollection.reset();
                            $('.error-container').show('fast');
                            _self.options.flashMessages.flashMsgCollection.add({
                                key: 'token-function-save',
                                type: 'error',
                                html: _.escape(_(JSON.stringify(e.data!=false ? e.data : e.message)).t())
                            });
                            this._disableToggleButton($e);
                            return;
                        }
                    }
                    _self.options.flashMessages.flashMsgCollection.reset();
                    this.model.savedhandler && this.model.savedhandler.call(null, _self, mvc);
                    this._disableToggleButton(e);
                }
            },
            startListening: function() {
                this.listenTo(this.model.activeTab, 'change:tab', function() {
                    this.manageStateOfChildren();
                });
            },
            setPanels: function() {
                this.children.views[0].activate().$el.show();
                if (this.children.length > 1) {
                    for (var i=1; i<this.children.length;i++){
                        this.children.views[i].activate().$el.hide();
                    }
                }
            },
            activate: function(options) {
                var clonedOptions = _.extend({}, (options || {}));
                delete clonedOptions.deep;
                this.ensureDeactivated({deep: true});
                this.manageStateOfChildren();
                return this;
            },
            deactivate: function(options) {
                if (!this.active) {
                    return BaseView.prototype.deactivate.apply(this, arguments);
                }
                BaseView.prototype.deactivate.apply(this, arguments);
                return this;
            },
            manageStateOfChildren: function() {
                var tab = this.model.activeTab.get('tab');
                for (let i=0; i<this.children.views.length; i++){
                    if (this.tab_collection[i]==tab) {
                       this.children.views[i].activate().$el.show();
                    } else {
                        this.children.views[i].activate().$el.hide();
                    }
                }
                return this;
            },
            render : function() {
                this.$el.html(Modal.TEMPLATE), 
                this.$(Modal.HEADER_TITLE_SELECTOR).html(this.options.title);
                this.$(Modal.HEADER_SELECTOR).append(_.template(this.headerTemplate)());
                this.$(Modal.BODY_SELECTOR).html(this.template);
                var that = this;
                _.each(this.children.tabs,function(tab){
                    tab.render().appendTo(that.$('.nav-tabs'));
                }); 
                _.each(this.children.views,function(view){
                    view.render().appendTo(that.$('.tab-content'));
                }); 
                this.setPanels.call(this);
                this.$(Modal.FOOTER_SELECTOR).append(Modal.BUTTON_CANCEL), 
                this.$(Modal.FOOTER_SELECTOR).append(this.options.primarybutton), 
                this.$(Modal.FOOTER_SELECTOR + " .modal-btn-primary").addClass("save"), 
                this.$(Modal.FOOTER_SELECTOR);
                this.$(".error-container").append(this.options.flashMessages.render().el),
                this.$(".info-container").append(this.options.infoMessages.render().el);
                this.startListening();
                this._addfields(this.model.basefields,'base');
                this.$('input').first().focus();
                return this.children.entityTitle && $form.append(this.children.entityTitle.render().el), this;
            },
            headerTemplate:'<div class="error-container"></div><div class="info-container"></div>',
            template: '<div class="base-form form-horizontal"></div>\
                <ul class="nav nav-tabs main-tabs"></ul>\
                <div class="tab-content tab-group" style="overflow:visible; padding-top:15px;"></div>\
            '
        });
    });

    