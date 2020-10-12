define([
    "underscore",
    'splunkjs/mvc/textinputview'
], function (_, TextInputView) {
    return TextInputView.extend({
        initialize: function (options) {
            TextInputView.prototype.initialize.apply(this, arguments);
            this.options = options;
            options.defaultvalue && (this.defaultvalue = options.defaultvalue);
            this.value = options.value;
        },
        render: function (e) {
            var base = TextInputView.prototype.render.apply(this, arguments);
            if (!this.defaultvalue)
                return base;
            if (this.value === null) {
                this.$el.find('input').attr("placeholder", this.defaultvalue);
                /*const that = this;
                this.$el.find('input').keydown(function (e) {
                    if ((this.value === ""|| e.keyCode==9) && that.breakit) {
                        that.$el.find('input').removeAttr("placeholder");
                    }
                    else
                        that.breakit = true;
                });*/
            }
            return base;
        },
        revertTemplate: '<a class="revert" data-target="<%-target%>" data-value="<%-oldvalue%>">r</a>',
    });
});