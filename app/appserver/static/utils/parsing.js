var appName = window.location.pathname.match(/..-..\/app\/(?<app>[^\/]+)/).groups.app;

define([
    'underscore',
], function (_) {
    return function () {
        const capitalize = (s) => {
            if (typeof s !== 'string') return ''
            return s.charAt(0).toUpperCase() + s.slice(1)
        }

        return {
            capitalize: capitalize,
            parseError: function (err) {
                var errorMessage;

                if (err.data && err.data.messages && err.data.messages.length > 0) {
                    errorMessage = err.data.messages.map(m => capitalize(m.text) + ".").join("\n ");
                } else if (err.data) {
                    errorMessage = err.data;
                } else if (err.error) {
                    errorMessage = err.error;
                } else if (err.status) {
                    errorMessage = '' + err.status;
                } else {
                    errorMessage = '' + err;
                }

                return errorMessage;
            },
            normalizeBoolean: function (test, strictMode) {
                if (typeof (test) == 'string') {
                    test = test.toLowerCase();
                }
                switch (test) {
                    case true:
                    case 1:
                    case '1':
                    case 'yes':
                    case 'on':
                    case 'true':
                        return true;
                    case false:
                    case 0:
                    case '0':
                    case 'no':
                    case 'off':
                    case 'false':
                        return false;
                    default:
                        if (strictMode) throw TypeError("Unable to cast value into boolean: " + test);
                        return test;
                }
            },
        };
    }();
});