import logging
import base64
import requests
from odoo import fields, models, api
from ..classes import Sirett

_logger = logging.getLogger(__name__)

class EuroCron(models.TransientModel):
    _name = 'eurocomp.cron'
    _description = 'Modelo de sincronización de datos'

    def _get_sirett_config(self):
        # Método para obtener la configuración de Sirett
        config = self.env['ir.config_parameter'].sudo()
        return config

    def save_Products(self):
        # Obtén la configuración de Sirett
        sirett_config = self._get_sirett_config()

        # Inicializa la conexión con Sirett
        user = sirett_config.get_param('eurocomp_username')
        password = sirett_config.get_param('eurocomp_password')

        sirett_connector = Sirett.SirettConnector(user, password)

        # Obtén los ítems de la bodega
        items = sirett_connector.get_items(pBodega=1)

        for data in items:
            existing_product = self.env['eurocomp.producto'].search([('codigo', '=', data['codigo'])], limit=1)

            if existing_product:
                # Si el registro ya existe, actualiza precio y stock
                existing_product.write({
                    'precio': float(data['precio']),
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
                    'precio': float(data['precio']),
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
        _user = _configs.get_param('eurocomp_username')
        _password = _configs.get_param('eurocomp_password')
        _connector = Sirett.SirettConnector(_user, _password)
        for product in ltsProducts:
            try:
                EuroProduct = _connector.get_item(1, product.product_code)[0]
                # Obtiene el stock actual utilizando un campo calculado en product.product
                Warehouse_Stock = product.product_tmpl_id.qty_available

                if EuroProduct['stock'] != product.current_stock:
                    product.current_stock = EuroProduct['stock']

                if EuroProduct['precio'] > product.price:
                    product.price = self._CalculatePrice(float(EuroProduct['precio']), True)
                    product.product_tmpl_id.list_price = self._CalculatePrice(float(EuroProduct['precio']))
                    product.product_tmpl_id.standart_price = self._CalculatePrice(float(EuroProduct['precio']), True)

                if product.product_tmpl_id.standart_price <= 0:
                    product.product_tmpl_id.list_price = self._CalculatePrice(float(EuroProduct['precio']))
                    product.product_tmpl_id.standart_price = self._CalculatePrice(float(EuroProduct['precio']), True)

                # Aquí se descarga la imagen y se convierte en base64 antes de asignarla
                if EuroProduct['image_url'] and not product.product_tmpl_id.image_1920:
                    image_url = "https://eurocompcr.com/" + EuroProduct['image_url']
                    try:
                        response = requests.get(image_url)
                        response.raise_for_status()  # Asegurarse de que la solicitud sea exitosa
                        # Almacenar la imagen en base64 como bytes
                        image_base64_bytes = base64.b64encode(response.content)
                        product.product_tmpl_id.image_1920 = image_base64_bytes
                    except requests.exceptions.RequestException as e:
                        _logger.error("Error downloading image from %s: %s", image_url, e)

                # Validación del stock actual en las bodegas y el stock del proveedor
                if int(EuroProduct['stock']) < int(_configs.get_param('eurocomp_stock_min')) and Warehouse_Stock <= 0:
                    self.ProductSwitch(product.product_tmpl_id.id, False)
                else:
                    self.ProductSwitch(product.product_tmpl_id.id, True)

            except Exception as e:
                _logger.error(e)

    def _CalculatePrice(self, precio, cost=False):
        ObjExchange = self.env['res.currency.rate']
        Exchange = ObjExchange.search([], order='name desc', limit=1)

        if not cost:
            margin = self.env['ir.config_parameter'].sudo().get_param('eurocomp_margin')
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
