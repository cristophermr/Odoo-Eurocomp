import logging
import base64
import requests
from PIL import Image
from io import BytesIO

_logger = logging.getLogger(__name__)

class ImageBuilder:

    def __init__(self):
        self.image_domain = "https://eurocompcr.com/"
        self.image_base = "https://pcmasters.tech/frames/WEB.jpg"
        self.final_width = 1920
        self.final_height = 1920

    def _decode_base64(self, base64_str):
        """Decodifica una cadena base64 en una imagen binaria."""
        try:
            # Decodificar la cadena base64
            image_data = base64.b64decode(base64_str)
            return Image.open(BytesIO(image_data)).convert('RGBA')
        except Exception as e:
            _logger.error(f"Error decoding base64 image: {str(e)}")
            return None

    def _download_image(self, img_path):
        """Descargar imagen desde una URL o manejar cadena base64."""
        try:
            # Verificar si img_path es una URL
            if img_path.startswith('https://'):
                response = requests.get(img_path)
                if response.status_code == 200:
                    image_data = BytesIO(response.content)
                    with Image.open(image_data) as img:
                        img.verify()  # Verificar la integridad de la imagen
                    image_data.seek(0)  # Reposición del cursor en el buffer
                    return Image.open(image_data).convert('RGBA')
                else:
                    _logger.error(f"Failed to download image. Status code: {response.status_code}")
                    return None

            # Si no es una URL, se trata de una cadena base64
            if isinstance(img_path, str):
                return self._decode_base64(img_path)

        except Exception as e:
            _logger.error(f"Error in _download_image: {str(e)}")
            return None

    def compute_image_1920(self, img_path):
        """Procesar y combinar imagen."""
        try:
            # Descargar la imagen de fondo
            bg_response = requests.get(self.image_base)
            if bg_response.status_code == 200:
                bg_image = Image.open(BytesIO(bg_response.content))
                bg_image = bg_image.resize((self.final_width, self.final_height), Image.LANCZOS)
            else:
                _logger.error(f"Failed to download background image. Status code: {bg_response.status_code}")
                return None

            # Obtener la imagen del producto
            prod_image = self._download_image(img_path)
            if prod_image is None:
                _logger.error("Failed to download or process product image.")
                return None

            # Redimensionar la imagen del producto a las dimensiones finales
            prod_image = prod_image.resize((self.final_width, self.final_height), Image.LANCZOS)

            # Centrar la imagen del producto en el fondo
            bg_image.paste(prod_image, (0, 0), prod_image)

            # Guardar la imagen combinada en un buffer
            buffered = BytesIO()
            bg_image.save(buffered, format="PNG")
            buffered.seek(0)

            # Convertir la imagen combinada a base64
            base64_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            return base64_str  # Devuelve la imagen en formato base64

        except Exception as e:
            _logger.error(f"Error in compute_image_1920: {str(e)}")
            return None
