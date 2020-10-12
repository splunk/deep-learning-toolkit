define([
    "underscore"
], function (_) {
    return [
        {
            id: "entityname",
            value: "",
            default: "Enter Name here...",
            label: "Algorithm",
            type: "text",
            important: true,
            readonly: true
        },
        {
            id: "methodname",
            value: "",
            default: "Enter Name here...",
            label: "Name",
            type: "text",
            important: true,
            mandatory: true,
            readonly: false
        }
    ];
});