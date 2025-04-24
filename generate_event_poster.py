from PIL import Image, ImageDraw, ImageFont
import os

# === File paths ===
BACKGROUND_PATH = "static/img/fur_bg.jpg"
FONT_TITLE = "static/fonts/FUR-Bold.ttf"
FONT_TEXT = "static/fonts/FUR-Regular.ttf"
OUTPUT_DIR = "temp"

# === Style & Sizes ===
IMG_WIDTH, IMG_HEIGHT = 1280, 720
TEXT_COLOR = (255, 215, 0)
SHADOW_COLOR = (0, 0, 0)
ROLE_COLOR = (255, 100, 100)
MOTTO = "Forged in Unity"

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = f"{line} {word}".strip()
        if draw.textlength(test, font=font) <= max_width:
            line = test
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines

def generate_event_poster(event, filename=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not filename:
        filename = f"event_{event['id']}.png"

    bg = Image.open(BACKGROUND_PATH).resize((IMG_WIDTH, IMG_HEIGHT)).convert("RGBA")
    draw = ImageDraw.Draw(bg)

    font_title = ImageFont.truetype(FONT_TITLE, 64)
    font_text = ImageFont.truetype(FONT_TEXT, 36)
    font_small = ImageFont.truetype(FONT_TEXT, 28)

    draw.text((170, 50), f"📅 {event['title']}", font=font_title, fill=TEXT_COLOR)
    draw.text((60, 160), f"🕒 {event['event_time']}", font=font_text, fill=TEXT_COLOR)
    draw.text((60, 220), f"🎭 {event['role'] or '—'}", font=font_text, fill=ROLE_COLOR)

    desc_lines = wrap_text(draw, f"📄 {event['description']}", font_text, 1160)
    for i, line in enumerate(desc_lines):
        draw.text((60, 300 + i * 42), line, font=font_text, fill=(240, 240, 240))

    draw.text((IMG_WIDTH - 400, IMG_HEIGHT - 60), MOTTO, font=font_small, fill=TEXT_COLOR)

    out_path = os.path.join(OUTPUT_DIR, filename)
    bg.save(out_path)
    print(f"✅ Poster saved to: {out_path}")
    return out_path
