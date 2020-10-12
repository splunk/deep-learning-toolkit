define([
    "underscore",
    'views/shared/waitspinner/Master',
    'splunkjs/mvc/tableview'
], function(_,WaitSpinner,TableView ){   
    var ICONS = {
        deployed: { icon : 'icon-check-circle', color : 'rgb(92, 192, 92)'},
        deploying: { icon : 'spinner-medium', color : 'gray'},
        undeploying: { icon : 'spinner-medium', color : 'gray'},
        disabling: { icon : 'spinner-medium', color : 'gray'},
        disabled: { icon : 'icon-warning-sign', color : 'gray'},
        error: { icon : 'icon-error', color : 'red'},
        question: { icon : 'icon-box-unchecked', color : 'gray'},
        empty : { icon : '', color : 'lightgray'}
    };
    var StatusCellRenderer = TableView.BaseCellRenderer.extend({
        initialize: function(options) {
            TableView.BaseCellRenderer.prototype.initialize.apply(this, arguments);
            this.options = options;
        },
        canRender: function(cellData) {
            return cellData.field.toLowerCase() === 'status';
        },
        setup: function($td, cellData) {
            $td.addClass("ConditionalExtras");
        },
        teardown: function($td, cellData) {
            $td.removeClass("ConditionalExtras");
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
            var icon = 'question';
            var color = 'lightgray';
            var filteredValue = this.filterStats(cellData.value);
            if (!filteredValue || filteredValue === ""){
                filteredValue = "empty";
            }
            if(ICONS.hasOwnProperty(filteredValue)) {
                icon = ICONS[filteredValue].icon,
                color = ICONS[filteredValue].color
            }
            if (filteredValue == "deploying"){
                var spinner = new WaitSpinner();
                $td.append(spinner.render().el);
                spinner.$el.show();
                spinner.start();
            } else {
                $td.addClass('icon').html(_.template('<i style="color:<%-color%>" class="<%-icon%> <%- value %>" title="<%- value %>"></i>', {
                    icon: icon,
                    color: color,
                    value: cellData.value
                }));
                
            }
            $td.attr("width","60");
        }
    });
    return StatusCellRenderer;
});