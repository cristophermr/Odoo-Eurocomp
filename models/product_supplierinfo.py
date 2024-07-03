from odoo import fields, models, api

class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    current_stock = fields.Integer(string='Current stock',help="Current stock available in this product")


