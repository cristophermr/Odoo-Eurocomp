import requests
from PIL import Image, ImageOps
from io import BytesIO
import base64


class ImageBuilder:

    def __init__(self):
        self.image_domain = "https://eurocompcr.com/"
        self.image_base = "https://pcmasters.tech/frames/WEB.jpg"
        self.image_width = 512
        self.image_height = 512

    def _compute_image_1920(self, img_url):
        try:
            # Descargar la imagen de fondo
            bg_response = requests.get('https://pcmasters.tech/frames/WEB.jpg')
            bg_image = Image.open(BytesIO(bg_response.content))

            # Descargar la imagen del producto
            prod_response = requests.get("")
            prod_image = Image.open(BytesIO(prod_response.content)).convert('RGBA')

            # Redimensionar la imagen del producto manteniendo la relación de aspecto
            prod_image.thumbnail((480, 480), Image.LANCZOS)

            # Asegurarse de que la imagen no sea más grande que el fondo
            if prod_image.width > bg_image.width or prod_image.height > bg_image.height:
                prod_image.thumbnail((bg_image.width, bg_image.height), Image.LANCZOS)

            # Ajustar la imagen del producto al centro del fondo
            bg_image.paste(prod_image, ((bg_image.width - prod_image.width) // 2,
                                        (bg_image.height - prod_image.height) // 2),
                           prod_image)

            # Guardar la imagen combinada en un buffer
            buffered = BytesIO()
            bg_image.save(buffered, format="PNG")

            # Codificar la imagen en base64
            image_1920 = base64.b64encode(buffered.getvalue())
            print(image_1920)
        except Exception as e:
            print(e)
            # _logger.error('Error al procesar la imagen: %s', str(e))


# Ejemplo de uso
if __name__ == "__main__":
    image_builder = ImageBuilder()
    image_url = "https://eurocompcr.com/upload/items/2018/9/4051_8664.jpg"
    base64_image = image_builder._compute_image_1920()
    print(base64_image)
