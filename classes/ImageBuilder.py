import logging
import base64
import requests
from PIL import Image
from io import BytesIO

_logger = logging.getLogger(__name__)

class ImageBuilder:

    def __init__(self):
        self.image_base = "https://pcmasters.tech/frames/WEB.jpg"
        self.final_width = 1920
        self.final_height = 1920
        self.scale_factor = 2.5  # Factor de escala para hacer la imagen más grande

    def _decode_base64(self, base64_str):
        """Decodifica una cadena base64 en una imagen binaria."""
        try:
            image_data = base64.b64decode(base64_str)
            return Image.open(BytesIO(image_data)).convert('RGBA')
        except Exception as e:
            _logger.error(f"Error decoding base64 image: {str(e)}")
            return None

    def _download_image(self, img_path):
        """Descargar imagen desde una URL o manejar cadena base64."""
        try:
            if img_path.startswith('https://'):
                _logger.info(f"Attempting to download image from URL: {img_path}")
                response = requests.get(img_path)
                if response.status_code == 200:
                    _logger.info(f"Successfully downloaded image from {img_path}")
                    image_data = BytesIO(response.content)
                    return Image.open(image_data).convert('RGBA')
                else:
                    _logger.error(f"Failed to download image from {img_path}. Status code: {response.status_code}")
                    return None
            elif isinstance(img_path, str):
                return self._decode_base64(img_path)

        except Exception as e:
            _logger.error(f"Error in _download_image: {str(e)}")
            return None

    def compute_image_1920(self, img_path):
        """Procesar y combinar imagen."""
        try:
            # Descargar la imagen de fondo
            _logger.info(f"Attempting to download background image from {self.image_base}")
            bg_response = requests.get(self.image_base)

            if bg_response.status_code == 200:
                _logger.info(f"Successfully downloaded background image from {self.image_base}")
                bg_image = Image.open(BytesIO(bg_response.content))
                bg_image = bg_image.resize((self.final_width, self.final_height), Image.LANCZOS)
            else:
                _logger.error(f"Failed to download background image from {self.image_base}. Status code: {bg_response.status_code}")
                return None

            # Obtener la imagen del producto
            prod_image = self._download_image(img_path)
            if prod_image is None:
                _logger.error("Failed to download or process product image.")
                return None

            # Redimensionar la imagen del producto manteniendo la relación de aspecto
            prod_image.thumbnail((self.final_width, self.final_height), Image.LANCZOS)

            # Aumentar el tamaño de la imagen del producto
            new_size = (int(prod_image.width * self.scale_factor), int(prod_image.height * self.scale_factor))
            prod_image = prod_image.resize(new_size, Image.LANCZOS)

            # Calcular la posición para centrar la imagen del producto en el fondo
            pos_x = (self.final_width - prod_image.width) // 2
            pos_y = (self.final_height - prod_image.height) // 2

            # Pegar la imagen del producto en el centro de la imagen de fondo
            bg_image.paste(prod_image, (pos_x, pos_y), prod_image)

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
