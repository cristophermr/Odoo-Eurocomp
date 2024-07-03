odoo.define('eurocomp.product_tree_decorator', function (require) {
    "use strict";

    var ListView = require('web.ListView');
    var core = require('web.core');
    var QWeb = core.qweb;

    ListView.include({
        render: function () {
            var self = this;
            this._super.apply(this, arguments);

            // Obtener el valor de eurocomp_stock_min desde el servidor
            this._rpc({
                model: 'eurocomp.producto',
                method: 'get_stock_min',
            }).then(function (stock_min) {
                // Aplicar las decoraciones según el valor de stock_min
                self.$el.find('tbody tr').each(function () {
                    var $tr = $(this);
                    var stock = parseFloat($tr.find('td[data-field="stock"]').text());

                    if (stock == 0) {
                        $tr.addClass('o_data_row decoration-danger');
                    } else if (stock >= 1 && stock <= stock_min) {
                        $tr.addClass('o_data_row decoration-warning');
                    } else if (stock > stock_min) {
                        $tr.addClass('o_data_row decoration-success');
                    }
                });
            });
        }
    });
});
