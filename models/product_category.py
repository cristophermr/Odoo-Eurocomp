import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ProductCategory(models.Model):
    _inherit = 'product.category'

    sku_slug = fields.Char(string='SKU Slug', help='This is an abbreviation code for adding SKU to all imported products')

    def action_generate_sku(self):
        products = self.env['product.template'].search([('categ_id', '=', self.id), ('default_code', '=', False)])
        for product in products:
            sku = self._generate_sku()
            product.write({'default_code': sku})
        return self._show_notification('Se asigno el SKU a los productos en la categoría seleccionada','success')

    def _generate_sku(self):
        consecutive = self._get_consecutive()
        sku = f"{self.sku_slug}-{str(consecutive).zfill(5)}"
        return sku

    def _get_consecutive(self):
        next_id = 1
        products = self.env['product.template'].sudo().search([('default_code', 'like', f"{self.sku_slug}%")])
        if products:
            try:
                last_product = products.sorted(key=lambda r: int(r.default_code.split('-')[1]), reverse=True)[0]
                last_sku_parts = last_product.default_code.split('-')
                next_id = int(last_sku_parts[1]) + 1
            except Exception as e:
                _logger.exception("Error al obtener el consecutivo del SKU: %s", e)
        return next_id


    def _show_notification(self, message, type):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Notificación',
                'message': message,
                'type': type,  # types: success, warning, danger, info
                'next': {
                    'type': 'ir.actions.act_window_close',
                },
            }
        }