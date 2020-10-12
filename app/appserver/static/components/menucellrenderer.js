define([
    "underscore",
     './basecellrenderer'
], function(_,BaseCellRenderer){   
    var MenuCellRenderer = BaseCellRenderer.extend({
        initialize: function(options) {
            BaseCellRenderer.prototype.initialize.apply(this, arguments);
            this.options = options;
        },
        canRender: function(cellData) {
            return cellData.field.toLowerCase() === '...';
        },
        setup: function($td, cellData) {
            //$td.addClass("ConditionalExtras");
        },
        teardown: function($td, cellData) {
            //$td.removeClass("ConditionalExtras");
        },
        filterStats:function(data){
            if (!data || data == "undefined")
                return 'empty';

            var status = JSON.stringify(data);
            if (status.indexOf("deployed")>-1){
                return 'deployed';
            }
            if (status.indexOf("error")>-1){
                return 'error';
            }
            if (typeof(data)!='object')
                return data;

            return data[0];
        },
        render: function($td, cellData) {
            $td.attr("width","10");
            $td.append(_.template(this.templateMenuContainer)(this._targetModel(arguments,cellData)));
        },
        templateMenuContainer : '<div class="menu-container"><i class="caret menu-click" data-type="<%-type%>" data-entityname="<%-entityname%>" data-method="<%-method%>" data-environment="<%-environment%>" data-status="<%-status%>" data-runtime="<%-runtime%>" data-url="<%-url%>" ></i></div>',
      
    });
    return MenuCellRenderer;
});