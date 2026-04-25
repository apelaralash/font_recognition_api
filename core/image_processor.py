import numpy as np
import cv2

def read_image_from_bytes(image_bytes: bytes, flags=cv2.IMREAD_GRAYSCALE) -> np.ndarray:
    stream = np.frombuffer(image_bytes, dtype=np.uint8)
    return cv2.imdecode(stream, flags)

def preprocess_image_for_model(
    image_bytes: bytes,
    target_height: int = 105,
    target_width: int = 105
) -> np.ndarray:
    img = read_image_from_bytes(image_bytes, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Не удалось декодировать изображение. Формат повреждён или не поддерживается.")

    h, w = img.shape

    scale = target_height / h
    new_width = max(1, int(w * scale))

    img = cv2.resize(img, (new_width, target_height), interpolation=cv2.INTER_AREA)

    if new_width > target_width:
        img = img[:, :target_width]  # Обрезаем справа
    else:
        pad_width = target_width - new_width
        pad = np.ones((target_height, pad_width), dtype=np.uint8) * 255  # Белый фон
        img = np.concatenate([img, pad], axis=1)

    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=-1)  # (H, W) -> (H, W, 1)
    img = np.expand_dims(img, axis=0)  # (H, W, 1) -> (1, H, W, 1) — batch

    return img