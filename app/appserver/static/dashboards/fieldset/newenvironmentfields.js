define([
    "underscore"
], function (_) {
    return [
        {
            id: "name",
            value: "",
            default: "Enter Name here...",
            label: "Name",
            type: "text",
            mandatory: true,
            important: true
        },
        {
            id: "connector",
            value: "",
            label: "Connector",
            type: "picker",
            important: true,
            query: "| rest splunk_server=local services/dltk/connectors",
            querylabel: "name",
            query_value: "name",
            mandatory: true
        }
    ];
});