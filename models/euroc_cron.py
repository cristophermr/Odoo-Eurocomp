import logging

from odoo import fields, models, api
from ..Connectors import Sirett

_logger = logging.getLogger(__name__)


class EuroCron(models.TransientModel):
    _name = 'eurocomp.cron'
    _description = 'Modelo de sincronización de datos'

    def _get_sirett_config(self):
        # Método para obtener la configuración de Sirett
        config = self.env['res.config.settings'].sudo().search([], limit=1)
        return config

    def save_Products(self):
        # Obtén la configuración de Sirett
        sirett_config = self._get_sirett_config()

        if not sirett_config:
            return False  # No hay configuración disponible

        # Inicializa la conexión con Sirett
        user = sirett_config.eurocomp_username
        password = sirett_config.eurocomp_password
        sirett_connector = Sirett.SirettConnector(user, password)

        # Obtén los ítems de la bodega
        items = sirett_connector.get_items(pBodega=1)

        for data in items:
            existing_product = self.env['eurocomp.producto'].search([('codigo', '=', data['codigo'])], limit=1)

            if existing_product:
                # Si el registro ya existe, actualiza precio y stock
                existing_product.write({
                    'precio': float(data['precio'].replace(',', '.')),
                    'stock': data['stock'],
                })
            else:
                # Si no existe, crea un nuevo registro
                self.env['eurocomp.producto'].create({
                    'codigo': data['codigo'],
                    'cod_hacienda': data['cod_hacienda'],
                    'descripcion': data['descripcion'],
                    'familia': data['familia'],
                    'marca': data['marca'],
                    'clase': data['clase'],
                    'modelo': data['modelo'],
                    'precio': float(data['precio'].replace(',', '.')),
                    'stock': data['stock'],
                    'caracteristicas': data['caracteristicas'],
                    'peso': data['peso'],
                    'medida': data['medida'],
                })

        return True

    def ProductSwitch(self, productid, state):
        Product_tmpl = self.env['product.template'].sudo().search([('id', '=', productid)], limit=1)
        if Product_tmpl:
            Product_tmpl.write({'active': state})

    def update_products(self):
        partner = self.env['res.partner'].search([('vat', '=', '3101294674')], limit=1).id
        ltsProducts = self.env['product.supplierinfo'].search([('partner_id', '=', partner)])
        _configs = self._get_sirett_config()

        for product in ltsProducts:
            try:
                _connector = Sirett.SirettConnector(_configs.eurocomp_username, _configs.eurocomp_password)
                EuroProduct = _connector.get_item(1, product.product_code)[0]

                # Obtiene el stock actual utilizando un campo calculado en product.product
                Warehouse_Stock = product.product_tmpl_id.qty_available #Esto esta mal

                if EuroProduct['stock'] != product.current_stock:
                    product.current_stock = EuroProduct['stock']

                if EuroProduct['precio'] > product.price:
                    product.price = self._CalculatePrice(float(EuroProduct['precio']),True)
                    product.product_tmpl_id.list_price = self._CalculatePrice(float(EuroProduct['precio']))
                    product.product_tmpl_id.standart_price = self._CalculatePrice(float(EuroProduct['precio']),True)

                # Validación del stock actual en las bodegas y el stock del proveedor
                if EuroProduct['stock'] < _configs.eurocomp_stock_min and Warehouse_Stock <= 0:
                    self.ProductSwitch(product.product_tmpl_id.id, False)
                else:
                    self.ProductSwitch(product.product_tmpl_id.id, True)
                product.update()
            except Exception as e:
                _logger.error(e)

    def _CalculatePrice(self, precio, cost=False):
        ObjExchange = self.env['res.currency.rate']
        Exchange = ObjExchange.search([], order='name desc', limit=1)

        if cost == False:
            margin = self.env['res.config.settings'].sudo().search([], limit=1).eurocomp_margin
            # Redondear el valor de Exchange a 2 decimales
            Price = round((precio / ((100 - int(margin)) / 100) * Exchange.original_rate))
            Total = round(Price / 10) * 10  # Redondeamos al múltiplo de 10 más cercano directamente
            return float(Total)
        else:
            return float(round(precio * Exchange.original_rate / 10) * 10)


    def cron_getItems(self):
        self.save_Products()

    def cron_updateItems(self):
        self.update_products()
