define(function(require, exports, module) {
    var _ = require('underscore');
    var BaseChoiceView = require("splunkjs/mvc/basechoiceview");
    var Dropdown = require('splunkjs/mvc/components/Dropdown');
    
    //20200826 We need this cause std dropdownview has no exposed changeevent
    var DropdownView = BaseChoiceView.extend({/** @lends splunkjs.mvc.DropdownView.prototype */
        moduleId: module.id,
        className: "splunk-dropdown splunk-choice-input",
        getReactComponent: function() {
            return Dropdown;
        },
        resetValue: function() {
            this.val(this.settings.get('default'));
        },
        getState: function() {
            var baseState = BaseChoiceView.prototype.getState.apply(this, arguments);
            return _.extend({}, baseState, {
                allowCustomValues: this.settings.get('allowCustomValues'),
                id: this.settings.get('id'),
                minimumResultsForSearch: this.settings.get('minimumResultsForSearch'),
                defaultValue: this.settings.get('default'),
                showClearButton: this.settings.get('showClearButton'),
                width: this.settings.get('width'),
                onReset: this.resetValue.bind(this),
                onChange: function(value) {
                    this.onUserInput();
                    this.val(value);
                    this.settings.get('change') && this.settings.get('change').call(this,{target:{value: value},currentTarget:{id: this.id}});
                }.bind(this)
            });
        }
    });
    return DropdownView;
});
