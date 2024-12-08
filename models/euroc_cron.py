import logging
import base64
import requests
from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from ..classes import Sirett

_logger = logging.getLogger(__name__)

class EuroCron(models.TransientModel):
    _name = 'eurocomp.cron'
    _description = 'Modelo de sincronización de datos'

    def _get_sirett_config(self):
        # Método para obtener la configuración de Sirett
        config = self.env['ir.config_parameter'].sudo()
        return config
    def save_and_update_products(self):
        # Obtén la configuración de Sirett
        sirett_config = self._get_sirett_config()

        # Inicializa la conexión con Sirett
        user = sirett_config.get_param('eurocomp_username')
        password = sirett_config.get_param('eurocomp_password')

        sirett_connector = Sirett.SirettConnector(user, password)

        # Obtén los ítems de la bodega
        items = sirett_connector.get_items(pBodega=1)

        if not items:
            raise UserError("No se pudieron obtener los ítems de la bodega")

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

            # Actualiza la información del producto del proveedor
            partner = self.env['res.partner'].search([('vat', '=', '3101294674')], limit=1).id
            supplier_product = self.env['product.supplierinfo'].search([('product_code', '=', data['codigo']), ('partner_id', '=', partner)], limit=1)

            if supplier_product:
                # Si el registro ya existe, actualiza precio y stock
                supplier_product.write({
                'price': float(data['precio']),
                'current_stock': data['stock'],
                })
            else:
                # Si no existe, crea un nuevo registro
                self.env['product.supplierinfo'].create({
                    'product_tmpl_id': existing_product.id if existing_product else self.env['eurocomp.producto'].search([('codigo', '=', data['codigo'])], limit=1).id,
                    'currency_id': 1,
                    'delay': 1,
                    'product_code': data['codigo'],
                    'product_name': data['descripcion'],
                    'min_qty': 1,
                    'price': float(data['precio']),
                    'current_stock': data['stock'],
                    'partner_id': partner,
                })

            # Aquí se descarga la imagen y se convierte en base64 antes de asignarla
            if data['image_url'] and not existing_product.image_1920:
                image_url = "https://eurocompcr.com/" + data['image_url']
                try:
                    response = requests.get(image_url)
                    response.raise_for_status()  # Asegurarse de que la solicitud sea exitosa
                    # Almacenar la imagen en base64 como bytes
                    image_base64_bytes = base64.b64encode(response.content)
                    existing_product.image_1920 = image_base64_bytes
                except requests.exceptions.RequestException as e:
                    _logger.error("Error downloading image from %s: %s", image_url, e)

        return True

    def ProductSwitch(self, productid, state):
        Product_tmpl = self.env['product.template'].sudo().search([('id', '=', productid)], limit=1)
        if Product_tmpl:
            Product_tmpl.write({'active': state})
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
        self.save_and_update_products()
