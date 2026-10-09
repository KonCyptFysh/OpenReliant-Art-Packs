"""Portable compositing recipe from the selected HUD authoring pipeline."""
from pathlib import Path
from PIL import Image

def trim(image: Image.Image) -> Image.Image:
    alpha = image.getchannel("A")
    box = alpha.getbbox()
    if box is None:
        raise ValueError("neutral render is empty")
    return image.crop(box)


def tint(image: Image.Image, state: str) -> Image.Image:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    gray = rgba.convert("L")
    if state == "gold":
        low, high = (35, 14, 0), (224, 132, 12)
    else:
        low, high = (30, 1, 0), (205, 26, 12)
    visible = sorted(value for value, a in zip(gray.getdata(), alpha.getdata()) if a > 8)
    if visible:
        dark = visible[len(visible) // 50]
        bright = visible[min(len(visible) - 1, len(visible) * 49 // 50)]
    else:
        dark, bright = 0, 255
    span = max(1, bright - dark)
    colored = Image.new("RGBA", rgba.size)
    pixels = []
    for value, a in zip(gray.getdata(), alpha.getdata()):
        normalized = max(0.0, min(1.0, (value - dark) / span))
        t = (0.18 + 0.82 * normalized) ** 0.82
        pixels.append(tuple(round(low[i] + (high[i] - low[i]) * t) for i in range(3)) + (a,))
    colored.putdata(pixels)
    return colored


def composite_slots(neutral: Image.Image, slots: list[dict], canvas_size: int, output: Path) -> list[dict]:
    scale = canvas_size / 112.0
    base = trim(neutral)
    selected_box = slots[0]["reference_bbox"]
    target_major = round(max(selected_box[2] - selected_box[0],
                             selected_box[3] - selected_box[1]) * scale)
    ratio = target_major / max(base.size)
    base = base.resize((max(1, round(base.width * ratio)), max(1, round(base.height * ratio))),
                       Image.Resampling.LANCZOS)
    records = []
    for slot in slots:
        # Neutral render is horizontal. Slot zero is the upright, selected
        # missile; subsequent slots progress clockwise in 36-degree steps.
        rotated = base.rotate(-slot["angle_degrees"],
                              resample=Image.Resampling.BICUBIC, expand=True)
        sprite = tint(rotated, slot["state"])
        center = [round(value * scale) for value in slot["center"]]
        position = (center[0] - sprite.width // 2, center[1] - sprite.height // 2)
        canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        canvas.alpha_composite(sprite, position)
        path = output / f"slot_{slot['slot']:02d}_{slot['state']}.png"
        canvas.save(path)
        records.append({**slot, "output": str(path), "canvas": [canvas_size, canvas_size],
                        "placed_bbox": list(canvas.getchannel("A").getbbox() or ())})
    return records

