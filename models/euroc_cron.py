from odoo import fields, models, api
from ..Connectors import Sirett

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

    def ProductSwitch(self, productid,state):
        Product_tmpl = self.env['product.template'].sudo().search(['id','=',productid], limit=1)
        if state:
            Product_tmpl.active = True
        else:
            Product_tmpl.active = False
        Product_tmpl.save()

    def update_products(self):
        partner = self.env['res.partner'].search([('vat', '=', '3101294674')], limit=1).id
        ltsProducts = self.env['product.supplierinfo'].search([('partner_id','=',partner)])
        _configs = self._get_sirett_config()
        for Product in ltsProducts:
            _connector = Sirett.SirettConnector(_configs.eurocomp_username, _configs.eurocomp_password)
            EuroProduct = _connector.get_item(1,Product.product_code)
            if EuroProduct['stock'] != Product.current_stock:
                Product.current_stock = EuroProduct['stock']
            if EuroProduct['precio'] > Product.price:
                Product.price = EuroProduct['precio']
            if EuroProduct['stock'] < _configs.eurocomp_min_stock:
                self.ProductSwitch(Product.product_tmpl_id,False)
            else:
                self.ProductSwitch(Product.product_tmpl_id,True)
            Product.save()

    def cron_getItems(self):
        self.save_Products()

    def cron_updateItems(self):
        self.update_products()