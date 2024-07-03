from odoo import models, fields, api

from ..Connectors import Sirett

class Producto(models.Model):
    _name = 'eurocomp.producto'
    _description = 'Eurocomp Productos'

    codigo = fields.Char('SKU')
    cod_hacienda = fields.Char('CABYS')
    descripcion = fields.Char('Descripción')
    familia = fields.Char('Familia')
    marca = fields.Char('Marca')
    clase = fields.Char('Clase')
    modelo = fields.Char('Modelo')
    precio = fields.Float('Precio')
    stock = fields.Float('Stock')
    caracteristicas = fields.Text('Características')
    peso = fields.Float('Peso')
    medida = fields.Char('Medida')

    @api.model
    def get_stock_min(self):
        config = self.env['res.config.settings'].sudo().search([], limit=1)
        return config.eurocomp_stock_min if config else 0
