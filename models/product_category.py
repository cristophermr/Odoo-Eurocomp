import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    _inherit = 'product.category'
    sku_slug = fields.Char(string='SKU Slug',help='This is a abbrev code for add sku to all imported products')

    @api.model
    def action_generate_sku(self):
        return False