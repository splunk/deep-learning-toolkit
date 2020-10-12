var appName = window.location.pathname.match(/..-..\/app\/(?<app>[^\/]+)/).groups.app;

require([
    "jquery",
    "splunkjs/mvc",
    "splunkjs/mvc/textinputview",
    'splunkjs/mvc/tableview',
    Splunk.util.make_url(`/static/app/${appName}/autodiscover.js`),
    Splunk.util.make_url(`/static/app/${appName}/utils/loading.js`),
    Splunk.util.make_url(`/static/app/${appName}/utils/rest.js`),
    Splunk.util.make_url(`/static/app/${appName}/utils/dialog.js`),
    Splunk.util.make_url(`/static/app/${appName}/utils/parsing.js`),
    'splunkjs/mvc/simplexml/ready!',
], function (
    $,
    mvc,
    TextInputView,
    TableView,
    _,
    loading,
    rest,
    Dialog,
    parsing,
    _,
) {
    const endpoint = rest.createRestEndpoint();
    const tokens = mvc.Components.getInstance("submitted");
    const algorithmName = tokens.attributes.name;

    const titleElement = $(".dashboard-title.dashboard-header-title");
    titleElement.text(`${titleElement.text()}: ${algorithmName}`);

    const backButton = $('<button class="btn action-button">Back</button>');
    backButton.click(async function () {
        window.location.href = 'algorithms';
    });
    $(".dashboard-view-controls").append(backButton);

    // open editor
    (function () {
        const deleteButton = $('<button class="btn btn-primary action-button">Open Editor</button>');
        var editableDeployment;
        deleteButton.click(function () {
            var w = window.open(editableDeployment.editor_url, '_blank');
            w.focus();
        });
        const searchManager = mvc.Components.get("deployments_search");
        const searchResults = searchManager.data('results', {
            output_mode: 'json',
        });
        searchResults.on("data", function () {
            if (!searchResults.hasData()) {
                return;
            }
            const deployments = searchResults.data().results;
            editableDeployment = deployments.find(d =>
                parsing.normalizeBoolean(d.editable) &&
                d.status == "deployed"
            );
            if (editableDeployment) {
                deleteButton.show();
            }
            else {
                deleteButton.hide();
            }
        })
        deleteButton.hide();
        $(".dashboard-view-controls").append(deleteButton);
    })();

    // delete
    (function () {
        const deleteButton = $('<button class="btn btn-primary btn-warn action-button">Delete</button>');
        deleteButton.click(async function () {
            const progressIndicator = loading.newLoadingIndicator({
                title: "Deleting Algorithm...",
                subtitle: "Please wait.",
            });
            try {
                await endpoint.delAsync(`algorithm/${algorithmName}`);
                window.location.href = `algorithms`;
            }
            catch (err) {
                Dialog.showErrorDialog(null, err, true).wait();
            }
            finally {
                progressIndicator.hide();
            }
        });
        $(".dashboard-view-controls").append(deleteButton);
    })();

    // add/remove/edit methods
    (function () {
        const searchManager = mvc.Components.getInstance("algorithm_search");
        const editMethodDialog = $("#edit-method-dialog");
        var MethodActionsCellRenderer = TableView.BaseCellRenderer.extend({
            canRender: function (cell) {
                return cell.field == "actions";
            },
            render: function ($td, cell) {
                const method = cell.value.split("|")[0];
                const commandType = cell.value.split("|")[1];
                const removeButton = $(`<a class="action-link" href="#">Remove</a>`).click(async function () {
                    const progressIndicator = loading.newLoadingIndicator({
                        title: "Removing Method ...",
                        subtitle: "Please wait.",
                    });
                    try {
                        const data = {};
                        data[`method.${method}.delete`] = '1';
                        await endpoint.postAsync(`algorithm/${algorithmName}`, data);
                        searchManager.startSearch();
                        progressIndicator.hide();
                    }
                    catch (err) {
                        progressIndicator.hide();
                        await Dialog.showErrorDialog(null, err, true).wait();
                    }
                });
                $td.append(removeButton);
                const editButton = $(`<a class="action-link">Edit</a>`).click(function () {
                    const commandTypeField = mvc.Components.getInstance("edit-method-command-type");
                    commandTypeField.val(commandType);
                    editMethodDialog.attr("data-method", method);
                    Dialog.show(editMethodDialog);
                });
                $td.append(editButton);
            }
        });
        mvc.Components.get('methods_table').getVisualization(function (tableView) {
            tableView.table.addCellRenderer(new MethodActionsCellRenderer());
        });
        $('button.edit', editMethodDialog).click(async function () {
            const method = editMethodDialog.attr("data-method");
            const commandTypeField = mvc.Components.getInstance("edit-method-command-type");
            const progressIndicator = loading.newLoadingIndicator({
                title: "Updating Method ...",
                subtitle: "Please wait.",
            });
            try {
                const data = {};
                data[`method.${method}.command_type`] = commandTypeField.val();
                await endpoint.postAsync(`algorithm/${algorithmName}`, data);
                searchManager.startSearch();
                progressIndicator.hide();
            }
            catch (err) {
                progressIndicator.hide();
                await Dialog.showErrorDialog(null, err, true).wait();
            }
        });
        const addMethodDialog = $("#add-method-dialog");
        var methodNameField;
        var commandTypeField;
        $("#add-method-button").click(function () {
            Dialog.show(addMethodDialog);
            methodNameField = mvc.Components.getInstance("add-method-name");
            commandTypeField = mvc.Components.getInstance("add-method-command-type");
            setTimeout(function () {
                $("input[type=\"text\"]", methodNameField.$el).focus();
            }, 300);
        });
        $('button.add', addMethodDialog).click(async function () {
            const progressIndicator = loading.newLoadingIndicator({
                title: "Adding Method ...",
                subtitle: "Please wait.",
            });
            try {
                const data = {};
                data[`method.${methodNameField.val()}.command_type`] = commandTypeField.val();
                await endpoint.postAsync(`algorithm/${algorithmName}`, data);
                searchManager.startSearch();
                progressIndicator.hide();
            }
            catch (err) {
                progressIndicator.hide();
                await Dialog.showErrorDialog(null, err, true).wait();
            }
        });
    })();

    // create deployment
    (function () {
        const deployDialog = $("#deploy-dialog");
        $("#deploy-button").click(function () {
            Dialog.show(deployDialog);
        });
        $('button.create', deployDialog).click(async function () {
            const progressIndicator = loading.newLoadingIndicator({
                title: "Deploying Algorithm...",
                subtitle: "Please wait.",
            });
            try {
                const searchManager = mvc.Components.get("deployments_search");
                const searchResults = searchManager.data('results', {
                    output_mode: 'json',
                });
                const environmentName = mvc.Components.getInstance("environment").val();
                await endpoint.postAsync(`deployments`, {
                    algorithm: algorithmName,
                    environment: environmentName,
                });
                const waitForDeployment = new Promise(function (resolve/*, reject*/) {
                    const done = function (msg) {
                        console.log(msg)
                        searchResults.off("data");
                        resolve();
                    }
                    searchResults.on("data", function () {
                        if (!searchResults.hasData()) {
                            return;
                        }
                        const deployments = searchResults.data().results;
                        console.log(deployments);
                        const deployment = deployments.find(d => d.environment == environmentName);
                        if (deployment) {
                            done("found deployment");
                            return;
                        }
                    })
                });
                await waitForDeployment;
                progressIndicator.hide();
            }
            catch (err) {
                progressIndicator.hide();
                await Dialog.showErrorDialog(null, err, true).wait();
            }
        });
    })();

    // delete deployment
    const deleteDeployment = async function (environment) {
        const progressIndicator = loading.newLoadingIndicator({
            title: "Deleting Deployment...",
            subtitle: "Please wait.",
        });
        try {
            console.log(`deleting ${environment} ...`);
            await endpoint.delAsync(`deployment/${algorithmName}/${environment}`);
            const waitForDeployment = new Promise(function (resolve/*, reject*/) {
                const searchManager = mvc.Components.getInstance("deployments_search");
                const searchResults = searchManager.data('results', {
                    output_mode: 'json',
                });
                const done = function (msg) {
                    console.log(msg)
                    searchResults.off("data");
                    resolve();
                }
                searchResults.on("data", function () {
                    if (!searchResults.hasData()) {
                        return;
                    }
                    const deployments = searchResults.data().results;
                    const deployment = deployments.find(d => d.environment == environment);
                    if (!deployment) {
                        done("deployment gone");
                        return;
                    }
                    if (deployment.status == "undeploying") {
                        done("deployment is status 'undeploying'");
                        return;
                    }
                    console.log(deployment);
                })
            });
            await waitForDeployment;
            progressIndicator.hide();
        }
        catch (err) {
            progressIndicator.hide();
            await Dialog.showErrorDialog(null, err, true).wait();
        }
    };

    // restart deployment
    const restartDeployment = async function (environment) {
        const progressIndicator = loading.newLoadingIndicator({
            title: "Restarting Deployment...",
            subtitle: "Please wait.",
        });
        try {
            console.log(`restarting ${environment} ...`);
            await endpoint.postAsync(`deployment/${algorithmName}/${environment}`, {
                "restart_required": true,
            });
            const waitForDeployment = new Promise(function (resolve, reject) {
                const searchManager = mvc.Components.getInstance("deployments_search");
                const searchResults = searchManager.data('results', {
                    output_mode: 'json',
                });
                const done = function (msg) {
                    console.log(msg)
                    searchResults.off("data");
                    resolve();
                }
                const fail = function (msg) {
                    searchResults.off("data");
                    reject(msg);
                }
                searchResults.on("data", function () {
                    if (!searchResults.hasData()) {
                        return;
                    }
                    const deployments = searchResults.data().results;
                    const deployment = deployments.find(d => d.environment == environment);
                    if (!deployment) {
                        fail("deployment gone");
                        return;
                    }
                    const restart_required = parsing.normalizeBoolean(deployment.restart_required);
                    if (restart_required) {
                        console.log("still marked as restart required");
                        return;
                    }
                    done("Not marked as restart required anymore");
                })
            });
            await waitForDeployment;
            progressIndicator.hide();
        }
        catch (err) {
            progressIndicator.hide();
            await Dialog.showErrorDialog(null, err, true).wait();
        }
    };

    // disable deployment
    const disableDeployment = async function (environment) {
        const progressIndicator = loading.newLoadingIndicator({
            title: "Disabling Deployment...",
            subtitle: "Please wait.",
        });
        try {
            console.log(`disabling ${environment} ...`);
            await endpoint.postAsync(`deployment/${algorithmName}/${environment}`, {
                "disabled": true,
            });
            const waitForDeployment = new Promise(function (resolve, reject) {
                const searchManager = mvc.Components.getInstance("deployments_search");
                const searchResults = searchManager.data('results', {
                    output_mode: 'json',
                });
                const done = function (msg) {
                    console.log(msg)
                    searchResults.off("data");
                    resolve();
                }
                const fail = function (msg) {
                    searchResults.off("data");
                    reject(msg);
                }
                searchResults.on("data", function () {
                    if (!searchResults.hasData()) {
                        return;
                    }
                    const deployments = searchResults.data().results;
                    const deployment = deployments.find(d => d.environment == environment);
                    if (!deployment) {
                        fail("deployment gone");
                        return;
                    }
                    const disabled = parsing.normalizeBoolean(deployment.disabled);
                    if (!disabled) {
                        console.log("still not marked as disabled");
                        return;
                    }
                    if (deployment.status == "disabled") {
                        done("deployment is status 'disabled'");
                        return;
                    }
                    if (deployment.status == "disabling") {
                        done("deployment is status 'disabling'");
                        return;
                    }
                    console.log(`status is still ${deployment.status} ...`);
                })
            });
            await waitForDeployment;
            progressIndicator.hide();
        }
        catch (err) {
            progressIndicator.hide();
            await Dialog.showErrorDialog(null, err, true).wait();
        }
    };

    // enable deployment
    const enableDeployment = async function (environment) {
        const progressIndicator = loading.newLoadingIndicator({
            title: "Enabling Deployment...",
            subtitle: "Please wait.",
        });
        try {
            console.log(`enabling ${environment} ...`);
            await endpoint.postAsync(`deployment/${algorithmName}/${environment}`, {
                "disabled": false,
            });
            const waitForDeployment = new Promise(function (resolve, reject) {
                const searchManager = mvc.Components.getInstance("deployments_search");
                const searchResults = searchManager.data('results', {
                    output_mode: 'json',
                });
                const done = function (msg) {
                    console.log(msg)
                    searchResults.off("data");
                    resolve();
                }
                const fail = function (msg) {
                    searchResults.off("data");
                    reject(msg);
                }
                searchResults.on("data", function () {
                    if (!searchResults.hasData()) {
                        return;
                    }
                    const deployments = searchResults.data().results;
                    const deployment = deployments.find(d => d.environment == environment);
                    if (!deployment) {
                        fail("deployment gone");
                        return;
                    }
                    const disabled = parsing.normalizeBoolean(deployment.disabled);
                    if (disabled) {
                        console.log("still not marked as enabled");
                        return;
                    }
                    if (deployment.status == "deploying") {
                        done("deployment is enabled and status 'deploying'");
                        return;
                    }
                    if (deployment.status == "deployed") {
                        done("deployment is enabled and status 'deployed'");
                        return;
                    }
                    if (deployment.status == "error") {
                        fail(deployment.status_message);
                        return;
                    }
                    console.log(`status is still ${deployment.status} ...`);
                })
            });
            await waitForDeployment;
            progressIndicator.hide();
        }
        catch (err) {
            progressIndicator.hide();
            await Dialog.showErrorDialog(null, err, true).wait();
        }
    };

    // deployment actions
    (function () {
        var CellRenderer = TableView.BaseCellRenderer.extend({
            canRender: function (cell) {
                return cell.field == "actions";
            },
            render: function ($td, cell) {
                const data = cell.value.split("|");
                const environment = data[0];
                const editable = parsing.normalizeBoolean(data[1]);
                //const disabled = parsing.normalizeBoolean(data[2]);
                const status = data[3];
                const editorURL = data[4];
                // STATUS_DEPLOYING = "deploying"
                // STATUS_DEPLOYED = "deployed"
                // STATUS_UNDEPLOYING = "undeploying"
                // STATUS_DISABLING = "disabling"
                // STATUS_DISABLED = "disabled"
                // STATUS_ERROR = "error"
                if (editable && status == "deployed" && editorURL) {
                    $td.append($(`<a class="action-link">Editor</a>`).click(function () {
                        var w = window.open(editorURL, '_blank');
                        w.focus();
                    }));
                }
                /*$td.append($(`<a class="action-link">Start Editor</a>`).click(function () {
                }));
                $td.append($(`<a class="action-link">Stop Editor</a>`).click(function () {
                }));*/
                if (status != "undeploying") {
                    $td.append($(`<a class="action-link">Delete</a>`).click(function () {
                        deleteDeployment(environment);
                    }));
                }
                $td.append($(`<a class="action-link">Restart</a>`).click(function () {
                    restartDeployment(environment);
                }));
            }
        });
        mvc.Components.get('deployments_table').getVisualization(function (tableView) {
            tableView.table.addCellRenderer(new CellRenderer());
        });
    })();

    // deployment status
    (function () {
        var CellRenderer = TableView.BaseCellRenderer.extend({
            canRender: function (cell) {
                return cell.field == "status";
            },
            render: function ($td, cell) {
                const components = cell.value.split("|");
                const environment = components[0];
                const status = components[1];
                const statusMessage = components[2];
                const disabled = parsing.normalizeBoolean(components[3]);
                const lineOne = $(`<p></p>`);
                const label = $(`<a class="action-link"></a>`);
                label.text(status).click(function () {
                    window.location.href = `deployment?algorithm=${algorithmName}&environment=${environment}`;
                });
                lineOne.append(label);
                if (!disabled) {
                    lineOne.append($(`<button class="btn btn-small">Disable</button>`).click(function () {
                        disableDeployment(environment);
                    }));
                } else {
                    lineOne.append($(`<button class="btn btn-small">Enable</button>`).click(function () {
                        enableDeployment(environment);
                    }));
                }
                $td.append(lineOne);
                if (statusMessage && statusMessage.length > 0) {
                    const lineTwo = $(`<p></p>`).css({
                        //"border-style": "dashed",
                        //"border-radius": "0.4em",
                        //"border-width": "initial",
                        //"border-color": status == "error" ? "#f007" : "#0007",
                        //"padding": "0.4em"
                        //"font-style": "italic",
                    });
                    lineTwo.text("(" + statusMessage + ")");
                    $td.append(lineTwo);
                }
            }
        });
        mvc.Components.get('deployments_table').getVisualization(function (tableView) {
            tableView.table.addCellRenderer(new CellRenderer());
        });
    })();

    // deployment parameters
    (function () {
        const editDialog = $("#edit-deployment-parameters-dialog");
        const paramsTable = $('.params', editDialog);
        const paramComponents = [];
        var environmentName;
        var CellRenderer = TableView.BaseCellRenderer.extend({
            canRender: function (cell) {
                return cell.field == "parameters";
            },
            render: function ($td, cell) {
                var parameters;
                if (Array.isArray(cell.value)) {
                    environmentName = cell.value.shift();
                    parameters = cell.value;
                } else {
                    parameters = []
                }
                if (parameters.length == 0) {
                    $td.text("No parameters available.");
                    return;
                }
                const table = $(`<table></table>`).css({
                    //"margin-bottom": "1em",
                    "float": "left",
                });
                parameters.forEach(function (param) {
                    const components = param.split("=");
                    const name = components[0];
                    const value = components[1];
                    const row = $(`<tr></tr>`)
                    row.append($(`<td></td>`).text(name));
                    row.append($(`<td></td>`).text(value));
                    table.append(row);
                });
                $td.append(table);
                const editButton = $(`<button class="btn btn-small">Edit</button>`).css({
                    "margin-left": "1em",
                });
                editButton.click(async function () {
                    const progressIndicator = loading.newLoadingIndicator({
                        title: "Loading ...",
                        subtitle: "Please wait.",
                    });
                    try {
                        const result = await endpoint.getAsync(`deployment/${algorithmName}/${environmentName}/`);
                        const deploymentConfig = await rest.getResponseContent(result);
                        const params = {};
                        const defaultParams = {};
                        Object.keys(deploymentConfig).forEach(function (k) {
                            if (k.startsWith("param.")) {
                                const name = k.substr("param.".length);
                                params[name] = deploymentConfig[k];
                            }
                            if (k.startsWith("defaultparam.")) {
                                const name = k.substr("defaultparam.".length);
                                defaultParams[name] = deploymentConfig[k];
                            }
                        });
                        progressIndicator.hide();

                        $("tr", paramsTable).slice(1).remove();
                        Object.keys(params).forEach(function (name) {
                            const row = $("<tr></tr>");
                            row.append($(`<td>${name}</td>`));
                            const valueCell = $(`<td></td>`);
                            var paramTextInputView = new TextInputView({
                                id: "param." + name,
                                value: params[name],
                                el: valueCell,
                            });
                            paramTextInputView.on("change", function () {
                                updateRevertButtonVisibility();
                            });
                            paramComponents.push(paramTextInputView);
                            paramTextInputView.render();
                            row.append(valueCell);
                            const revertButton = $(`<button class="btn">Revert</button>`).click(function () {
                                paramTextInputView.val(defaultParams[name]);
                            });
                            const updateRevertButtonVisibility = function () {
                                const defaultVal = defaultParams[name];
                                const currentVal = paramTextInputView.val();
                                if (currentVal == defaultVal) {
                                    revertButton.css("visibility", "hidden");
                                } else {
                                    revertButton.css("visibility", "");
                                }
                            };
                            updateRevertButtonVisibility();
                            row.append($("<td></td>").append(revertButton));
                            paramsTable.append(row);
                        });
                        Dialog.show(editDialog, {
                            close() {
                                paramComponents.forEach(function (c) {
                                    c.remove();
                                });
                            }
                        });
                    }
                    catch (err) {
                        progressIndicator.hide();
                        await Dialog.showErrorDialog(null, err, true).wait();
                    }
                });
                $td.append(editButton);
            }
        });
        mvc.Components.get('deployments_table').getVisualization(function (tableView) {
            tableView.table.addCellRenderer(new CellRenderer());
        });
        $('button.apply', editDialog).click(async function () {
            const progressIndicator = loading.newLoadingIndicator({
                title: "Updating Deployment Parameters...",
                subtitle: "Please wait.",
            });
            try {
                const data = {};
                paramComponents.forEach(function (c) {
                    data[c.id] = c.val();
                });
                await endpoint.postAsync(`deployment/${algorithmName}/${environmentName}`, data);
                const searchManager = mvc.Components.getInstance("deployments_search");
                searchManager.startSearch();
                progressIndicator.hide();
            }
            catch (err) {
                progressIndicator.hide();
                await Dialog.showErrorDialog(null, err, true).wait();
            }
        });
    })();

    // edit algo parameters
    (function () {
        const searchManager = mvc.Components.getInstance("algorithm_search");
        const editDialog = $("#edit-params-dialog");
        const paramsTable = $('.params', editDialog);
        const paramComponents = [];
        $("#edit-params-button").click(async function () {
            const progressIndicator = loading.newLoadingIndicator({
                title: "Loading ...",
                subtitle: "Please wait.",
            });
            try {
                const result = await endpoint.getAsync(`algorithm/${algorithmName}`);
                const algorithmConfig = await rest.getResponseContent(result);
                const params = {};
                const defaultParams = {};
                Object.keys(algorithmConfig).forEach(function (k) {
                    if (k.startsWith("param.")) {
                        const name = k.substr("param.".length);
                        params[name] = algorithmConfig[k];
                    }
                    if (k.startsWith("defaultparam.")) {
                        const name = k.substr("defaultparam.".length);
                        defaultParams[name] = algorithmConfig[k];
                    }
                });
                progressIndicator.hide();

                $("tr", paramsTable).slice(1).remove();
                Object.keys(params).forEach(function (name) {
                    const row = $("<tr></tr>");
                    row.append($(`<td>${name}</td>`));
                    const valueCell = $(`<td></td>`);
                    var paramTextInputView = new TextInputView({
                        id: "param." + name,
                        value: params[name],
                        el: valueCell,
                    });
                    paramTextInputView.on("change", function () {
                        updateRevertButtonVisibility();
                    });
                    paramComponents.push(paramTextInputView);
                    paramTextInputView.render();
                    row.append(valueCell);
                    const revertButton = $(`<button class="btn">Revert</button>`).click(function () {
                        paramTextInputView.val(defaultParams[name]);
                    });
                    const updateRevertButtonVisibility = function () {
                        const defaultVal = defaultParams[name];
                        const currentVal = paramTextInputView.val();
                        if (currentVal == defaultVal) {
                            revertButton.css("visibility", "hidden");
                        } else {
                            revertButton.css("visibility", "");
                        }
                    };
                    updateRevertButtonVisibility();
                    row.append($("<td></td>").append(revertButton));
                    paramsTable.append(row);
                });
                Dialog.show(editDialog, {
                    close() {
                        paramComponents.forEach(function (c) {
                            c.remove();
                        });
                    }
                });
            }
            catch (err) {
                progressIndicator.hide();
                await Dialog.showErrorDialog(null, err, true).wait();
            }
        });
        $('button.apply', editDialog).click(async function () {
            const progressIndicator = loading.newLoadingIndicator({
                title: "Updating Algorithm...",
                subtitle: "Please wait.",
            });
            try {
                const data = {};
                paramComponents.forEach(function (c) {
                    data[c.id] = c.val();
                });
                await endpoint.postAsync(`algorithm/${algorithmName}`, data);
                searchManager.startSearch();
                progressIndicator.hide();
            }
            catch (err) {
                progressIndicator.hide();
                await Dialog.showErrorDialog(null, err, true).wait();
            }
        });
    })();
});
