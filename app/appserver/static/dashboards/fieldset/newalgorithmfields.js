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
            id: "runtime",
            value: "",
            label: "Runtime",
            type: "picker",
            important: true,
            query: "| rest splunk_server=local services/dltk/runtimes",
            querylabel: "name",
            query_value: "name",
            mandatory: true
        },
        {
            id: "environment",
            value: "",
            label: "Environment",
            type: "picker",
            important: true,
            query: "| rest splunk_server=local services/dltk/environments",
            query_label: "name",
            query_value: "name",
            
        }
    ];
});