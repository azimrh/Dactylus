import io
from PIL import Image
from django.core.files.base import ContentFile


def process_category_image(image_file):
    if not image_file:
        return None

    img = Image.open(image_file)

    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        if img.mode in ('RGBA', 'LA'):
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Обрезаем до квадрата (центрированно)
    width, height = img.size
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    img = img.crop((left, top, right, bottom))

    img = img.resize((512, 512), Image.Resampling.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=90, optimize=True)
    buffer.seek(0)

    filename = f"{image_file.name.rsplit('.', 1)[0]}.jpg"
    return ContentFile(buffer.getvalue(), name=filename)
