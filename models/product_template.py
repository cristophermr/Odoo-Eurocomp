import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    euro_item_code = fields.Char(string='Euro Item Code',readonly=True)