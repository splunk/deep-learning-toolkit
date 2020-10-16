define([
    'underscore',
    'jquery',
    'views/shared/Modal',
    'models/Base',
    'splunkjs/mvc',
    './dropdownview',
    'splunkjs/mvc/searchmanager',
    './textinputview',
    'views/shared/controls/ControlGroup',
    'views/shared/FlashMessages',
    'css!./modalview.css'
    ], 
    function(_, $, Modal, BaseModel, mvc, DropdownView, SearchManager, TextInputView, ControlGroup, FlashMessagesView) {
        var FieldModel = BaseModel.extend({
            element : {},
            init : function(options){
                this.options = options;
                this.element = mvc.Components.get(options.id);
            },
            get_value : function(){
                this.element = mvc.Components.get(this.options.id);
                let state = this.element.getState();
                let val = null;
                state.value && (val = state.value);
                state.choices && (val = state.choices.length>0 ? state.value : null);
                this.value = val;
                return val;
            },
            validate : function() {
                this.get_value();
                let error = {key: 'token-' + this.options.id, type: 'error', html: ''};
                if (_.isEmpty(this.value) && (this.options.mandatory && this.options.mandatory === true)){ 
                    error['html'] = _(`'${this.options.label}' must not be empty.`).t();
                    return error;
                }
                return true;
            }
        }); 
        var BUTTON_CREATE = '<a role="button" href="#" class="btn btn-primary modal-btn-primary btn-save">Create</a>';
         
        return Modal.extend({
            className: Modal.CLASS_NAME,
            defaults : {
                model : {},
                learnMoreTag : "learnMore",
                title : 'Not Set',
                primarybutton : BUTTON_CREATE
            },
            updatefieldmodel: function(objects, tag=""){
                var _self = this;
                if (objects) {
                    _.each(objects, function(child){
                        !child.id && (child.id = child.name);
                        !child.label && (child.label = child.name);
                        !child.type && (child.type = 'text');
                        typeof(child.important) == 'undefined' && (child.important = false);
                        child.fieldmodel = new FieldModel(child);
                        child.fieldmodel.init({id : child.id ,label:child.label, type:child.type, tag: tag, mandatory: child.mandatory});
                        if (mvc.Components.get(child.id)){
                            mvc.Components.revokeInstance(child.id);
                        }
                        child.control_label = new ControlGroup({
                            label: _(child.mandatory ? child.label+" *":child.label).t(),
                            controlType: "Label",
                            controlOptions: {
                                className: "placeholder-"+child.id,
                                model: child.fieldmodel,
                                modelAttribute: "owner"
                            }
                        });
                        switch(child.type)
                        {
                            case('picker'):
                                mvc.Components.revokeInstance(child.id + "-search");
                                if (!window.SearchManagers || !window.SearchManagers[child.id]){ 
                                    child.collection = new SearchManager({
                                        id: "search-manager-"+child.id,
                                        search: child.query,
                                        cache: false
                                    });
                                    if (!window.SearchManagers){
                                        window.SearchManagers = {};
                                    }
                                    window.SearchManagers[child.id] = child.collection;
                                } else {
                                    child.collection = window.SearchManagers[child.id];
                                    child.collection.settings.set("search",child.query)
                                }
                                var dropdown = {
                                    id: child.id,
                                    managerid: "search-manager-"+child.id,
                                    labelField: child.query_label,
                                    valueField: child.query_value,
                                    showClearButton: false,
                                    disabled : child.readonly === true,
                                    className: child.mandatory ? "pickervalue mandatory":"pickervalue",
                                    model: child.fieldmodel,
                                    width: 300,
                                    change: function(e){
                                        if (_self.model && typeof(_self.model.fieldchangehandler)=="function"){
                                            if (false == _self.model.fieldchangehandler.call(null, e))
                                            {
                                                return;
                                            }
                                        }
                                    }
                                };
                                if (child.value){
                                    dropdown.initialValue = child.value;
                                }
                                child.control_control = new DropdownView(dropdown);
                                break;
                            default:
                            case('text'):
                                child.control_control = new TextInputView({
                                    id: child.id,
                                    label: _(child.mandatory ? child.label+" *":child.label).t(),
                                    value: child.value ?? (child.default ?? '' ),
                                    disabled : child.readonly === true,
                                    className: child.mandatory ? "textvalue mandatory":"textvalue",
                                    model: child.fieldmodel,
                                    defaultvalue: child.default
                                });
                                break;
                        }
                    });
                }
                return objects;
            },
            initialize: function(options) {
                Modal.prototype.initialize.apply(this, arguments), this.action = this.options.action;
                this.options.children = [];
                this.options = _.extend({}, this.defaults, this.options);
                this.options.flashMessages = new FlashMessagesView({ model: {}});
                this.options.flashMessages.activate();
                this.options.infoMessages = new FlashMessagesView({ model: {}});
                this.options.infoMessages.activate();
                options.model && (this.model = options.model);
      
                this.model.children && (this.options.model.children = this.updatefieldmodel(this.model.children));
            },
            events: {
                'click .revert': async function(e){
                    debugger;
                },
                'click .close,.cancel': async function(e){
                    var _self = this;
                    if (this.model && typeof(this.model.cancelhandler)=="function"){
                        if (false == await this.model.cancelhandler.call(null, e))
                        {
                            return;
                        }
                    }
                    _self.options.flashMessages.flashMsgCollection.reset();
                },
                'change .textvalue': function(e){
                    if (this.model && typeof(this.model.fieldchangehandler)=="function"){
                        if (false == this.model.fieldchangehandler.call(null, e))
                        {
                            return;
                        }
                    }
                },
                'keyup .textvalue': function(e){
                    if (this.model && typeof(this.model.fieldkeyuphandler)=="function"){
                        if (false == this.model.fieldkeyuphandler.call(null, e))
                        {
                            return;
                        }
                    }
                },
                'click .save': async function(e){
                    $('.error-container').hide();
                    e.preventDefault();
                    var returnvalue = {};
                    var _self = this;
                    _self.options.flashMessages.flashMsgCollection.reset();
                    _.each($('.pickervalue,.textvalue'),function(child){
                        let $el = mvc.Components.get(child.id), tag = null;
                        $el.options.model && $el.options.model.options.tag && (tag = $el.options.model.options.tag);
                        if (!returnvalue[tag]){
                            returnvalue[tag] = [];
                        }
                        returnvalue[tag][child.id] = $el.options.model.get_value();
                        var validationresult = $el.options.model.validate();
                        if ( validationresult !== true){
                            $('.error-container').show('fast');
                            _self.options.flashMessages.flashMsgCollection.add(validationresult);
                        }
                    });
                    if (_self.options.flashMessages.flashMsgCollection.length > 0){
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
                            if (false == await this.model.savehandler.call(null, returnvalue, this)){
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
                            return;
                        }
                    }
                    _self.options.flashMessages.flashMsgCollection.reset();
                    this.model.savedhandler && this.model.savedhandler.call(null, _self, mvc);
                }
            },
            removefields: function(children, tag=""){
                var $importantForm = this.$(".important-form");
                var $unimportantForm = this.$(".unimportant-form");
                var $baseForm = this.$(".base-form");
                
                _.each(children, function(child){
                    switch(tag){
                        case 'base':
                                element = $baseForm;
                            break;
                        case 'runtime':
                        case 'environment':
                            $('.' + tag).hide();
                        default:
                            $importantForm.find('#'+child.id).parent().parent().remove();
                            $unimportantForm.find('#'+child.id).parent().parent().remove();
                            break;
                    }
                });
            },
            addfields: function(fields, tag=""){
                this.model.children = $.merge(this.model.children ?? [], this._addfields(fields,tag));
            },
            _addfields: function(fields, tag=""){
                var children = this.updatefieldmodel(fields, tag);
                var $importantForm = this.$(".important-form");
                var $unimportantForm = this.$(".unimportant-form");
                var $baseForm = this.$(".base-form");
                var $container = this.$("."+tag);
                _.each(children, function(child) {
                    var element = $unimportantForm;
                    child.tag = tag;
                    switch(tag){
                        case 'base':
                                element = $baseForm;
                            break;
                        case 'connector':
                        case 'runtime':
                        case 'environment':
                            $('.' + tag).show();
                            $container && (element = $container.find(child.important === true ? '.important-form':'.unimportant-form'))
                            break;
                        default:
                            child.important === true && (element = $importantForm);
                            break;
                    }
                    if (child.control_label && child.control_control) {
                        child.control_label && element.append(child.control_label.render().el);
                        element.find('.placeholder-'+ child.id).replaceWith(child.control_control.render().el);
                    } else if (child.control_control) {
                        element.append(child.control_control.render().el);
                    } else if (child.section_control){
                        element.append(child.section_control);
                    }
                });
                return children;

            },
            render: function() {
                if ($(' .modal').length > 0){$(' .modal')[0].remove();}
                this.$el.html(Modal.TEMPLATE), 
                this.$(Modal.HEADER_TITLE_SELECTOR).html(this.options.title);
                bodyHTML = _.template(this.bodyTemplate)(), headHTML = _.template(this.headerTemplate)();
                this.$(Modal.HEADER_SELECTOR).append(headHTML),
                this.$(Modal.BODY_SELECTOR).html(bodyHTML),
                this.$(".error-container").empty(),
                this.$(Modal.FOOTER_SELECTOR).append(Modal.BUTTON_CANCEL), 
                this.$(Modal.FOOTER_SELECTOR).append(this.options.primarybutton), 
                this.$(Modal.FOOTER_SELECTOR + " .modal-btn-primary").addClass("save"), 
                this.$(Modal.FOOTER_SELECTOR);
                this.$(".error-container").append(this.options.flashMessages.render().el),
                this.$(".info-container").append(this.options.infoMessages.render().el),
                this.$(".advanced-settings").append(new ControlGroup({
                    label: "",
                    controlType: "Label",
                    controlOptions: {
                        className: "element-more",
                        defaultValue: " Advanced Settings",
                        inputClassName: "element-more-input"
                    }
                }).render().$el);
                this.$('.element-more').addClass("icon-chevron-right");
                this.$('.advanced-settings').click(function(){
                    $('.unimportant-form').slideToggle('slow');
                    $('.element-more').toggleClass("icon-chevron-right");
                    $('.element-more').toggleClass("icon-chevron-down");
                });
                return this.children.entityTitle && $form.append(this.children.entityTitle.render().el), this._addfields(this.options.model.children,'base'), this;
            },
            headerTemplate:'<div class="error-container"></div><div class="info-container"></div>',
            bodyTemplate:  '<div class="base-form form-horizontal"></div>\
                            <div id="accordion" class="accordion-group form-horizontal">\
                                <div class="runtime-form form-horizontal"></div>\
                                <div class="card runtime">\
                                    <div class="important-form form-horizontal"></div>\
                                </div>\
                                <div class="card environment">\
                                    <div class="important-form form-horizontal"></div>\
                                </div>\
                                <div class="card runtime advanced-settings">\
                                </div>\
                                <div class="card runtime">\
                                    <div class="unimportant-form form-horizontal">\
                                    </div>\
                                </div>\
                                <div class="card connector advanced-settings">\
                                </div>\
                                <div class="card connector">\
                                    <div class="unimportant-form form-horizontal">\
                                    </div>\
                                </div>\
                                <div class="card environment">\
                                    <div class="unimportant-form form-horizontal" id="uif2"></div>\
                                </div>\
                            </div>'
        });
    });