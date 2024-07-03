from odoo import api,fields,models

class AddProductsInventory(models.TransientModel):
    name = "Add.Products.Inventory"
    description = "Agregar productos Eurocomp a Inventario"
    product_id = fields.Many2one('eurocomp.producto','Producto Eurocomp', required=True)
