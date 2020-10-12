define([
    'underscore',
    'jquery',
    'splunkjs/mvc',
    'views/shared/Modal',
    'views/shared/FlashMessages',
    'css!./modalview.css'
    ], function(_, $, mvc, Modal, FlashMessagesView) {
        return Modal.extend({
            className: Modal.CLASS_NAME + " modal-with-spinner",
            defaults : {
                model : {
                    text : 'Lorem Ipsum dolor sit',
                    title : 'Not Set'
                }
            },
            events: {
                'click .close,.cancel': function(e){
                    var _self = this;
                    e.modal = _self;
                    if (this.model && typeof(this.options.cancelhandler)=="function"){
                        if (false == this.options.cancelhandler.call(null, e))
                        {
                            return;
                        }
                    }
                    _self.options.flashMessages.flashMsgCollection.reset();
                },
                'click .btn-primary': async function(e){
                    e.preventDefault();
                    $('.error-container').hide('fast');
                    var _self = this;
                    this.options.flashMessages.flashMsgCollection.reset();

                    if (this.model && typeof(this.options.actionhandler)=="function"){
                        try {
                            $('.info-container').show('fast');
                            this.options.flashMessages.flashMsgCollection.add({
                                key: 'token-info',
                                type: 'info',
                                html: _.escape(_("Saving..... Please be patient.").t())
                            });
                            if (true == await this.options.actionhandler.call(null, e, _self, mvc)){
                                _self.options.flashMessages.flashMsgCollection.reset();
                                _self.hide();
                            }
                        } catch (e){
                            $('.info-container').hide('fast');
                            this.options.flashMessages.flashMsgCollection.reset();
                            this.options.flashMessages.flashMsgCollection.reset();
                            $('.error-container').show('fast');
                            this.options.flashMessages.flashMsgCollection.add({
                                key: 'token-function-save',
                                type: 'error',
                                html: _.escape(_(JSON.stringify(e.data!=false ? e.data : e.message)).t())
                            });
                            return false;
                        }
                    }
                },
            },
            initialize: function(options) {
                Modal.prototype.initialize.apply(this, arguments), this.action = this.options.action;
                this.options = _.extend({}, this.defaults, options);
                this.options.flashMessages = new FlashMessagesView({ model: {}});
                this.options.flashMessages.activate();
            },
            render: function() {
                if ($(' .modal').length > 0){$(' .modal')[0].remove();}
                this.$el.html(Modal.TEMPLATE), this.$(Modal.HEADER_TITLE_SELECTOR).html(this.options.model.title);
                bodyHTML = _.template(this.bodyTemplate)(this.options.model);
                headHTML = _.template(this.headerTemplate)(this.options.model);
                this.$(Modal.BODY_SELECTOR).append(bodyHTML),
                this.$(Modal.HEADER_SELECTOR).append(headHTML),
                this.$(".error-container").append(this.options.flashMessages.render().el),
                this.$(Modal.FOOTER_SELECTOR).append(Modal.BUTTON_CANCEL), 
                this.$(Modal.FOOTER_SELECTOR).append(this.options.model.button);
                $('.error-container').hide('fast');
            },
            headerTemplate:'<div class="error-container"></div><div class="info-container"></div>',
            bodyTemplate:'<div class="confirm-body">\
                <p><%-text%></p>\
            </div>'
        });
    }
);