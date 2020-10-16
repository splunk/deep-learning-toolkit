define([
    "underscore",
    "backbone",
    "jquery",
    'views/shared/Modal',
    'controllers/Base',
    '../../components/modalconfirm',
    '../../components/modaledit',
    '../../components/modalview',
   '../../utils/rest',
   '../fieldset/newenvironmentfields',
   '../fieldset/newdeploymentfields',
   '../fieldset/newmethodfields',
   '../fieldset/editparameterfields'
], function(
        _, 
        Backbone, 
        $, 
        ModalView, 
        BaseController,
        ModalConfirm, 
        ModalEdit, 
        CreateModalView, 
        rest,
        NewEnvironmentFields,
        NewDeploymentFields, 
        NewMethodFields,
        EditParameterFields
    ){
    var BUTTON_OK = '<a role="button" href="#" class="btn btn-primary modal-btn-primary btn-save">Ok</a>';
    return BaseController.extend({
        initialize: function(options) {
            BaseController.prototype.initialize.apply(this, arguments);
            this.collection = this.collection || {};
            this.children = this.children || {};
            this.model = this.model || {};
            this.deferreds = this.deferreds || {};
            // Setup event listeners to the view we are controlling
            
            //Environment
            this.on("action:show-create", this.show_create, this);
            this.on("action:delete-environment", this.delete_environment, this);
            
            this.on("action:edit-environment", this.edit_environment, this);
        },
        show_create : function(element){
            var $Modal = element;
            $Modal.children.createDialog = new CreateModalView({
                title: 'Create Environment',
                changedFields: {},
                model: {
                    children: JSON.parse(JSON.stringify(NewEnvironmentFields)),
                    cancelhandler: async function (e) {
                        $Modal.children.createDialog.changedFields = {};
                        return true;
                    },
                    savehandler: async function (modalvalues, el) {
                        var environment = {};
                        let r = modalvalues['base'], p = modalvalues['runtime'];
                        if (r){
                            for (var key in r){
                                if (r[key] && typeof(r[key])!='function'){
                                    environment[key] = _.escape(_(r[key]).t());
                                }
                            }
                            await rest.createRestEndpoint().postAsync(`environments`, environment);
                            if (p){
                                for (var key in p){
                                    if (p[key] && typeof(p[key])!='function')
                                        environment[key] = _.escape(_(p[key]).t());
                                }
                                await rest.createRestEndpoint().putAsync(`environment_params`, environment);
                            }
                        }
                    },
                    savedhandler: async function (el, m) {
                        $Modal.children.createDialog.changedFields = {};
                        el.hide();
                    },
                    fieldchangehandler: async function (evt) {
                        $('.error-container').hide('fast');
                        $('.info-container').hide('fast');
                        var value = evt.target.value;
                        var fieldname = evt.currentTarget.id;
                        $Modal.children.createDialog.changedFields[fieldname] = value;
                        if ("connector" == fieldname) {
                            $Modal.children.createDialog.removefields($('.connector').find('.textvalue,.pickervalue'));
                            const result = await rest.createRestEndpoint().getAsync(`environment_params`, { connector: encodeURIComponent($Modal.children.createDialog.changedFields['connector']) });
                            const fieldconfig = await rest.getResponseContents(result);
                            var input = [];
                            _.each(fieldconfig, function (field) {
                                input.push(field);
                            });
                            $Modal.children.createDialog.addfields(input,"connector");
                        }
                    }
                },
                onHiddenRemove: !0,
                backdrop: "static"
            });
            $Modal.children.createDialog.changedFields = {};
            $("body").append($Modal.children.createDialog.render().el), 
            $Modal.children.createDialog.show();
        },
        edit_environment : async function(element,model){
            var $Modal = element;
            var deployments = {};
            var algorithm_params = [];
            var deployment_params = [];
            var children = [];
            try 
            {
                result = await rest.createRestEndpoint().getAsync(`environment_params`, { environment: model.entityname, include_deployments:1});
                if (!result.data || !result.data.entry || !result.data.entry[0] || !result.data.entry[0].content){
                    return;
                }
                _.each(result.data.entry,function(value){
                    let env = value.content.environment;
                    if (!env || env ==''){
                        algorithm_params.push(value.content);
                    }
                    else {
                        if (!deployments[env]){
                            deployments[env] = []
                        }
                        deployments[env].push(value.content);
                    }
                });
                children.push({collection: algorithm_params, label: model.entityname});
                for (key in deployments) {
                    if (typeof(deployments[key])=='function'){
                        continue;
                    }
                    children.push({collection: deployments[key], label: key});
                }
            } catch (ex) {
                console.log(JSON.stringify(ex));
                return;
            }
            var fields = EditParameterFields;
            fields[0].value = model.entityname;
            fields[1].value = model.runtime;
            const BUTTON_UPDATE = '<a role="button" href="#" class="btn btn-primary modal-btn-primary btn-save">Update</a>';
            $Modal.children.createDialog = new ModalEdit({
                title: 'Settings',
                primarybutton: BUTTON_UPDATE,
                changedFields: {},
                model: {
                    children: children,
                    basefields : fields, 
                    cancelhandler: async function (e) {
                        $Modal.children.createDialog.changedFields = {};
                        return true;
                    },
                    savehandler: async function (r, el) {
                        var algorithm = {};
                        var _m = {environment : model.entityname};
                        for (var subkey in r.algoparams){
                            if (typeof(r.algoparams[subkey])=='function')
                                continue;

                            _m[subkey]=r.algoparams[subkey];
                        }
                        await rest.createRestEndpoint().putAsync(`environment_params`, _m);
                    },
                    savedhandler: async function (el, m) {
                        $Modal.children.createDialog.changedFields = {};
                        el.hide();
                    },
                    fieldchangehandler: async function (evt) {
                        $('.error-container').hide('fast');
                        $('.info-container').hide('fast');
                        var value = evt.target.value;
                        var fieldname = evt.currentTarget.id;
                        $Modal.children.createDialog.changedFields[fieldname] = value;
                    },
                    fieldkeyuphandler: async function (evt) {
                    },
                    
                },
                onHiddenRemove: !0,
                backdrop: "static"
            });
            $Modal.children.createDialog.changedFields = {};
            $("body").append($Modal.children.createDialog.render().el), 
            $Modal.children.createDialog.show();
        },
        delete_environment : async function(e,model){
            e.children.deleteDialog = new ModalConfirm({
                model : {
                    title : 'Delete Environment',
                    text : `Do you really want to delete ${model.entityname}?`,
                    button: ModalView.BUTTON_DELETE
                },
                actionhandler : async function(e, modal, m){
                    await rest.createRestEndpoint().delAsync(`environments`, {
                        name : model.entityname, environment: model.environment
                    });
                    return true;
                }
            }),
            $("body").append(e.children.deleteDialog.render().el), 
            e.children.deleteDialog.show();
        }
    });
});