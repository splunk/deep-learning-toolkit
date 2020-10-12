define([
    "underscore",
    "backbone",
    "jquery",
    'views/shared/Modal',
    'splunkjs/mvc/tableview',
    'splunkjs/mvc/searchmanager',
    './environmentcontroller',
    '../../components/editorcellrenderer',
    '../../components/menucellrenderer',
    '../../components/modalconfirm',
    '../../components/rowmenu',
    '../../utils/rest',
    "css!./environmentcontrols.css"
], function(
        _, 
        Backbone, 
        $, 
        ModalView, 
        TableView, 
        SearchManager, 
        MenuController,
        EditorCellRenderer, 
        MenuCellRenderer, 
        ModalConfirm, 
        RowMenu, 
        rest
    ){
    var TableViewWithExtras = TableView.extend({
        initialize: function(options) {
            TableView.prototype.initialize.apply(this, arguments);
            this.options = _.extend({}, options, this.options);
        },
        addRenderer:function(){
            var _self = this,
            cellEditorRenderer = new EditorCellRenderer({typestring:'environments', tableview: _self});
            this.addCellRenderer(cellEditorRenderer);
        }
    });
    return Backbone.View.extend({
        className: "tableviewwithextras",
        defaults: {
            
        },
        _prepareEventModel:function(e){
            var entityname = undefined,status = undefined,environment = undefined,url = undefined,runtime = undefined,enabledisable=undefined,type=undefined,method=undefined;
            e.currentTarget.dataset && e.currentTarget.dataset['entityname'] && (entityname = e.currentTarget.dataset['entityname']);
            e.currentTarget.dataset && e.currentTarget.dataset['type'] && (type = e.currentTarget.dataset['type']);
            e.currentTarget.dataset && e.currentTarget.dataset['status'] && (status = e.currentTarget.dataset['status']);
            e.currentTarget.dataset && e.currentTarget.dataset['environment'] && (environment = e.currentTarget.dataset['environment']);
            e.currentTarget.dataset && e.currentTarget.dataset['url'] && (url = e.currentTarget.dataset['url']);
            e.currentTarget.dataset && e.currentTarget.dataset['runtime'] && (runtime = e.currentTarget.dataset['runtime']);
            e.currentTarget.dataset && e.currentTarget.dataset['enabledisable'] && (enabledisable = e.currentTarget.dataset['enabledisable']);
            e.currentTarget.dataset && e.currentTarget.dataset['method'] && (method = e.currentTarget.dataset['method']);
            return {
                entityname : entityname,
                status : status,
                environment : environment,
                url: url,
                runtime:runtime,
                enabledisable:enabledisable,
                type: type,
                method: method
            }
        },
        events: {
            'click .editor':function(e){
                e.preventDefault();
                var url = undefined;
                e.currentTarget.dataset && e.currentTarget.dataset['url'] && (url = e.currentTarget.dataset['url']);
                this._triggerControllerEvent('action:open-editor',this,this._prepareEventModel(e));
            },
            'click .menu-click':function(e){
                e.preventDefault();
                this.children.otherMenu = new RowMenu({
                    model: this.model,
                    collection: this._prepareEventModel(e),
                });
                this.children.otherMenu.once('hide', this.children.otherMenu.remove);
                $('body').append(this.children.otherMenu.render().$el);
                var $btn = $(e.currentTarget);
                $btn.addClass('active');
                this.children.otherMenu.show($btn);
                this.children.otherMenu.once('hide', function () {
                    $btn.removeClass('active');
                });
            },
            'click .toggle-status':function(e){
                e.preventDefault();
                var model = this._prepareEventModel(e);
                model.enabledisable = "enable";
                if (model.status == 'deployed'){
                    model.enabledisable = "disable";
                }
                this._triggerControllerEvent('action:toggle-status',this,model);
            },
            'click .delete-algorithm':function(e){
                e.preventDefault();
                this._triggerControllerEvent('action:delete-algorithm',this,this._prepareEventModel(e),$('body'));
            }
        },
        initialize: function() {
            Backbone.View.prototype.initialize.apply(this, arguments);
            this.model = new Backbone.Model();
            this.options = _.extend({}, this.defaults, this.options);
            this.model.controller = new MenuController(this.options);
            this.children = this.children || {};
            this.element_options = this.element_options || {};
            this.$el[0] && this.$el[0].dataset && this.$el[0].dataset.basequery && (this.element_options.basequery = this.$el[0].dataset.basequery);
            this.$el[0] && this.$el[0].dataset && this.$el[0].dataset.parameterquery && (this.element_options.parameterquery = this.$el[0].dataset.parameterquery);
            this.options = _.extend(this.element_options, this.options);
            this.children.searchmanager = new SearchManager({
                preview: false,
                cache: true,
                search: this.options.basequery,
                refresh: '11s',
                earliest_time: "-24h@h",
                latest_time: "now",
                //
            });
            this.children.tableview = new TableViewWithExtras({
                id: "environmentstable",
                managerid: this.children.searchmanager.id,
                drilldown: "none",
                wrap: true,
                pageSize: 50,
                className: "results-table wrapped-results"
            });
            //this.children.searchmanager.settings.set("refreshDisplay","progressbar");
            //this.children.tableview.settings.set("refreshType","none");
            this.children.tableview.settings.set("refreshDisplay","progressbar");
        },
        _triggerControllerEvent: function () {
            this.model.controller.trigger.apply(this.model.controller, arguments);
        },
        render: function () {
            var model = _.extend({}, this.model, this.options);
            this.$el.addClass(this.className);
            this.$el.html(this.template(model));
            var $form =  this.$(".tableview-container");
            this.children.tableview.addRenderer();
            $form.append(this.children.tableview.render().el);
        },
        template: _.template('<div id="environmentstableview" class="tableview-container"></div>')
    });
});