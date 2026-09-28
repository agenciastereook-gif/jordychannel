"""Regenera PNG, identidad.json y la lámina de muestra. Requiere Pillow.

Ejecutar desde cualquier carpeta: python generar_kit.py
Las fuentes y licencias se incluyen en fuentes/. No modifica Estudio.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
C = {"negro": "#101010", "papel": "#F4F0E6", "amarillo": "#FFE000",
     "azul": "#0047FF", "rojo": "#FF2A23"}
F = {"titulo": "Anton.ttf", "texto": "IBMPlexSans-Regular.ttf",
     "semibold": "IBMPlexSans-SemiBold.ttf"}


def text(box, size, value, font="texto", color="papel", line=None, minimum=None,
         lines=1, align="left", key=None):
    return {"kind": "text", "box": box, "font": font, "size_px": size,
            "line_height_px": line or round(size * 1.2), "min_size_px": minimum or size,
            "max_lines": lines, "align": align, "color": color,
            "sample": value, "content_key": key}


def rect(box, color, opacity=1):
    return {"kind": "rect", "box": box, "color": color, "opacity": opacity}


def motion(seconds, delta=(0, 0), opacity=(0, 1), ease="ease_out_cubic"):
    return {"duration_s": seconds, "translate_from_px": list(delta),
            "translate_to_px": [0, 0], "opacity": list(opacity), "easing": ease}


def leave(seconds, delta=(0, 0)):
    return {"duration_s": seconds, "translate_from_px": [0, 0],
            "translate_to_px": list(delta), "opacity": [1, 0], "easing": "ease_in_cubic"}


def format_spec(vertical):
    v = vertical
    lower = [72, 1160, 852, 160] if v else [96, 688, 960, 136]
    x, y, w, h = lower
    credit = [72, 1352, 660, 44] if v else [96, 610, 720, 44]
    cx, cy, cw, ch = credit
    sub = [72, 1424, 852, 144] if v else [360, 866, 1200, 128]
    sx, sy, sw, sh = sub
    mx, my = (72, 156) if v else (96, 54)
    return {
        "canvas_px": [1080, 1920] if v else [1920, 1080],
        "safe_box": [72, 144, 852, 1440] if v else [96, 54, 1728, 972],
        "pieces": {
            "zocalo": {"enter": motion(.30, (-64, 0)), "exit": leave(.20, (-32, 0)),
                "hold_s": 4, "layers": [rect(lower, "negro", .94),
                    rect([x, y, 8, h], "amarillo"),
                    text([x+32, y+22, w-64, 60 if v else 52], 52 if v else 44,
                         "[NOMBRE Y APELLIDO]", "titulo", minimum=42 if v else 36, key="nombre"),
                    text([x+32, y+(96 if v else 80), w-64, 40], 30 if v else 28,
                         "[Cargo o función]", key="cargo")]},
            "credito": {"enter": motion(.16), "exit": leave(.12),
                "hold": "during_credited_asset", "layers": [rect(credit, "negro", .92),
                    text([cx+16, cy+6, cw-32, 32], 24, "Imagen: [Autor / medio]", key="credito")]},
            "subtitulos": {"enter": motion(0, ease="linear"), "exit": leave(0),
                "hold": "speech_cue", "layers": [rect(sub, "negro", .92),
                    text([sx+24, sy+16, sw-48, sh-32], 46 if v else 40,
                         "Así se ve una frase\nsubtitulada en pantalla.", "semibold",
                         line=56 if v else 48, lines=2, align="center", key="subtitulo")]},
            "marca_agua": {"enter": motion(.24), "exit": leave(.16),
                "hold": "entire_video", "layers": [rect([mx-8, my-8, 184, 72], "negro", .80),
                    {"kind": "image", "box": [mx, my, 168, 56],
                     "file": "logos/marca-agua-clara-168.png", "opacity": 1}]},
            "dato": {"background": "azul", "enter": motion(.24, (0, 24)),
                "exit": leave(.16), "hold_s": 4,
                "hold_formula": "max(4, visible_word_count / 3)", "layers": (
                    [text([72, 432, 852, 44], 30, "LA CIFRA", "semibold"),
                     rect([72, 500, 96, 10], "papel"),
                     text([72, 550, 852, 336], 312, "[CIFRA]", "titulo", minimum=176, key="cifra"),
                     text([72, 922, 852, 68], 44, "[Unidad / período]", "semibold", key="unidad"),
                     text([72, 1024, 852, 126], 42, "[Qué mide este dato\ny a quiénes alcanza]", line=54,
                          lines=2, key="contexto"),
                     text([72, 1200, 852, 84], 26, "Fuente: [Organismo / documento]\n[Fecha del dato]",
                          line=34, lines=2, key="fuente")]
                    if v else
                    [text([96, 250, 800, 44], 30, "LA CIFRA", "semibold"),
                     rect([96, 318, 96, 10], "papel"),
                     text([96, 382, 816, 250], 212, "[CIFRA]", "titulo", minimum=144, key="cifra"),
                     text([96, 660, 816, 60], 36, "[Unidad / período]", "semibold", key="unidad"),
                     rect([960, 382, 4, 300], "papel", .65),
                     text([1040, 388, 784, 174], 44, "[Qué mide este dato\ny a quiénes alcanza]",
                          line=56, lines=3, key="contexto"),
                     text([1040, 610, 784, 80], 26, "Fuente: [Organismo / documento]\n[Fecha del dato]",
                          line=34, lines=2, key="fuente")])},
            "cita": {"background": "papel", "enter": motion(.28, (0, 24)),
                "exit": leave(.20), "hold_s": 6,
                "hold_formula": "max(6, quote_and_attribution_word_count / 3)", "layers": (
                    [text([72, 376, 852, 44], 30, "CITA", "semibold", "negro"),
                     rect([72, 450, 96, 10], "rojo"),
                     text([72, 530, 852, 500], 112, "«[Frase textual\nverificada,\nsin cambiar\nsus palabras]»", "titulo", "negro",
                          line=128, minimum=88, lines=4, key="cita"),
                     text([72, 1080, 852, 58], 38, "[Nombre y apellido]", "semibold", "negro", key="autor"),
                     text([72, 1152, 852, 84], 30, "[Cargo o función]", color="negro",
                          line=40, lines=2, key="cargo"),
                     text([72, 1256, 852, 76], 26, "Fuente: [Medio / documento]\n[Fecha de la declaración]",
                          color="negro", line=34, lines=2, key="fuente")]
                    if v else
                    [text([96, 218, 1728, 44], 30, "CITA", "semibold", "negro"),
                     rect([96, 290, 96, 10], "rojo"),
                     text([300, 310, 1524, 310], 104, "«[Frase textual verificada,\nsin cambiar sus palabras]»", "titulo", "negro",
                          line=120, minimum=84, lines=2, key="cita"),
                     text([300, 658, 1524, 58], 40, "[Nombre y apellido]", "semibold", "negro", key="autor"),
                     text([300, 726, 1524, 42], 28, "[Cargo o función]", color="negro", key="cargo"),
                     text([300, 788, 1524, 40], 24, "Fuente: [Medio / documento] · [Fecha]",
                          color="negro", key="fuente")])}
        }
    }


SPEC = {
    "brand": "Jordy en Vivo", "version": "1.0", "date": "2026-09-28",
    "status": "Design assets and layout specification; not integrated into Estudio",
    "palette": C,
    "fonts": {
        "titulo": {"family": "Anton", "style": "Regular", "weight": 400, "file": "fuentes/Anton.ttf"},
        "texto": {"family": "IBM Plex Sans", "style": "Regular", "weight": 400, "file": "fuentes/IBMPlexSans-Regular.ttf"},
        "semibold": {"family": "IBM Plex Sans", "style": "SemiBold", "weight": 600, "file": "fuentes/IBMPlexSans-SemiBold.ttf"}},
    "geometry": {"units": "reference_pixels", "box": "[x, y, width, height]",
                 "origin": "top_left", "text_origin": "top_left_of_visible_ink",
                 "font_size": "em_pixels", "tracking_px": 0, "radius_px": 0,
                 "scale": "output_width / reference_width; output aspect ratio must match reference",
                 "rounding": "nearest_integer_half_up_after_scaling"},
    "text_fit": {"method": "word_wrap_then_decrease_font_size_by_2px",
                 "line_height": "multiply_original_line_height_by_fitted_size / original_size",
                 "word_break": False, "ellipsis": False, "horizontal_stretch": False,
                 "on_overflow": "reject_and_request_shorter_authorized_text_or_split_into_cards",
                 "preserve_quote_text": True, "source_required_for_data_and_quotes": True,
                 "placeholders_allowed_in_production": False},
    "composition": {"video_order": ["footage", "credito", "zocalo", "subtitulos", "marca_agua"],
                    "card_order": ["background", "dato_or_cita", "subtitulos", "marca_agua"],
                    "exclusive": [["dato", "cita", "zocalo"]],
                    "omit_credit_on_cards": True, "card_source_replaces_image_credit": True,
                    "skip_subtitle_background_when_no_cue": True},
    "texture": {"default": "none", "optional": "static_monochrome_grain_on_card_background_only",
                "max_opacity": .03, "grain_size_px": [1, 2], "on_text_or_logo": False},
    "motion": {"easing": {"ease_out_cubic": "1-(1-t)^3", "ease_in_cubic": "t^3", "linear": "t"},
               "frame_quantization": "duration=0 => 0 frames; otherwise max(1, floor(seconds*fps+0.5))",
               "property_interpolation": "start+(end-start)*easing(clamp(elapsed/duration,0,1))",
               "piece_scope": "animate piece layers as one group; full-card background cuts at scene boundary",
               "watermark_scope": "once_at_video_start_and_end; never_restart_on_shot_change",
               "default_image_transition": {"type": "cut", "duration_s": 0},
               "optional_same_scene_stills_transition": {"type": "crossfade", "duration_s": .12},
               "crossfade_scope": "footage_only_keep_overlays_stationary",
               "still_motion": "none", "count_up_numbers": False, "flash_or_bounce": False,
               "max_same_video_continuous_s": 5},
    "formats": {"vertical": format_spec(True), "horizontal": format_spec(False)}
}


def color(name, opacity=1):
    h = C.get(name, name).lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (round(255*opacity),)


def font(key, size):
    return ImageFont.truetype(str(ROOT / "fuentes" / F[key]), size)


def ink(draw, xy, value, f, fill):
    b = f.getbbox(value)
    draw.text((xy[0]-b[0], xy[1]-b[1]), value, font=f, fill=fill)


def logo(compact, theme, scale=2):
    # Geometría tipográfica: se dibuja de cero; no se recortan las referencias.
    size = (480, 160) if compact else (1200, 240)
    im = Image.new("RGBA", (size[0]*scale, size[1]*scale))
    d = ImageDraw.Draw(im)
    fill = color(theme)
    if compact:
        ink(d, (20*scale, 16*scale), "JORDY", font("titulo", 144*scale), fill)
        d.ellipse(tuple(v*scale for v in (390, 53, 444, 107)), fill=color("rojo"))
    else:
        ink(d, (20*scale, 20*scale), "JORDY", font("titulo", 230*scale), fill)
        d.rectangle(tuple(v*scale for v in (600, 42, 1180, 212)), outline=fill, width=6*scale)
        ink(d, (628*scale, 93*scale), "EN VIVO", font("semibold", 92*scale), fill)
        d.ellipse(tuple(v*scale for v in (1078, 89, 1154, 165)), fill=color("rojo"))
    return im


def fitted_lines(layer):
    _, _, width, height = layer["box"]
    for size in range(layer["size_px"], layer["min_size_px"]-1, -2):
        f = font(layer["font"], size)
        lines = []
        for paragraph in layer["sample"].split("\n"):
            line = ""
            for word in paragraph.split():
                trial = f"{line} {word}".strip()
                if f.getlength(trial) <= width:
                    line = trial
                else:
                    if line:
                        lines.append(line)
                    line = word
            lines.append(line)
        lh = layer["line_height_px"] * size / layer["size_px"]
        max_width = max(f.getbbox(s)[2]-f.getbbox(s)[0] for s in lines)
        total = (len(lines)-1)*lh + max(f.getbbox(s)[3]-f.getbbox(s)[1] for s in lines)
        if len(lines) <= layer["max_lines"] and max_width <= width and total <= height:
            return f, lines, lh
    raise ValueError(f"Texto fuera de caja: {layer['sample']!r}")


def render_layer(im, layer):
    x, y, w, h = layer["box"]
    if layer["kind"] == "image":
        asset = Image.open(ROOT / layer["file"]).convert("RGBA").resize((w, h), Image.Resampling.LANCZOS)
        im.alpha_composite(asset, (x, y))
        return
    overlay = Image.new("RGBA", im.size)
    d = ImageDraw.Draw(overlay)
    if layer["kind"] == "rect":
        d.rectangle((x, y, x+w-1, y+h-1), fill=color(layer["color"], layer.get("opacity", 1)))
    else:
        f, lines, lh = fitted_lines(layer)
        for i, value in enumerate(lines):
            tw = f.getbbox(value)[2]-f.getbbox(value)[0]
            tx = x + ((w-tw)/2 if layer["align"] == "center" else 0)
            ink(d, (tx, y+i*lh), value, f, color(layer["color"]))
    im.alpha_composite(overlay)


def render_scene(fmt, kind):
    config = SPEC["formats"][fmt]
    W, H = config["canvas_px"]
    pieces = config["pieces"]
    im = Image.new("RGBA", (W, H), color(pieces.get(kind, {}).get("background", "negro")))
    if kind == "video":
        # Fondo neutro de maqueta, sin personas, fotos ni información periodística.
        d = ImageDraw.Draw(im)
        for x in range(0, W, 120):
            d.line((x, 0, x, H), fill=(30, 30, 29, 255), width=1)
        for y in range(0, H, 120):
            d.line((0, y, W, y), fill=(30, 30, 29, 255), width=1)
        ink(d, (72 if fmt == "vertical" else 96, 500 if fmt == "vertical" else 270),
            "VIDEO", font("titulo", 180), (54, 54, 51, 255))
        for name in ["credito", "zocalo", "subtitulos", "marca_agua"]:
            for layer in pieces[name]["layers"]:
                render_layer(im, layer)
    else:
        for name in [kind, "marca_agua"]:
            for layer in pieces[name]["layers"]:
                render_layer(im, layer)
    # Sello de maqueta fuera del área segura; no forma parte de las piezas.
    d = ImageDraw.Draw(im)
    ink(d, (72 if fmt == "vertical" else 96, H-70), "MAQUETA · CAMPOS SIN COMPLETAR",
        font("semibold", 20), color("negro" if kind == "cita" else "papel", .7))
    return im.convert("RGB")


def build():
    for folder in ["logos", "muestras"]:
        (ROOT / folder).mkdir(exist_ok=True)
    for theme, label in [("papel", "claro"), ("negro", "oscuro")]:
        logo(False, theme).save(ROOT / "logos" / f"logo-{label}-2400.png")
        mark = logo(True, theme)
        mark.resize((480, 160), Image.Resampling.LANCZOS).save(ROOT / "logos" / f"marca-agua-{label}-480.png")
        small_label = "clara" if theme == "papel" else "oscura"
        mark.resize((168, 56), Image.Resampling.LANCZOS).save(ROOT / "logos" / f"marca-agua-{small_label}-168.png")
    (ROOT / "identidad.json").write_text(json.dumps(SPEC, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    for fmt in SPEC["formats"]:
        for kind in ["video", "dato", "cita"]:
            render_scene(fmt, kind).save(ROOT / "muestras" / f"{fmt}-{kind}.png")
    board = Image.new("RGB", (1800, 1620), C["papel"])
    d = ImageDraw.Draw(board)
    header_logo = Image.open(ROOT / "logos" / "logo-oscuro-2400.png").resize((650, 130), Image.Resampling.LANCZOS)
    board.paste(header_logo, (54, 16), header_logo)
    ink(d, (65, 146), "SISTEMA VISUAL  /  VIDEO VERTICAL + HORIZONTAL  /  01", font("semibold", 23), C["negro"])
    swatch_x = 65
    for key, value in C.items():
        d.rectangle((swatch_x, 206, swatch_x+310, 264), fill=value, outline=C["negro"] if key == "papel" else value)
        ink(d, (swatch_x, 278), f"{key.upper()}  {value}", font("semibold", 19), C["negro"])
        swatch_x += 342
    labels = ["01 / VIDEO · ZÓCALO · SUBTÍTULOS", "02 / PLACA DE DATO", "03 / PLACA DE CITA"]
    for i, kind in enumerate(["video", "dato", "cita"]):
        x = 65+i*570
        ink(d, (x, 352), labels[i], font("semibold", 21), C["negro"])
        vert = Image.open(ROOT / "muestras" / f"vertical-{kind}.png").resize((378, 672), Image.Resampling.LANCZOS)
        board.paste(vert, (x, 406))
        if kind == "cita":
            d.rectangle((x, 406, x+377, 1077), outline=C["negro"], width=1)
        hor = Image.open(ROOT / "muestras" / f"horizontal-{kind}.png").resize((530, 298), Image.Resampling.LANCZOS)
        board.paste(hor, (x, 1124))
        if kind == "cita":
            d.rectangle((x, 1124, x+529, 1421), outline=C["negro"], width=1)
    ink(d, (65, 1480), "ANTON REGULAR  +  IBM PLEX SANS REGULAR / SEMIBOLD", font("semibold", 25), C["negro"])
    ink(d, (65, 1530), "Maquetas de aplicación. Los campos entre corchetes se reemplazan por información verificada.",
        font("texto", 22), C["negro"])
    board.save(ROOT / "vista-general.jpg", quality=94)
    validate()


def validate():
    """Comprueba tamaños, transparencia, encaje y separación de zonas."""
    for name, config in SPEC["formats"].items():
        W, H = config["canvas_px"]
        for piece in config["pieces"].values():
            for layer in piece["layers"]:
                x, y, w, h = layer["box"]
                assert 0 <= x < x+w <= W and 0 <= y < y+h <= H, (name, layer)
                if layer["kind"] == "text":
                    fitted_lines(layer)
        # Zócalo, crédito y subtítulos deben poder coexistir sin superponerse.
        boxes = [config["pieces"][p]["layers"][0]["box"] for p in ["zocalo", "credito", "subtitulos"]]
        for i, a in enumerate(boxes):
            for b in boxes[i+1:]:
                assert a[0]+a[2] <= b[0] or b[0]+b[2] <= a[0] or a[1]+a[3] <= b[1] or b[1]+b[3] <= a[1]
    for path in (ROOT / "logos").glob("*.png"):
        im = Image.open(path)
        assert im.mode == "RGBA" and im.getchannel("A").getextrema() == (0, 255), path
    print("OK: 2 formatos, 6 piezas, textos dentro de sus cajas y 6 PNG con transparencia real.")


if __name__ == "__main__":
    build()
