define([
    "underscore"
], function (_) {
    return [
        {
            id: "description",
            value: "",
            default: "Enter Description here...",
            label: "Description",
            type: "text",
            mandatory: false,
            important: true
        },
        {
            id: "category",
            value: "",
            default: "Enter Category here...",
            label: "Category",
            type: "text",
            mandatory: false,
            important: true
        }
    ];
});