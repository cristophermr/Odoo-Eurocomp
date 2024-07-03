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
                    'precio': data['precio'],
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
                    'precio': data['precio'],
                    'stock': data['stock'],
                    'caracteristicas': data['caracteristicas'],
                    'peso': data['peso'],
                    'medida': data['medida'],
                })

        return True

    def cron_getItems(self):
        self.save_Products()
