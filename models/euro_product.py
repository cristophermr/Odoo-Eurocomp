import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


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
    added = fields.Boolean('Added', default=False)

    @api.model
    def get_stock_min(self):
        config = self.env['res.config.settings'].sudo().search([], limit=1)
        return config.eurocomp_stock_min if config else 0

    def action_import_products(self):
        partner_id = self._CheckPartner()
        for product in self:
            try:
                category_id = self._CheckCategory(product.familia)
                product_id = self._CheckProduct(product, category_id)
                self._CheckSupplierInfo(partner_id, product_id, product)

            except Exception as e:
                _logger.error(e)
                return self._show_notification("Error al importar el producto: {}".format(e),'danger')

        return self._show_notification("Productos importados exitosamente",'success')
    def _CheckPartner(self):
        Objpartner = self.env['res.partner']
        # Verificar y crear el proveedor si no existe
        partner = Objpartner.search([('vat', '=', '3101294674')], limit=1)
        if not partner:
            partner_val = {
                'is_company': True,
                'identification_id': 2,
                'vat': '3101294674',
                'name': 'EUROCOMP DE COSTA RICA SOCIEDAD ANONIMA',
                'website': 'https://eurocompcr.com/',
                'phone': '+506 2238 0280',
                'email': 'ventas@eurocompcr.com'}
            partner = Objpartner.create(partner_val)
            _logger.info('Se agregó el proveedor con la data:  %s', partner)
        return partner.id

    def _CheckCategory(self, category_name):
        ObjCategory = self.env['product.category']
        category = ObjCategory.search([('name', '=', category_name)], limit=1)
        if not category:
            cat_vals = {
                'parent_id': 1,
                'name': category_name,
                'property_cost_method': 'average',
                'economic_activity_id': 365
            }
            category = ObjCategory.create(cat_vals)
            _logger.info('Se creó la categoria: %s', category)
            _logger.info('El id es : %s', category.id)
        return category.id

    def _CheckProduct(self, product, category_id):
        ObjProductTemplate = self.env['product.template']
        ObjProductCabys = self.env['cabys.producto']
        ltsProduct = ObjProductTemplate.search([('euro_item_code', '=', product.codigo)], limit=1)

        try:
            if not ltsProduct:
                Cabys = ObjProductCabys.search([('codigo', '=', product.cod_hacienda)], limit=1)
                product_val = {
                    'name': product.descripcion,
                    'type': 'product',
                    'code_type_id': 4,
                    'cabys_product_id': Cabys.id,
                    'categ_id': category_id,
                    'list_price': self._CalculatePrice(product.precio),
                    "tracking": 'serial',
                    'standard_price': round(product.precio,2),
                    'euro_item_code': product.codigo
                }
                result = ObjProductTemplate.create(product_val)
                return result.id
            else:
                raise Exception('El product ya existe')
        except Exception as e:
            _logger.error(e)

    def _CalculatePrice(self, precio):
        ObjExchange = self.env['res.currency.rate']
        Exchange = ObjExchange.search([], order='name desc', limit=1)

        # Redondear el valor de Exchange a 2 decimales
        Price = round((precio / ((100 - 15) / 100) * Exchange.original_rate))
        Total = round(Price / 10) * 10  # Redondeamos al múltiplo de 10 más cercano directamente
        return Total

    def _CheckSupplierInfo(self, partner_id,product_id,product):

        Objsupplierinfo = self.env['product.supplierinfo']
        ltsSupplierinfo = Objsupplierinfo.search([('product_code', '=', product.codigo)], limit=1)
        try:
            if not ltsSupplierinfo:
                supplier_val = {
                    'product_tmpl_id': product_id,
                    'currency_id': 1,
                    'delay': 1,
                    'product_code': product.codigo,
                    'product_name': product.descripcion,
                    'min_qty': 1,
                    'price': product.precio,
                    'current_stock': int(product.stock),
                    'partner_id': partner_id,
                }
                Objsupplierinfo.create(supplier_val)
                _logger.info('Se creo el producto del proveedor correctamente')
                self._detachItem(product.codigo)
        except Exception as e:
            _logger.error(e)

    def _detachItem(self,codigo):
        product = self.env['eurocomp.producto'].search([('codigo', '=', codigo)], limit=1)
        if product:
            product.write({
               'added': True
            })
            _logger.info('El producto %s ha excluido de la lista', product.id)
        else:
            _logger.warning('No se encontró el producto con el id especificado')

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


