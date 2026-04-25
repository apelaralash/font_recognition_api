import tensorflow as tf
from pathlib import Path
from config.settings import settings

model = None

def load_tf_model():
    global model
    model_path = Path(settings.tf_model_path)

    if not model_path.exists():
        raise RuntimeError(f"Модель не найдена: {model_path}")

    model = tf.keras.models.load_model(str(model_path))
    print(f"✅ TensorFlow модель загружена: {model_path}")
    return model