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
            readonly: true
        },
        {
            id: "runtime",
            value: "",
            label: "Runtime",
            type: "picker",
            important: true,
            query: "| rest splunk_server=local services/dltk/runtimes",
            querylabel: "name",
            query_value: "name",
            readonly: true
        }
    ];
});