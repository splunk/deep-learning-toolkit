define(
    [
        'jquery',
        'underscore',
        'models/Base'
    ],
    function(
        $,
        _,
        BaseModel
    ){
        return BaseModel.extend({
            defaults: {
                tab: 'tab0'
            }
        });
    }
);
