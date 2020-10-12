
define([
    'underscore',
], function (_, Modal) {
    var appName = window.location.pathname.match(/..-..\/app\/(?<app>[^\/]+)/).groups.app;
    //!TODO get rid of this
    var splunkurl_prefix = window.location.pathname.substr(0, window.location.pathname.search(/\/[a-z][a-z]-[A-Z][A-Z]\//i));
    var WebHTTPHandler = splunkjs.ProxyHttp.extend({
        init: function () {
            this._super(`${splunkurl_prefix}/en-US/splunkd/__raw`);
        }
    });
    var EndpointWithPUT = splunkjs.Service.Endpoint.extend({
        put: function (relpath, params, callback) {
            var url = this.qualifiedPath;

            // If we have a relative path, we will append it with a preceding
            // slash.
            if (relpath) {
                url = url + "/" + relpath;
            }

            return this.service.request(
                url,//path,
                "PUT", //method, 
                undefined, //query, 
                params, //post, 
                undefined, //body, 
                undefined, //headers, 
                callback //callback
            );
        },
    });
    return function () {
        return {
            createRestEndpoint: function () {
                const http = new WebHTTPHandler();
                const service = new splunkjs.Service(http, {
                    owner: "nobody",
                    app: appName,
                    sharing: "app",
                });
                var $body = $('body');
                if ($body.endpoint) {
                    return $body.endpoint;
                }
                var endpoint = new EndpointWithPUT(service, "dltk");
                endpoint.getAsync = function (path, options) {
                    return new Promise((resolve, reject) => {
                        this.get(path, options, function (err, response) {
                            if (err) {
                                reject(err);
                                return;
                            }
                            resolve(response);
                        });
                    });
                };
                endpoint.putAsync = function (path, options) {
                    return new Promise((resolve, reject) => {
                        this.put(path, options, function (err, response) {
                            if (err) {
                                reject(err);
                                return;
                            }
                            resolve(response);
                        });
                    });
                };
                endpoint.postAsync = function (path, options) {
                    return new Promise((resolve, reject) => {
                        this.post(path, options, function (err, response) {
                            if (err) {
                                reject(err);
                                return;
                            }
                            resolve(response);
                        });
                    });
                };
                endpoint.delAsync = function (path, options) {
                    return new Promise((resolve, reject) => {
                        this.del(path, options, function (err, response) {
                            if (err) {
                                reject(err);
                                return;
                            }
                            resolve(response);
                        });
                    });
                };
                $body.endpoint = endpoint;
                return endpoint;
            },
            to: function (promise) {
                return promise.then(function (result) {
                    return [result, undefined];
                }).catch(function (err) {
                    return [undefined, err];
                });
            },
            getResponseContents: function (response) {
                return new Promise((resolve, reject) => {
                    if (!response.data) {
                        reject("Unexpected response format (missing 'data')")
                        return;
                    }
                    if (!response.data.entry) {
                        reject("Unexpected response format (missing 'data.entry')")
                        return;
                    }
                    const contents = response.data.entry.map(function (e) {
                        return e.content;
                    });
                    resolve(contents);
                });
            },
            getResponseContent: async function (response) {
                const contents = await this.getResponseContents(response);
                const content = await new Promise((resolve, reject) => {
                    if (contents.length == 0) {
                        reject("response has no content")
                        return;
                    }
                    if (contents.length > 1) {
                        reject("response multiple contents")
                        return;
                    }
                    resolve(contents[0]);
                });
                return content;
            },
        };
    }();
});