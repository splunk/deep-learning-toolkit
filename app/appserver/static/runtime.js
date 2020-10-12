var appName = window.location.pathname.match(/..-..\/app\/(?<app>[^\/]+)/).groups.app;

require([
    "jquery",
    "splunkjs/mvc",
    Splunk.util.make_url(`/static/app/${appName}/utils/loading.js`),
    Splunk.util.make_url(`/static/app/${appName}/utils/rest.js`),
    Splunk.util.make_url(`/static/app/${appName}/utils/dialog.js`),
    'splunkjs/mvc/simplexml/ready!',
], function (
    $,
    mvc,
    loading,
    rest,
    Dialog,
    _,
) {
    const endpoint = rest.createRestEndpoint();
    const tokens = mvc.Components.getInstance("submitted");
    const runtimeName = tokens.attributes.name;

    const titleElement = $(".dashboard-title.dashboard-header-title");
    titleElement.text(`${titleElement.text()}: ${runtimeName}`);

    const backButton = $('<button class="btn action-button">Back</button>');
    backButton.click(async function () {
        window.location.href = 'runtimes';
    });
    $(".dashboard-view-controls").append(backButton);
});
