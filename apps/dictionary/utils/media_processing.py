import io
import os
import tempfile
from PIL import Image
from django.core.files.base import ContentFile
import ffmpeg

GIF_FPS = 15
VIDEO_SIZE = 720
IMAGE_SIZE = 512


def process_image(image_file):
    if not image_file:
        return None

    img = Image.open(image_file)

    # Конвертация в RGB с учетом альфа-канала
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        if img.mode in ('RGBA', 'LA'):
            background.paste(img, mask=img.split()[-1])
            img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Кроп по центру и ресайз
    w, h = img.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    img = img.crop((left, top, left + min_dim, top + min_dim))
    img = img.resize((IMAGE_SIZE, IMAGE_SIZE), Image.Resampling.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=90, optimize=True)
    buffer.seek(0)
    filename = f"{os.path.splitext(image_file.name)[0]}.jpg"
    return ContentFile(buffer.getvalue(), name=filename)


import ffmpeg
import os
from django.core.files.base import ContentFile

VIDEO_SIZE = 720
GIF_FPS = 15

def process_video(video_file):
    tmp_input = f'/tmp/{video_file.name}'
    tmp_output = f'/tmp/{video_file.name.rsplit(".",1)[0]}_processed.mp4'

    # сохраняем входной файл
    with open(tmp_input, 'wb') as f:
        f.write(video_file.read())

    # обрезка до квадрата, масштаб, удаляем аудио
    ffmpeg.input(tmp_input).filter(
        'crop', 'min(in_w,in_h)', 'min(in_w,in_h)'
    ).filter(
        'scale', VIDEO_SIZE, VIDEO_SIZE
    ).output(
        tmp_output, vcodec='libx264', preset='ultrafast', an=None
    ).run(overwrite_output=True)

    with open(tmp_output, 'rb') as f:
        content = ContentFile(f.read(), name=os.path.basename(tmp_output))

    os.remove(tmp_input)
    os.remove(tmp_output)
    return content

def video_to_gif(video_content):
    tmp_input = f'/tmp/{video_content.name}'
    tmp_output = f'/tmp/{video_content.name.rsplit(".",1)[0]}.gif'

    with open(tmp_input, 'wb') as f:
        f.write(video_content.read())

    ffmpeg.input(tmp_input).filter('fps', GIF_FPS).filter(
        'scale', VIDEO_SIZE, VIDEO_SIZE
    ).output(tmp_output).run(overwrite_output=True)

    with open(tmp_output, 'rb') as f:
        content = ContentFile(f.read(), name=os.path.basename(tmp_output))

    os.remove(tmp_input)
    os.remove(tmp_output)
    return content
