var appName = window.location.pathname.match(/..-..\/app\/(?<app>[^\/]+)/).groups.app;

require([
    "jquery",
    "splunkjs/mvc",
    "splunkjs/mvc/textinputview",
    Splunk.util.make_url(`/static/app/${appName}/utils/loading.js`),
    Splunk.util.make_url(`/static/app/${appName}/utils/rest.js`),
    Splunk.util.make_url(`/static/app/${appName}/utils/dialog.js`),
    Splunk.util.make_url(`/static/app/${appName}/utils/parsing.js`),
    Splunk.util.make_url(`/static/app/${appName}/autodiscover.js`),
    'splunkjs/mvc/simplexml/ready!',
], function (
    $,
    mvc,
    TextInputView,
    loading,
    rest,
    Dialog,
    parsing,
    _,
    _,
) {
    const endpoint = rest.createRestEndpoint();
    const tokens = mvc.Components.getInstance("submitted");
    const environment = tokens.attributes.environment;
    const algorithm = tokens.attributes.algorithm;

    const titleElement = $(".dashboard-title.dashboard-header-title");
    titleElement.text(`${titleElement.text()}: ${algorithm} in ${environment}`);

    const backButton = $('<button class="btn action-button">Back</button>');
    backButton.click(async function () {
        window.location.href = `algorithm?name=${algorithm}`;
    });
    $(".dashboard-view-controls").append(backButton);

    const updateConfig = async function (config) {
        const delay = ms => new Promise(res => setTimeout(res, ms));
        const progressIndicator = loading.newLoadingIndicator({
            title: "Updating Deployment...",
            subtitle: "Please wait.",
        });
        try {
            await endpoint.postAsync(`deployment/${algorithm}/${environment}`, config);
            await delay(10000);
        }
        catch (err) {
            Dialog.showErrorDialog(null, err, true).wait();
        }
        finally {
            progressIndicator.hide();
        }
    };

    // status message
    (function () {
        const configSearchManager = mvc.Components.getInstance("deployment_search");
        const configSearchResults = configSearchManager.data('results', {
            output_mode: 'json',
        });
        configSearchResults.on("data", function () {
            const results = configSearchResults.data().results;
            if (!results.length) return;
            const statusMessage = results[0].status_message
            if (statusMessage) {
                statusMessageP.text(statusMessage);
                statusMessageP.show();
            }
            else {
                statusMessageP.hide();
            }
        });
        const statusMessageP = $("#status_message_text");
    })();

    // edit
    (function () {
        const searchManager = mvc.Components.getInstance("deployment_search");
        const searchResults = searchManager.data('results', {
            output_mode: 'json',
        });
        const defaulParamPrefix = "defaultparam.";
        const paramPrefix = "param.";
        const editDialog = $("#edit-dialog");
        const paramsTable = $('.params', editDialog);
        const paramComponents = [];
        $("#edit-button").click(function () {
            const loadingProgressIndicator = loading.newLoadingIndicator({
                title: "Loading ...",
                subtitle: "Please wait.",
            });
            $("tr", paramsTable).slice(1).remove();
            searchResults.on("data", function () {
                loadingProgressIndicator.hide();
                searchResults.off("data");
                const results = searchResults.data().results;
                if (!results.length) return;
                const config = results[0];
                const params = {};
                const defaultParams = {};
                Object.keys(config).forEach(function (k) {
                    if (k.startsWith(paramPrefix)) {
                        const name = k.substr(paramPrefix.length);
                        params[name] = config[k];
                    }
                    if (k.startsWith(defaulParamPrefix)) {
                        const name = k.substr(defaulParamPrefix.length);
                        defaultParams[name] = config[k];
                    }
                });
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
            });
        });
        $('button.apply', editDialog).click(async function () {
            const data = {};
            paramComponents.forEach(function (c) {
                data[c.id] = c.val();
            });
            await updateConfig(data);
        });
    })();

    // restart
    (function () {
        const configSearchManager = mvc.Components.getInstance("deployment_search");
        const configSearchResults = configSearchManager.data('results', {
            output_mode: 'json',
        });
        configSearchResults.on("data", function () {
            const results = configSearchResults.data().results;
            if (!results.length) return;
            const restartRequired = parsing.normalizeBoolean(results[0].restart_required)
            if (restartRequired) {
                restartButton.hide();
            }
            else {
                restartButton.show();
            }
        });
        const restartButton = $("#restart-button").click(async function () {
            await updateConfig({
                "restart_required": true,
            });
        });
    })();

    // enable/disable
    (function () {
        const configSearchManager = mvc.Components.getInstance("deployment_search");
        const configSearchResults = configSearchManager.data('results', {
            output_mode: 'json',
        });
        configSearchResults.on("data", function () {
            const results = configSearchResults.data().results;
            if (!results.length) return;
            const disabled = parsing.normalizeBoolean(results[0].disabled)
            if (disabled) {
                disableButton.hide();
                enableButton.show();
            }
            else {
                enableButton.hide();
                disableButton.show();
            }
        });
        const disableButton = $("#disable-button").click(async function () {
            await updateConfig({
                "disabled": true,
            });
        });
        const enableButton = $("#enable-button").click(async function () {
            await updateConfig({
                "disabled": false,
            });
        });
    })();

    // editing
    (function () {
        const configSearchManager = mvc.Components.getInstance("deployment_search");
        const configSearchResults = configSearchManager.data('results', {
            output_mode: 'json',
        });
        var editor_url;
        configSearchResults.on("data", function () {
            const results = configSearchResults.data().results;
            if (!results.length) return;
            const editable = parsing.normalizeBoolean(results[0].editable);
            const status = results[0].status;
            editor_url = results[0].editor_url;
            if (editable) {
                startEditorButton.hide();
                stopEditorButton.show();
                if (status == "deployed") {
                    openEditorButton.show();
                }
                else {
                    openEditorButton.hide();
                }
            }
            else {
                startEditorButton.show();
                stopEditorButton.hide();
                openEditorButton.hide();
            }
        });
        const startEditorButton = $("#start-editor-button").click(async function () {
            await updateConfig({
                "editable": true,
            });
        });
        const stopEditorButton = $("#stop-editor-button").click(async function () {
            await updateConfig({
                "editable": false,
            });
        });
        const openEditorButton = $("#open-editor-button").click(function () {
            if (editor_url) {
                var win = window.open(editor_url, '_blank');
                win.focus();
            } else {
                alert("Editor URL missing.");
            }
        });
    })();

    // delete
    (function () {
        const delay = ms => new Promise(res => setTimeout(res, ms));
        const deleteButton = $('<button class="btn btn-primary btn-warn action-button">Undeploy</button>');
        deleteButton.click(async function () {
            const progressIndicator = loading.newLoadingIndicator({
                title: "Deleting Deployment...",
                subtitle: "Please wait.",
            });
            try {
                await endpoint.delAsync(`deployment/${algorithm}/${environment}`);
                await delay(3000);
                window.location.href = `algorithm?name=${algorithm}`;
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

    // create model
    (function () {
        const createModelDialog = $("#create-model-dialog");
        $("#open-create-model-dialog-button").click(function () {
            Dialog.show(createModelDialog);
        });
        $('button.create', createModelDialog).click(async function () {
            const progressIndicator = loading.newLoadingIndicator({
                title: "Creating Model...",
                subtitle: "Please wait.",
            });
            try {
                const modelName = mvc.Components.getInstance("model_name").val();
                await endpoint.postAsync("models", {
                    environment: environment,
                    algorithm: algorithm,
                    name: modelName,
                });
                progressIndicator.hide();
            }
            catch (err) {
                progressIndicator.hide();
                await Dialog.showErrorDialog(null, err, true).wait();
            }
        });
    })();

});
