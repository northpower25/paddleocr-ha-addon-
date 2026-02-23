import asyncio
import aiohttp
import logging
from homeassistant.components.image_processing import ImageProcessingEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    host = config.get("host", "http://supervisor/core/api/ingress")  # Beispiel
    entities = [PaddleOCREntity("paddleocr", host)]
    async_add_entities(entities)

class PaddleOCREntity(ImageProcessingEntity):
    def __init__(self, name, host):
        self._name = name
        self._host = host
        self._state = None
        self._last_text = ""

    @property
    def name(self):
        return self._name

    async def async_process_image(self, image):
        # image is bytes
        url = f"{self._host}/ocr"
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('file', image, filename='image.jpg', content_type='image/jpeg')
            async with session.post(url, data=data, timeout=60) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    texts = [l['text'] for l in result.get('lines', [])]
                    self._last_text = "\n".join(texts)
                    return self._last_text
                else:
                    _LOGGER.error("PaddleOCR server returned %s", resp.status)
                    return None
