import logging

from zeep import Client, Transport

_logger = logging.getLogger(__name__)
class SirettConnector:
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.WSDL = "https://eurocompcr.com/webservice.php?wsdl"
        self.client = self._initialize_client()

    def _initialize_client(self):
        transport = Transport(session=False)
        client = Client(self.WSDL, transport=transport)
        return client

    def _authenticate(self, service_method, *args):
        service = getattr(self.client.service, service_method)
        return service(self.user, self.password, *args)

    def get_items(self, pBodega):
        # Suponiendo que este método no necesita 'icodigo'
        response = self._authenticate('wsc_request_bodega_all_items', int(pBodega))
        return response['data']

    def get_item(self, pBodega, pProducto):
        try:
            response = self._authenticate('wsc_request_bodega_all_item', int(pBodega), str(pProducto))
            return response['data']
        except Exception as e:
            _logger.info(f"Error fetching item {pProducto} from bodega {pBodega}: {e}")
            _logger.info(f"Args: {self.user}, {self.password}, {int(pBodega)}, {str(pProducto)}")
            return None