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
   '../fieldset/newalgorithmfields',
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
        NewAlgorithmFields,
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
            //genral
            this.on("action:open-editor", this.open_editor, this);
            //algo
            this.on("action:show-create", this.show_create, this);
            this.on("action:delete-algorithm", this.delete_algorithm, this);
            this.on("action:edit-algorithm", this.edit_parameters, this);
            //methods
            this.on("action:add-method", this.show_create_method, this);
            this.on("action:delete-method", this.delete_method, this);
                        
            //deployment
            this.on("action:toggle-status", this.toggle_status, this);
            this.on("action:add-deployment", this.show_create_deployment, this);
            this.on("action:restart-deployment", this.restart_deployment, this);
            this.on("action:delete-deployment", this.delete_deployment, this);
            this.on("action:edit-deployment", this.edit_parameters, this);
        },
        open_editor : function(e,model){
            model.url && window.open(model.url);
        },
        show_create : function(element){
            var $Modal = element;
            $Modal.children.createDialog = new CreateModalView({
                title: 'Create Algorithm',
                changedFields: {},
                model: {
                    children: JSON.parse(JSON.stringify(NewAlgorithmFields)),
                    cancelhandler: async function (e) {
                        $Modal.children.createDialog.changedFields = {};
                        return true;
                    },
                    savehandler: async function (modalvalues, el) {
                        var algorithm = {};
                        let r = modalvalues['base'], p = modalvalues['runtime'];
                        if (r){
                            for (var key in r){

                                if (r[key] && typeof(r[key])!='function')
                                    algorithm[key] = _.escape(_(r[key]).t());
                            }
                            await rest.createRestEndpoint().postAsync(`algorithms`, algorithm);
                            if (algorithm['environment']){
                                var deployment = {
                                    algorithm: _.escape(_(algorithm["name"]).t()),
                                    environment: _.escape(_(algorithm["environment"]).t()) 
                                }                            
                                await rest.createRestEndpoint().postAsync(`deployments`, deployment);
                            }
                            if (p){
                                var algoparams = {
                                    algorithm: _.escape(_(algorithm["name"]).t())
                                };
                                for (var key in p){
                                    
                                    if (p[key] && typeof(p[key])!='function'){
                                        algoparams[key] = _.escape(_(p[key]).t());
                                    }
                                }
                                await rest.createRestEndpoint().putAsync(`algorithm_params`, algoparams);
                            }
                        }
                    },
                    savedhandler: async function (el, m) {
                        $Modal.children.createDialog.changedFields = {};
                        //m.Components.get("algortihms-search") && m.Components.get("algortihms-search").startSearch();
                        el.hide();
                    },
                    fieldchangehandler: async function (evt) {
                        $('.error-container').hide('fast');
                        $('.info-container').hide('fast');
                        var value = evt.target.value;
                        var fieldname = evt.currentTarget.id;
                        $Modal.children.createDialog.changedFields[fieldname] = value;
                        if ("runtime" === fieldname) {
                            $Modal.children.createDialog.removefields($('.runtime').find('.textvalue,.pickervalue'));
                            const result = await rest.createRestEndpoint().getAsync(`algorithm_params`, { runtime: encodeURIComponent($Modal.children.createDialog.changedFields['runtime']) });
                            const fieldconfig = await rest.getResponseContents(result);
                            var input = [];
                            _.each(fieldconfig, function (field) {
                                input.push(field);
                            });
                            $Modal.children.createDialog.addfields(input,"runtime");
                            if ("environment" in $Modal.children.createDialog.changedFields){
                                fieldname = "environment";
                            }
                        }
                        if ("environment" == fieldname && "runtime" in $Modal.children.createDialog.changedFields) {
                            $Modal.children.createDialog.removefields($('.environment').find('.textvalue,.pickervalue'));
                            const result = await rest.createRestEndpoint().getAsync(`deployment_params`, {
                                runtime: encodeURIComponent($Modal.children.createDialog.changedFields['runtime']),
                                environment: encodeURIComponent($Modal.children.createDialog.changedFields['environment'])
                            });
                            const fieldconfig = await rest.getResponseContents(result);
                            var input = [];
                            _.each(fieldconfig, function (field) {
                                input.push(field);
                            });
                            $Modal.children.createDialog.addfields(input,"environment");
                        }
                    }
                },
                onHiddenRemove: !0,
                backdrop: "static"
            });
            $Modal.children.createDialog.changedFields = {};
            $("body").append($Modal.children.createDialog.render().el), 
            $Modal.children.createDialog.show();
        }, show_create_deployment : function(element,model){
            var $Modal = element;
            var fields = NewDeploymentFields;
            fields[0].value = model.entityname;
            fields[1].value = model.runtime;
            $Modal.children.createDialog = new CreateModalView({
                title: 'Create Deployment',
                changedFields: {},
                model: {
                    children: fields,
                    cancelhandler: async function (e) {
                        $Modal.children.createDialog.changedFields = {};
                        return true;
                    },
                    savehandler: async function (r, el) {
                        if (r['environment']){
                            var deployment = {
                                algorithm: _.escape(_(r["name"]).t()),
                                environment: _.escape(_(r["environment"]).t()) 
                            }      
                            await rest.createRestEndpoint().postAsync(`deployments`, deployment);
                        }
                        return true;
                    },
                    savedhandler: async function (el, m) {
                        $Modal.children.createDialog.changedFields = {};
                        //m.Components.get("algortihms-search") && m.Components.get("algortihms-search").startSearch();
                        el.hide();
                    },
                    fieldchangehandler: async function (evt) {
                        $('.error-container').hide('fast');
                        $('.info-container').hide('fast');
                        var value = evt.target.value;
                        var fieldname = evt.currentTarget.id;
                        $Modal.children.createDialog.changedFields[fieldname] = value;
                        if ("environment" == fieldname && "runtime" in $Modal.children.createDialog.changedFields) {
                            if (!("init" in $Modal.children.createDialog.changedFields)) 
                            {
                                $Modal.children.createDialog.removefields($('.runtime').find('.textvalue,.pickervalue'));
                                const result = await rest.createRestEndpoint().getAsync(`algorithm_params`, { runtime: encodeURIComponent($Modal.children.createDialog.changedFields['runtime']) });
                                const fieldconfig = await rest.getResponseContents(result);
                                var input = [];
                                _.each(fieldconfig, function (field) {
                                    input.push(field);
                                });
                                $Modal.children.createDialog.addfields(input,"runtime");
                                $Modal.children.createDialog.changedFields['init'] = 1;
                            }
                            $Modal.children.createDialog.removefields($('.environment').find('.textvalue,.pickervalue'));
                            const result = await rest.createRestEndpoint().getAsync(`deployment_params`, {
                                runtime: encodeURIComponent($Modal.children.createDialog.changedFields['runtime']),
                                environment: encodeURIComponent($Modal.children.createDialog.changedFields['environment'])
                            });
                            const fieldconfig = await rest.getResponseContents(result);
                            var input = [];
                            _.each(fieldconfig, function (field) {
                                input.push(field);
                            });
                            $Modal.children.createDialog.addfields(input,"environment");
                        }
                    }
                },
                onHiddenRemove: !0,
                backdrop: "static"
            });
            $Modal.children.createDialog.changedFields = {};
            $Modal.children.createDialog.changedFields['runtime'] = model.runtime;
            $("body").append($Modal.children.createDialog.render().el), 
            $Modal.children.createDialog.show();
        }, 
        show_create_method : function(element,model){
            var $Modal = element;
            var fields = NewMethodFields;
            fields[0].value = model.entityname;
            $Modal.children.createDialog = new CreateModalView({
                title: 'Create Method',
                changedFields: {},
                model: {
                    children: fields,
                    cancelhandler: async function (e) {
                        $Modal.children.createDialog.changedFields = {};
                        return true;
                    },
                    savehandler: async function (r, el) {
                        if (r['entityname']){
                            var data = {
                                algorithm: _.escape(_(r["entityname"]).t()),
                                name: _.escape(_(r["methodname"]).t()) 
                            }      
                            await rest.createRestEndpoint().postAsync(`algorithm_methods`, data);
                        }
                        return true;
                    },
                    savedhandler: async function (el, m) {
                        $Modal.children.createDialog.changedFields = {};
                        //m.Components.get("algortihms-search") && m.Components.get("algortihms-search").startSearch();
                        el.hide();
                    },
                    fieldchangehandler: async function (evt) {
                        $('.error-container').hide('fast');
                        $('.info-container').hide('fast');
                        var value = evt.target.value;
                        var fieldname = evt.currentTarget.id;
                        $Modal.children.createDialog.changedFields[fieldname] = value;
                        if ("environment" == fieldname && "runtime" in $Modal.children.createDialog.changedFields) {
                            if (!("init" in $Modal.children.createDialog.changedFields)) 
                            {
                                $Modal.children.createDialog.removefields($('.runtime').find('.textvalue,.pickervalue'));
                                const result = await rest.createRestEndpoint().getAsync(`algorithm_params`, { runtime: encodeURIComponent($Modal.children.createDialog.changedFields['runtime']) });
                                const fieldconfig = await rest.getResponseContents(result);
                                var input = [];
                                _.each(fieldconfig, function (field) {
                                    input.push(field);
                                });
                                $Modal.children.createDialog.addfields(input,"runtime");
                                $Modal.children.createDialog.changedFields['init'] = 1;
                            }
                            $Modal.children.createDialog.removefields($('.environment').find('.textvalue,.pickervalue'));
                            const result = await rest.createRestEndpoint().getAsync(`deployment_params`, {
                                runtime: encodeURIComponent($Modal.children.createDialog.changedFields['runtime']),
                                environment: encodeURIComponent($Modal.children.createDialog.changedFields['environment'])
                            });
                            const fieldconfig = await rest.getResponseContents(result);
                            var input = [];
                            _.each(fieldconfig, function (field) {
                                input.push(field);
                            });
                            $Modal.children.createDialog.addfields(input,"environment");
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
        delete_algorithm : async function(e,model){
            e.children.deleteDialog = new ModalConfirm({
                model : {
                    title : 'Delete',
                    text : `Do you really want to delete ${model.entityname}?`,
                    button: ModalView.BUTTON_DELETE
                },
                actionhandler : async function(e, modal, m){
                    await rest.createRestEndpoint().delAsync(`algorithms`,{name: model.entityname});
                    //m.Components.get("algortihms-search") && m.Components.get("algortihms-search").startSearch();
                    return true;
                }
            }),
            $("body").append(e.children.deleteDialog.render().el), 
            e.children.deleteDialog.show();
        },
        edit_parameters : async function(element,model){
            var $Modal = element;
            var deployments = {};
            var algorithm_params = [];
            var deployment_params = [];
            var children = [];
            try 
            {
                result = await rest.createRestEndpoint().getAsync(`algorithm_params`, { algorithm: model.entityname, include_deployments:1});
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
                        var _m = {algorithm : model.entityname};
                        for (var subkey in r.algoparams){
                            if (typeof(r.algoparams[subkey])=='function')
                                continue;

                            _m[subkey]=r.algoparams[subkey];
                        }
                        await rest.createRestEndpoint().putAsync(`algorithm_params`, _m);
                        
                        for (var key in r.deploymentparams){
                            if (typeof(r.deploymentparams[key])=='function'){
                                continue;
                            }
                            var _m = {algorithm : model.entityname, environment: key};
                            for (var subkey in  r.deploymentparams[key]){
                                if (typeof(r.deploymentparams[subkey])!='function'){
                                    _m[subkey]=r.deploymentparams[key][subkey];
                                }
                            }
                            await rest.createRestEndpoint().putAsync(`deployment_params`, _m);
                        }
                    },
                    savedhandler: async function (el, m) {
                        $Modal.children.createDialog.changedFields = {};
                        //m.Components.get("algortihms-search") && m.Components.get("algortihms-search").startSearch();
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
        delete_deployment : async function(e,model){
            e.children.deleteDialog = new ModalConfirm({
                model : {
                    title : 'Delete Deployment',
                    text : `Do you really want to delete ${model.entityname}/${model.environment}?`,
                    button: ModalView.BUTTON_DELETE
                },
                actionhandler : async function(e, modal, m){
                    await rest.createRestEndpoint().delAsync(`deployments`, {
                        algorithm : model.entityname,environment: model.environment
                    });
                    //m.Components.get("algortihms-search") && m.Components.get("algortihms-search").startSearch();
                    return true;
                }
            }),
            $("body").append(e.children.deleteDialog.render().el), 
            e.children.deleteDialog.show();
        },
        toggle_status : async function(e,model){
            e.children.status_dialog = new ModalConfirm({
                model : {
                    title : 'Toggle Status',
                    text : `Do you really want to ${model.enabledisable} ${model.entityname}/${model.environment}?`,
                    button: BUTTON_OK
                },
                actionhandler : async function(e, modal, m){
                    await rest.createRestEndpoint().putAsync(`deployments`, {
                        disabled: model.enabledisable == "disable",
                        algorithm : model.entityname,environment: model.environment
                    });
                    //m.Components.get("algortihms-search") && m.Components.get("algortihms-search").startSearch();
                    return true;
                }
            }),
            $('body').append(e.children.status_dialog.render().el), 
            e.children.status_dialog.show();
        },
        restart_deployment : async function(e,model){
            e.children.restart_dialog = new ModalConfirm({
                model : {
                    title : 'Restart Deployment',
                    text : `Do you really want to restart ${model.entityname}/${model.environment} ?`,
                    button: BUTTON_OK
                },
                actionhandler : async function(e, modal, m){
                        await rest.createRestEndpoint().putAsync(`deployments`, {
                            algorithm : model.entityname,
                            environment: model.environment,
                            restart_required: true,
                        });
                        //m.Components.get("algortihms-search") && m.Components.get("algortihms-search").startSearch();
                    return true;
                }
            }),
            $('body').append(e.children.restart_dialog.render().el), 
            e.children.restart_dialog.show();
        },
        delete_method : async function(e,model){
            e.children.deleteDialog = new ModalConfirm({
                model : {
                    title : 'Delete Method',
                    text : `Do you really want to delete ${model.entityname}?`,
                    button: ModalView.BUTTON_DELETE
                },
                actionhandler : async function(e, modal, m){
                    await rest.createRestEndpoint().delAsync(`algorithm_methods`,{algorithm: model.entityname, name: model.method});
                    //m.Components.get("algortihms-search") && m.Components.get("algortihms-search").startSearch();
                    return true;
                }
            }),
            $("body").append(e.children.deleteDialog.render().el), 
            e.children.deleteDialog.show();
        }
    });
});