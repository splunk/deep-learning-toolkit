define([
    "underscore",
    'views/shared/waitspinner/Master',
    'splunkjs/mvc/tableview',
    './rowmenu'
], function(_,WaitSpinner,TableView,RowMenu ){   
    return TableView.BaseCellRenderer.extend({
        initialize: function(options) {
            TableView.BaseCellRenderer.prototype.initialize.apply(this, arguments);
            this.typestring = 'algorithms';
            options && (this.typestring = options.typestring ?? 'algorithms');
            options && (this.defaultValues = options.values);
            !this.defaultValues && (this.defaultValues = {});
        },
        _targetModel : function(arg,cellData) {
            let rowdata = [];
            let status,entityname,environment,url,name,runtime,method;
            arg.callee &&  arg.callee.caller &&  arg.callee.caller.arguments &&  arg.callee.caller.arguments[2] && (rowdata = arg.callee.caller.arguments[2]);
            _.each(rowdata,function(valueobj){
                switch(valueobj.field.toLowerCase()){
                    case('status'):
                        status = _.escape(valueobj.value);
                        break;
                    case('environment'):
                        environment = _.escape(valueobj.value);
                        break;
                    case('algorithm'):
                        entityname = _.escape(valueobj.value);
                        break;
                    case('name'):
                        name = _.escape(valueobj.value);
                        break;
                    case('method'):
                        method = _.escape(valueobj.value);
                        break;
                    case('url'):
                    case('actions'):
                        url = _.escape(valueobj.value);
                        break;
                    case('runtime'):
                        runtime = _.escape(valueobj.value);
                        break;
                }
            });
            let _model = {
                url:url,
                entityname:entityname ?? name,
                environment:environment,
                status:status,
                runtime:runtime,
                cellData: cellData,
                type: this.typestring ?? 'algorithm',
                method: method
            };
            $.each(this.defaultValues, function(key, value){
                _model[key] = value;
            });
            return _model;
        }
    });
});