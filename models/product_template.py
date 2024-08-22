import logging
from odoo import models, fields, api
from ..classes.ImageBuilder import ImageBuilder

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    euro_item_code = fields.Char(string='Euro Item Code', readonly=True, required=False)
    def write(self, vals):
        if vals.get('image_1920'):
            image_path = vals['image_1920']
            if isinstance(image_path, bytes):
                # Decodifica los bytes a una cadena
                image_path = image_path.decode('utf-8')

            builder = ImageBuilder()
            processed_image = builder.compute_image_1920(image_path)
            vals['image_1920'] = processed_image
        return super(ProductTemplate, self).write(vals)