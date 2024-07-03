from zeep import Client, Transport

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
        response = self._authenticate('wsc_request_bodega_all_items', int(pBodega))
        return response['data']

    def get_item(self, pBodega, pProducto):
        response = self._authenticate('wsp_request_bodega_item', int(pBodega), int(pProducto))
        return response['data']
