import io
import os
import tempfile
import subprocess
from PIL import Image
from django.core.files.base import ContentFile

GIF_FPS = 20
VIDEO_SIZE = 720
IMAGE_SIZE = 512


def process_image(image_file):
    if not image_file:
        return None

    img = Image.open(image_file)

    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1])
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

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


def process_video(video_file):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_in:
        tmp_in.write(video_file.read())
        tmp_input = tmp_in.name

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_out:
        tmp_output = tmp_out.name

    cmd = ["ffmpeg",
        "-i", tmp_input,
        "-vf",
        "crop=min(iw\\,ih):min(iw\\,ih):(iw-min(iw\\,ih))/2:(ih-min(iw\\,ih))/2,"
        f"scale={VIDEO_SIZE}:{VIDEO_SIZE}:flags=lanczos",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "slow",
        "-an",
        "-y",
        tmp_output
    ]

    subprocess.run(cmd, check=True)

    with open(tmp_output, "rb") as f:
        content = ContentFile(f.read(), name=os.path.basename(tmp_output))

    os.remove(tmp_input)
    os.remove(tmp_output)

    return content


def video_to_gif(video_file):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_in:
        tmp_in.write(video_file.read())
        tmp_input = tmp_in.name

    palette_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
    gif_file = tempfile.NamedTemporaryFile(suffix=".gif", delete=False).name

    # 1. генерация палитры
    cmd_palette = [
        "ffmpeg",
        "-i", tmp_input,
        "-vf", f"fps={GIF_FPS},palettegen=stats_mode=diff",
        "-y",
        palette_file
    ]
    subprocess.run(cmd_palette, check=True)

    # 2. применение палитры
    cmd_gif = [
        "ffmpeg",
        "-i", tmp_input,
        "-i", palette_file,
        "-filter_complex", f"fps={GIF_FPS},paletteuse=dither=none",
        "-y",
        gif_file
    ]
    subprocess.run(cmd_gif, check=True)

    with open(gif_file, "rb") as f:
        content = ContentFile(f.read(), name=os.path.basename(gif_file))

    os.remove(tmp_input)
    os.remove(palette_file)
    os.remove(gif_file)

    return content
