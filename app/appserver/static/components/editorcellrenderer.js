define([
    "underscore",
    './basecellrenderer'
 ], function(_,BaseCellRenderer ){   
    var ToggleStatusCellRenderer = BaseCellRenderer.extend({
        initialize: function(options) {
            BaseCellRenderer.prototype.initialize.apply(this, arguments);
            this.options = options;
        },
        canRender: function(cellData) {
            return cellData.field.toLowerCase() === 'actions';
        },
        setup: function($td, cellData) {
            $td.addClass("editor-link");
        },
        teardown: function($td, cellData) {
            $td.removeClass("editor-link");
        },
        render: function($td, cellData) {
            var cellmodel = this._targetModel(arguments,cellData);
            if (cellmodel.url && typeof(cellmodel.url) !="string" && cellmodel.url[0])
                cellmodel.url = cellmodel.url[0];

            $td.append(_.template(this.templateMenuContainer)(cellmodel));
            $td.attr("width","98");
        },
        templateMenuContainer : 
            '<div class="menu-container">\
                <% if (url) { %>\
                <a class="external editor btn-pill" data-entityname="<%-entityname%>" data-status="<%-status%>" data-environment="<%-environment%>" data-url="<%-url%>">Editor</a>\
                <% } %>\
                <a class="icon-chevron-down btn-pill menu-click" data-type="<%-type%>" data-entityname="<%-entityname%>" data-method="<%-method%>" data-environment="<%-environment%>" data-status="<%-status%>" data-runtime="<%-runtime%>" data-connector="<%-connector%>"  data-url="<%-url%>"></a>\
            </div>',
        
    });
    return ToggleStatusCellRenderer;
});

