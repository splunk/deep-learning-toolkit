define(
    [
        'jquery',
        'underscore',
        'module',
        'splunkjs/mvc',
        'views/Base',
        'models/Base',
        './dropdownview',
        './textinputview',
         'splunkjs/mvc/searchmanager',
        'views/shared/controls/ControlGroup'
    ],
    function(
        $,
        _,
        module,
        mvc,
        BaseView,
        BaseModel,
        DropdownView,
        TextInputView,
        SearchManager,
        ControlGroup
    ){
        var FieldModel = BaseModel.extend({
            validation: {
                value: function(value, attr, computedState) {
                    if (_.isEmpty(value)) return _("Please enter a value.").t()
                }
            }
        }); 
        return BaseView.extend({
            moduleId: module.id,
            className: 'form form-horizontal tabular-content',
            initialize: function(options) {
                this.label = _(options.heading).t();
                BaseView.prototype.initialize.apply(this, arguments);
                this.activate();
            },
            updatefieldmodel: function(objects){
                var _self = this;
                if (objects) {
                    _.each(objects, function(child){
                        !child.id && (child.id = child.name);
                        !child.label && (child.label = child.name);
                        !child.type && (child.type = 'text');
                        !child.category && child.environment && (child.category = 'deployment');
                        !child.category && !child.environment && (child.category = 'algorithm');
                        typeof(child.important) == 'undefined' && (child.important = false);
                        child.fieldmodel = new FieldModel(child);
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
                                if (child.value!=undefined){
                                    dropdown.initialValue =  child.value;
                                }
                                child.control_control = new DropdownView(dropdown);
                                break;
                            default:
                            case('text'):
                                child.control_control = new TextInputView({
                                    id: child.id,
                                    label: _(child.mandatory ? child.label+" *":child.label).t(),
                                    value: child.value,
                                    disabled : child.readonly === true,
                                    className: (child.mandatory ? "textvalue mandatory" : "textvalue") + " " + (child.category=='deployment' ? "deployment "+ child.environment : "algorithm"),
                                    defaultvalue: child.default
                                });
                                break;
                        }
                    });
                }
                return objects;
            },
            activate: function(options) {
                if (this.active) {
                    return BaseView.prototype.activate.apply(this, arguments);
                }
                return BaseView.prototype.activate.apply(this, arguments);
            },
            deactivate: function(options) {
                if (!this.active) {
                    return BaseView.prototype.deactivate.apply(this, arguments);
                }
                BaseView.prototype.deactivate.apply(this, arguments);
                return this;
            },
            _addfields: function(tag=""){
                var children = this.updatefieldmodel(this.options.collection);
                var $importantForm = this.$(".important-form");
                var $unimportantForm = this.$(".unimportant-form");
                var $baseForm = this.$(".base-form");
                var $container = this.$("."+tag);
                _.each(children, function(child) {
                    var element = $unimportantForm;
                    switch(tag){
                        case 'base':
                                element = $baseForm;
                            break;
                        case 'content':
                            $('.' + tag).show();
                            $container && (element = $container.find(child.important === true ? '.important-form':'.notsoimportant-form'))
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
                this.$el.html(this.compiledTemplate({_:_}));
                this._addfields('content');
                return this;
            },
            template:  
                ' <div class="accordion-group form-horizontal">\
                    <div class="runtime-form form-horizontal"></div>\
                    <div class="card content">\
                        <div class="important-form form-horizontal"></div>\
                        <div class="notsoimportant-form form-horizontal"></div>\
                    </div>\
                </div>'
        });
    }
);
