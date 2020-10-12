define([
    "underscore",
    'splunkjs/mvc/tableview',
    'splunkjs/mvc/searchmanager',
    'splunkjs/mvc/chartview',
    '../../components/statuscellrenderer',
    '../../components/editorcellrenderer',
    '../../components/menucellrenderer',
    "css!./algorithmrowrenderer.css"
], function(_,TableView,SearchManager,ChartView,StatusCellRenderer,EditorCellRenderer, MenuCellRenderer){   
    return TableView.BaseRowExpansionRenderer.extend({
        canRender: function(rowData) {
            return true;
        },
        createDeploymentSearchManager: function(algorithm){
            return new SearchManager({
                preview: true,
                cache: false,
                search: this.options.rowdeloymentsquery.replace("$algorithm$",algorithm),
                refresh :'13s',
                earliest_time: "-24h@h",
                latest_time: "now",
            });
        },
        createMethodsSearchManager: function(algorithm){
            return new SearchManager({
                preview: true,
                cache: false,
                search: this.options.rowmethodsquery.replace("$algorithm$",algorithm),
                refresh: '13s',
                earliest_time: "-24h@h",
                latest_time: "now",
            });
        },
        createVizSearchManager: function(algorithm){
            return new SearchManager({
                preview: true,
                cache: false,
                search: this.options.rowvizquery.replace("$algorithm$",algorithm),
                refresh: '13s',
                earliest_time: "-24h@h",
                latest_time: "now",
            });
        },
        initialize: function(options) {
            TableView.BaseRowExpansionRenderer.prototype.initialize.apply(this, arguments);
            this.options = _.extend({}, options, this.options);
        },
        setup: function(e){
            //f*ck the pain away
            $('.expanded-content-row').removeClass("expanded-content-row");
            $('.expanded-row').removeClass("expanded-row");
        },
        render: function($container, rowData) {
            $container.html(_.template(this.template)({entityname:rowData.cells[0].value ?? 'NaN'}));
            $container.searchDeployments = this.createDeploymentSearchManager(rowData.cells[0].value ?? 'NaN') ;
          
            $container.deploymenttableview = new TableView({
                managerid: $container.searchDeployments.id,
                drilldown: "none",
                element: "#deploymentstable"
            });
            $container.deploymenttableview.settings.set("refreshDisplay","progressbar");
           
            var cellExtrasRenderer = new StatusCellRenderer();
            var cellEditorRenderer = new EditorCellRenderer({typestring:'deployments',values : {entityname:rowData.cells[0].value}});

            $container.deploymenttableview.addCellRenderer(cellExtrasRenderer);
            $container.deploymenttableview.addCellRenderer(cellEditorRenderer);
           
            var $form =  $($container).find('#deploymentstable');
            $form.append($container.deploymenttableview.render().el);

            $container.searchMethods = this.createMethodsSearchManager(rowData.cells[0].value ?? 'NaN') ;
            $container.methodstableview = new TableView({
                managerid: $container.searchMethods.id,
                drilldown: "none",
                element: "#methodstable"
            });
            $container.methodstableview.settings.set("refreshDisplay","progressbar");
            
            cellExtrasRenderer = new StatusCellRenderer();
            cellEditorRenderer = new EditorCellRenderer({typestring:'methods',values : {entityname:rowData.cells[0].value}});
            
            $container.methodstableview.addCellRenderer(cellExtrasRenderer);
            $container.methodstableview.addCellRenderer(cellEditorRenderer);
            var $form =  $($container).find('#methodstable');
            $form.append($container.methodstableview.render().el);

            $container.searchViz = this.createVizSearchManager(rowData.cells[0].value ?? 'NaN');
            $container.fancyChart = new ChartView({
                managerid: $container.searchViz.id,
                type: "line",
                "charting.chart.stackMode": "stacked",
               "charting.axisLabelsX.majorLabelStyle.overflowMode":"ellipsisNone",
               "charting.axisLabelsX.majorLabelStyle.rotation":"0",
               "charting.axisTitleX.visibility":"collapsed",
               "charting.axisTitleY.visibility":"collapsed",
               "charting.axisTitleY2.visibility":"visible",
               "charting.axisX.abbreviation":"none",
               "charting.axisX.scale":"linear",
               "charting.axisY.abbreviation":"none",
               "charting.axisY.scale":"linear",
               "charting.axisY2.abbreviation":"none",
               "charting.axisY2.enabled":"0",
               "charting.axisY2.scale":"inherit",
               "charting.chart":"line",
               "charting.chart.bubbleMaximumSize":"50",
               "charting.chart.bubbleMinimumSize":"10",
               "charting.chart.bubbleSizeBy":"area",
               "charting.chart.nullValueMode":"connect",
               "charting.chart.showDataLabels":"none",
               "charting.chart.sliceCollapsingThreshold":"0.01",
               "charting.chart.stackMode":"default",
               "charting.chart.style":"shiny",
               "charting.drilldown":"none",
               "charting.layout.splitSeries":"0",
               "charting.layout.splitSeries.allowIndependentYRanges":"0",
               "charting.legend.labelStyle.overflowMode":"ellipsisMiddle",
               "charting.legend.mode":"standard",
               "charting.legend.placement":"bottom",
               "charting.lineWidth":"2",
               "trellis.enabled":"0",
               "trellis.scales.shared":"1",
               "trellis.size":"medium",
                el: $("#rowvizualisation")
            });
            $container.fancyChart.render();
            $container.fancyChart.settings.set("refreshDisplay","progressbar");
            
        },
        template: 
            '<div class="row-container shared-fieldinfo">\
                <div id="rowinrow">\
                    <div id="deploymentstable" class="environments-container">\
                        <h4 class="field-info-header" style="margin-bottom: 7px">Deployments</h4>\
                    </div>\
                    <div id="methodstable" class="methods-container">\
                        <h4 class="field-info-header" style="margin: 23px 0 7px 0">Methods</h4>\
                    </div>\
                </div>\
                <div id="rowvizualisation" class="visualization-container">\
                    <h4 class="field-info-header" style="margin-bottom: 7px">Activity by Method</h4>\
                </div>\
            </div>' 
    });
});
