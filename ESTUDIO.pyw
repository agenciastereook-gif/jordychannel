# -*- coding: utf-8 -*-
"""
ESTUDIO v0.1
------------
Panel único para armar los shorts de Jordy en Vivo · El Hit.

  - Barra lateral con los shorts (estilo Discord, igual que StreamDash)
  - Investigación y guion con ChatGPT (Codex, con tu cuenta de ChatGPT)
  - Transcripción gratis en la compu, asignación de material y textos con Claude
  - Armado del video y vista previa, todo en la misma ventana

Sin librerías externas: solo Python y Windows. Doble clic y listo (no abre consola).
La ventana es Edge en modo app; la interfaz está en estudio/index.html.

Cada short vive en episodios/AAAA-MM-DD-slug/:
    tema.txt  investigacion.md  guion.md  voz.<ext>  voz.srt  marcas.txt
    material/  .mini/  asignacion.txt  imagenes/  short.mp4  textos.md
"""

import difflib
import html
import json
import mimetypes
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_NAME = "Estudio"
VERSION = "0.1"
PUERTO = 8430

RAIZ = Path(__file__).resolve().parent
EPISODIOS = RAIZ / "episodios"
SCRIPTS = RAIZ / "scripts"
PROMPTS = RAIZ / "prompts"
WEB = RAIZ / "estudio"

AUDIOS = {".mp3", ".m4a", ".wav", ".ogg", ".opus", ".aac"}
IMAGENES = {".png", ".jpg", ".jpeg", ".webp"}
VIDEOS = {".mp4", ".mov", ".webm", ".m4v"}
SIN_VENTANA = 0x08000000 if sys.platform.startswith("win") else 0
PLACEHOLDER_GUION = "(Borrá esta línea"

def actualizar_path():
    """Al abrir con doble clic, Windows puede pasar un PATH viejo (de antes de instalar Codex,
    Claude o Gemini). Lo releo del registro y sumo las carpetas de Node/npm."""
    rutas = []
    try:
        import winreg
        for raiz, clave in ((winreg.HKEY_CURRENT_USER, r"Environment"),
                            (winreg.HKEY_LOCAL_MACHINE,
                             r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")):
            try:
                with winreg.OpenKey(raiz, clave) as k:
                    rutas += os.path.expandvars(winreg.QueryValueEx(k, "Path")[0]).split(";")
            except OSError:
                pass
    except ImportError:
        pass
    rutas += [os.path.expandvars(r"%APPDATA%\npm"), os.path.expandvars(r"%ProgramFiles%\nodejs")]
    actuales = os.environ.get("PATH", "").split(os.pathsep)
    nuevas = [r for r in rutas if r and r not in actuales and os.path.isdir(r)]
    os.environ["PATH"] = os.pathsep.join(actuales + nuevas)


actualizar_path()
sys.path.insert(0, str(SCRIPTS))
from nuevo_episodio import slug as hacer_slug  # noqa: E402

mimetypes.add_type("audio/mp4", ".m4a")
mimetypes.add_type("image/webp", ".webp")


# ------------------------------------------------------------------ utilidades
def leer(path):
    try:
        return Path(path).read_text(encoding="utf-8-sig")
    except Exception:
        return ""


def escribir(path, texto):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(texto, encoding="utf-8")


def sin_numerales(texto):
    """Los .md exportados desde Word traen '# ' delante de cada línea: lo saco."""
    lineas = texto.splitlines()
    llenas = [l for l in lineas if l.strip()]
    if llenas and all(l.lstrip().startswith("#") for l in llenas):
        lineas = [re.sub(r"^\s*#\s?", "", l) for l in lineas]
    return "\n".join(lineas).replace("\\_", "_").replace("\\[", "[").replace("\\]", "]")


def prompt_de(archivo):
    """Contenido de un prompt: lo que está después de la primera línea '---' (si la hay)."""
    texto = sin_numerales(leer(PROMPTS / archivo))
    partes = re.split(r"^---\s*$", texto, maxsplit=1, flags=re.M)
    return (partes[1] if len(partes) == 2 else texto).strip()


def plantilla(nombre, **datos):
    """Prompt editable de prompts/estudio/<nombre>.md; {{CLAVE}} se completa con los datos del short."""
    texto = re.sub(r"<!--.*?-->\s*", "", leer(PROMPTS / "estudio" / f"{nombre}.md"), flags=re.S).strip()
    for clave, valor in datos.items():
        texto = texto.replace("{{" + clave + "}}", str(valor))
    return texto


def ffmpeg_bin():
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return None


def correr(cmd, cwd=None, entrada=None, log=None):
    """Corre un comando sin ventana; manda cada línea de salida a log(). Devuelve (código, salida)."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1",
               HF_HUB_DISABLE_SYMLINKS_WARNING="1", HF_HUB_VERBOSITY="error",
               PYTHONWARNINGS="ignore")
    p = subprocess.Popen(cmd, cwd=cwd, env=env, creationflags=SIN_VENTANA,
                         stdin=subprocess.PIPE if entrada is not None else subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, encoding="utf-8", errors="replace")
    if entrada is not None:
        threading.Thread(target=lambda: (p.stdin.write(entrada), p.stdin.close()), daemon=True).start()
    salida = []
    for linea in p.stdout:
        salida.append(linea)
        if log and linea.strip():
            log(linea.rstrip())
    return p.wait(), "".join(salida)


def python_cmd():
    exe = Path(sys.executable)
    consola = exe.with_name("python.exe")
    return str(consola if consola.exists() else exe)


# ------------------------------------------------------------------ herramientas
def estado_herramientas():
    codex, claude = shutil.which("codex"), shutil.which("claude")
    r = {"codex": bool(codex), "codex_login": False, "claude": bool(claude),
         "claude_login": False, "ffmpeg": bool(ffmpeg_bin()),
         "gemini": bool(agy_exe()), "gemini_login": gemini_conectado()}
    try:
        import faster_whisper  # noqa: F401
        r["whisper"] = True
    except ImportError:
        r["whisper"] = False
    if codex:
        _, out = correr([codex, "login", "status"])
        r["codex_login"] = "Logged in" in out
    if claude:
        _, out = correr([claude, "auth", "status"])
        r["claude_login"] = '"loggedIn": true' in out
    return r


AGY_DIR = Path.home() / ".gemini" / "antigravity-cli"


def agy_exe():
    """Antigravity CLI (agy), el reemplazo gratis de Gemini CLI. winget lo deja fuera del PATH viejo."""
    if shutil.which("agy"):
        return shutil.which("agy")
    for f in (Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages").glob(
            "Google.AntigravityCLI_*/agy.exe"):
        return str(f)
    return None


def gemini_conectado():
    """La sesión va al llavero de Windows; este archivo aparece después del primer login."""
    return (AGY_DIR / "cache" / "default_project_id.txt").exists()


HERRAMIENTAS = {}


def refrescar_herramientas():
    actualizar_path()
    HERRAMIENTAS.clear()
    HERRAMIENTAS.update(estado_herramientas())


# ------------------------------------------------------------------ El Recorte
def carpeta_videos():
    """La carpeta Videos de Windows (donde El Recorte guarda lo que exporta)."""
    try:
        import ctypes
        import uuid
        guid = uuid.UUID("{18989B1D-99B5-455B-841C-AB7C74E4DDFC}")  # FOLDERID_Videos
        buf = ctypes.c_wchar_p()
        ctypes.windll.shell32.SHGetKnownFolderPath(
            ctypes.byref(ctypes.c_buffer(guid.bytes_le)), 0, None, ctypes.byref(buf))
        ruta = Path(buf.value)
        ctypes.windll.ole32.CoTaskMemFree(buf)
        return ruta
    except Exception:
        return Path.home() / "Videos"


RECORTE = carpeta_videos() / "El Recorte" / "Exportados"
MINIS_RECORTE = Path(os.environ.get("LOCALAPPDATA", RAIZ)) / "JordyEstudio" / "mini-recorte"


def exportados_recorte():
    if not RECORTE.is_dir():
        return []
    archivos = [f for f in RECORTE.iterdir() if f.is_file() and f.suffix.lower() in VIDEOS]
    archivos.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    salida = []
    ff = ffmpeg_bin()
    for f in archivos[:24]:
        mini = MINIS_RECORTE / (f.name + ".jpg")
        if ff and (not mini.exists() or mini.stat().st_mtime < f.stat().st_mtime):
            mini.parent.mkdir(parents=True, exist_ok=True)
            correr([ff, "-y", "-v", "error", "-ss", "1", "-i", str(f), "-frames:v", "1",
                    "-vf", "scale=360:-2", str(mini)])
        salida.append({"nombre": f.name, "fecha": time.strftime("%d/%m %H:%M", time.localtime(f.stat().st_mtime)),
                       "mb": round(f.stat().st_size / 1e6, 1), "mini": mini.exists()})
    return salida


def importar_material(c, origen):
    origen = Path(origen)
    if not origen.is_file() or origen.suffix.lower() not in IMAGENES | VIDEOS:
        raise Falla(f"No encontré ese archivo de foto o video: {origen.name}")
    destino = c / "material" / origen.name
    n = 2
    while destino.exists():
        destino = c / "material" / f"{origen.stem}-{n}{origen.suffix}"
        n += 1
    shutil.copy2(origen, destino)
    return destino.name


# ------------------------------------------------------------------ episodios
def carpeta(slug):
    c = (EPISODIOS / Path(slug).name).resolve()
    if c.parent != EPISODIOS.resolve() or not c.is_dir():
        raise FileNotFoundError(slug)
    return c


def voz_de(c):
    for f in sorted(c.iterdir()):
        if f.is_file() and f.stem == "voz" and f.suffix.lower() in AUDIOS:
            return f
    return None


def audios_sueltos(c):
    return [f for f in c.iterdir() if f.is_file() and f.suffix.lower() in AUDIOS
            and f.stem != "voz_original" and not f.name.startswith(".")]


def titulo_de(c):
    tema = leer(c / "tema.txt").strip()
    if tema:
        return tema
    primera = leer(c / "guion.md").strip().splitlines()
    if primera and primera[0].startswith("#"):
        return primera[0].lstrip("# ").strip()
    return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", c.name).replace("-", " ")


def guion_de(c):
    g = leer(c / "guion.md")
    return "" if PLACEHOLDER_GUION in g else g


def listar_episodios():
    EPISODIOS.mkdir(exist_ok=True)
    eps = [c for c in EPISODIOS.iterdir() if c.is_dir() and not c.name.startswith(".")]
    eps.sort(key=lambda c: c.name, reverse=True)
    return [{"slug": c.name, "titulo": titulo_de(c), "fecha": c.name[:10],
             "listo": (c / "short.mp4").exists()} for c in eps]


def nuevo_episodio(tema):
    import datetime
    base = f"{datetime.date.today():%Y-%m-%d}-{hacer_slug(tema)}"
    c, n = EPISODIOS / base, 2
    while c.exists():
        c, n = EPISODIOS / f"{base}-{n}", n + 1
    (c / "material").mkdir(parents=True)
    escribir(c / "tema.txt", tema.strip() + "\n")
    return c.name


def miniatura(c, f):
    """Ruta relativa de la miniatura (imágenes: el archivo mismo; videos: un fotograma)."""
    if f.suffix.lower() in IMAGENES:
        return f"material/{f.name}"
    if f.suffix.lower() not in VIDEOS:
        return None
    mini = c / ".mini" / (f.name + ".jpg")
    if not mini.exists() or mini.stat().st_mtime < f.stat().st_mtime:
        ff = ffmpeg_bin()
        if not ff:
            return None
        mini.parent.mkdir(exist_ok=True)
        for ss in ("1", "0"):
            correr([ff, "-y", "-v", "error", "-ss", ss, "-i", str(f), "-frames:v", "1",
                    "-vf", "scale=480:-2", str(mini)])
            if mini.exists():
                break
    return f".mini/{f.name}.jpg" if mini.exists() else None


def material_de(c):
    m = c / "material"
    m.mkdir(exist_ok=True)
    salida, creditos = [], creditos_de(c)
    for f in sorted(m.iterdir(), key=lambda x: x.name.lower()):
        ext = f.suffix.lower()
        if f.is_file() and ext in IMAGENES | VIDEOS:
            salida.append({"nombre": f.name, "tipo": "video" if ext in VIDEOS else "imagen",
                           "mini": miniatura(c, f), "descripcion": descripcion_de(c, f),
                           "fuente": creditos.get(f.name, {}).get("fuente", "")})
    return salida


def descripcion_de(c, f):
    """Lo que Gemini vio en un video (si ya lo miró y el video no cambió)."""
    d = c / ".mini" / (f.name + ".txt")
    if d.exists() and d.stat().st_mtime >= f.stat().st_mtime:
        return leer(d).strip()
    return ""


MARCA = re.compile(r"^\s*\[(\d+(?:\.\d+)?)\]\s*(.*)$")


def marcas_de(c):
    salida = []
    for l in leer(c / "marcas.txt").splitlines():
        m = MARCA.match(l)
        if m:
            salida.append({"t": float(m.group(1)), "texto": m.group(2).strip()})
    return salida


def asignacion_de(c):
    salida = {}
    for l in leer(c / "asignacion.txt").splitlines():
        m = re.match(r"^\s*\[(\d+(?:\.\d+)?)\]\s*([^|]+?)\s*(?:\|.*)?$", l)
        if m:
            archivo = m.group(2).strip()
            salida[f"{float(m.group(1)):.2f}"] = archivo.replace("material/", "", 1)
    return salida


def escribir_asignacion(c, filas):
    """filas: [{t, archivo, texto}] con archivo = nombre en material/, '=' o 'IA'."""
    lineas = []
    for f in filas:
        a = (f.get("archivo") or "IA").strip()
        ruta = a if a in ("=", "IA") else f"material/{Path(a).name}"
        lineas.append(f"[{float(f['t']):.2f}] {ruta} | {f.get('texto', '').strip()}")
    escribir(c / "asignacion.txt", "\n".join(lineas) + "\n")


IAS = {"chatgpt": ("ChatGPT", "investigacion.md"),
       "gemini": ("Gemini", "investigacion_gemini.md"),
       "claude": ("Claude", "investigacion_claude.md")}


def fuentes_de(c):
    try:
        return json.loads(leer(c / "fuentes.json") or "[]")
    except ValueError:
        return []


def agregar_fuente(c, texto):
    texto = texto.strip()
    if not texto:
        raise Falla("La fuente está vacía.")
    fuentes = fuentes_de(c)
    if re.fullmatch(r"https?://\S+", texto):
        fuentes.append({"tipo": "link", "url": texto})
    else:
        primera = next((l.strip() for l in texto.splitlines() if l.strip()), "")
        fuentes.append({"tipo": "texto", "titulo": primera[:90], "texto": texto})
    escribir(c / "fuentes.json", json.dumps(fuentes, ensure_ascii=False, indent=2))


def borrar_fuente(c, i):
    fuentes = fuentes_de(c)
    if 0 <= i < len(fuentes):
        fuentes.pop(i)
    escribir(c / "fuentes.json", json.dumps(fuentes, ensure_ascii=False, indent=2))


def investigaciones_de(c):
    """{ia: texto} de las investigaciones que ya están hechas."""
    return {ia: leer(c / archivo) for ia, (_, archivo) in IAS.items() if leer(c / archivo).strip()}


def bloque_editor(c):
    """Tema, eje y fuentes que carga Jordy: van en todos los pedidos de investigación y guion."""
    partes = [f"TEMA:\n{leer(c / 'tema.txt').strip() or titulo_de(c)}"]
    eje = leer(c / "eje.txt").strip()
    if eje:
        partes.append(f"EJE PERIODÍSTICO (decisión del editor):\n{eje}")
    fuentes = fuentes_de(c)
    if fuentes:
        lineas = []
        for i, f in enumerate(fuentes, 1):
            if f["tipo"] == "link":
                lineas.append(f"[{i}] Link: {f['url']} (abrilo y leelo)")
            else:
                lineas.append(f"[{i}] Nota completa pegada por el editor:\n<<<\n{f['texto']}\n>>>")
        partes.append("FUENTES QUE APORTA EL EDITOR (consultalas primero):\n" + "\n\n".join(lineas))
    return "\n\n".join(partes)


def material_investigacion(c):
    invs = investigaciones_de(c)
    return "\n\n".join(f"=== INFORME DE INVESTIGACIÓN ({IAS[ia][0]}) ===\n{texto.strip()}"
                       for ia, texto in invs.items())


PROMPTS_EDITABLES = [  # (id, nombre en pantalla, archivo)
    ("investigacion", "1 · Investigación", PROMPTS / "00_investigacion.md"),
    ("guion", "2 · Guion", PROMPTS / "01_guion_chatgpt.md"),
    ("manual", "2 · Manual de estilo", RAIZ / "modelos" / "MANUAL_DE_ESTILO.md"),
    ("revisar_datos", "2 · Revisar datos", PROMPTS / "estudio" / "revisar_datos.md"),
    ("ortografia", "2 · Revisión ortográfica", PROMPTS / "estudio" / "ortografia.md"),
    ("revision_completa", "2 · Revisión completa", PROMPTS / "estudio" / "revision_completa.md"),
    ("buscar_material", "3 · Buscar material", PROMPTS / "estudio" / "buscar_material.md"),
    ("mirar_videos", "3 · Mirar videos", PROMPTS / "estudio" / "mirar_videos.md"),
    ("asignacion", "4 · Asignación", PROMPTS / "estudio" / "asignacion.md"),
    ("editar", "5 · Editar con Claude", PROMPTS / "estudio" / "editar.md"),
    ("textos", "6 · Textos", PROMPTS / "03_publicacion.md"),
]
ORIGINALES = PROMPTS / ".originales"


def prompts_editables():
    return [{"id": i, "nombre": n, "archivo": str(a.relative_to(RAIZ)), "texto": leer(a),
             "tocado": (ORIGINALES / a.name).exists() and leer(ORIGINALES / a.name) != leer(a)}
            for i, n, a in PROMPTS_EDITABLES]


def guardar_prompt(pid, texto=None):
    """Guarda un prompt editado (la primera vez respalda el original). Sin texto, vuelve al original."""
    archivo = next(a for i, _, a in PROMPTS_EDITABLES if i == pid)
    respaldo = ORIGINALES / archivo.name
    if texto is None:
        if respaldo.exists():
            escribir(archivo, leer(respaldo))
        return
    if not respaldo.exists():
        escribir(respaldo, leer(archivo))
    escribir(archivo, texto)


STREAMDASH_AJUSTES = Path(r"P:\TRANSMISIONES\JORDY EN VIVO\GRAPH\v2\ajustes.json")


def estilos_streamdash():
    """Estilos principal y secundario del perfil actual de StreamDash (si está a mano)."""
    try:
        d = json.loads(STREAMDASH_AJUSTES.read_text(encoding="utf-8"))
        perfiles = d.get("perfiles", {})
        perfil = perfiles.get(d.get("perfil_actual")) if isinstance(perfiles, dict) else perfiles[0]
        return {k: perfil[k] for k in ("principal", "secundario") if k in perfil}
    except Exception:
        return {}


def datos_episodio(slug):
    c = carpeta(slug)
    voz = voz_de(c)
    video = c / "short.mp4"
    return {
        "slug": c.name,
        "titulo": titulo_de(c),
        "tema": leer(c / "tema.txt").strip() or titulo_de(c),
        "eje": leer(c / "eje.txt").strip(),
        "fuentes": fuentes_de(c),
        "investigaciones": investigaciones_de(c),
        "guion": guion_de(c),
        "guion_edicion": leer(c / "guion_edicion.html"),
        "guion_previo": leer(c / "guion_edicion_previo.html") or html.escape(leer(c / "guion_previo.md")),
        "meta": meta_de(c),
        "edicion": edicion_de(c),
        "subtitulos": subtitulos_de(c),
        "audios_extra": sorted(f.name for f in (c / "audios").glob("*") if f.suffix.lower() in AUDIOS)
        if (c / "audios").is_dir() else [],
        "voz": voz.name if voz else None,
        "voz_v": int(voz.stat().st_mtime) if voz else 0,
        "guion_ia_marcas": leer(c / "guion_edicion_ia.html"),
        "pedido": {"pendiente": (c / ".pedido_claude").exists(), "en_curso": leer(c / ".pedido_en_curso").strip()},  # para que el navegador no use la voz vieja
        "voz_original": any(f.stem == "voz_original" for f in c.iterdir()),
        "audios_sueltos": [f.name for f in audios_sueltos(c) if f != voz],
        "srt": (c / "voz.srt").exists(),
        "material": material_de(c),
        "marcas": marcas_de(c),
        "asignacion": asignacion_de(c),
        "video": video.exists(),
        "video_v": int(video.stat().st_mtime) if video.exists() else 0,
        "textos": leer(c / "textos.md"),
        "revision": leer(c / "revision_guion.md"),
        "tarea": TAREAS.get(c.name),
        "redactor": redactor(),
    }


# ------------------------------------------------------------------ tareas (IA y scripts)
TAREAS = {}
CANDADO = threading.Lock()


class Falla(Exception):
    pass


def tarea_investigar(c, log, estado, datos):
    if not (leer(c / "tema.txt").strip() or fuentes_de(c)):
        raise Falla("Escribí el tema (o agregá una fuente) antes de investigar.")
    ias = [ia for ia in datos.get("ias", []) if ia in IAS]
    if not ias:
        raise Falla("Elegí al menos una IA para investigar.")
    instrucciones = re.sub(r"TEMA:\s*<pegá el tema[^>]*>\s*$", "", prompt_de("00_investigacion.md")).rstrip()
    prompt = f"{instrucciones}\n\n{bloque_editor(c)}\n"

    def una(ia):
        nombre, archivo = IAS[ia]
        milog = lambda linea: log(f"{nombre}: {linea}")  # noqa: E731
        try:
            if ia == "chatgpt":
                texto = codex(prompt, c, milog, buscar=True)
            elif ia == "gemini":
                texto = gemini("Es una investigación periodística: usá la búsqueda web y abrí los links "
                               "que te pasan.", prompt, c, milog)
            else:
                texto = claude(prompt, c, milog, herramientas="WebSearch WebFetch")
            escribir(c / archivo, texto.strip() + "\n")
            estado["partes"][ia] = "ok"
            milog("listo.")
        except Falla as e:
            estado["partes"][ia] = "error"
            milog(str(e))

    estado["partes"] = {ia: "corriendo" for ia in ias}
    hilos = [threading.Thread(target=una, args=(ia,), daemon=True) for ia in ias]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    if not any(v == "ok" for v in estado["partes"].values()):
        raise Falla("Ninguna IA pudo terminar la investigación.")


def tarea_guion(c, log, datos=None):
    invs = investigaciones_de(c)
    if not invs:
        raise Falla("Todavía no hay investigación generada.")
    instr = prompt_de("01_guion_chatgpt.md")
    instr = re.sub(r"MATERIAL:.*$", "", instr, flags=re.S).rstrip()
    manual = sin_numerales(leer(RAIZ / "modelos" / "MANUAL_DE_ESTILO.md"))
    extra = []
    if leer(c / "eje.txt").strip():
        extra.append("EJE PERIODÍSTICO: lo decide el editor y el guion va en esa línea. No lo contradigas ni "
                     "cambies el enfoque. Si el material tensiona el eje, no lo cambies: anotalo al final, "
                     "en la sección OBSERVACIONES.")
    tipo = meta_de(c).get("tipo_editor")
    if tipo:
        extra.append(f"TIPO DE RELATO: {tipo} (lo eligió el editor: usá esa estructura).")
    if len(invs) > 1:
        extra.append("Hay varios informes de investigación hechos por distintas IA. Cruzalos: usá lo "
                     "coincidente; un dato que aparece en un solo informe es exclusivo (atribuilo o marcá "
                     "[VERIFICAR]); si los informes se contradicen, no elijas uno: [VERIFICAR].")
    prompt = (f"{instr}\n\n" + "\n\n".join(extra) +
              f"\n\n=== MANUAL_DE_ESTILO.md (adjunto) ===\n{manual}\n=== FIN DEL MANUAL ===\n\n"
              f"{bloque_editor(c)}\n\nMATERIAL:\n{material_investigacion(c)}\n")
    ia = (datos or {}).get("ia") if (datos or {}).get("ia") in IAS else "chatgpt"
    if ia == "gemini":
        texto = gemini("Escribí el guion periodístico.", prompt, c, log)
    elif ia == "claude":
        texto = claude(prompt, c, log)
    else:
        texto = codex(prompt, c, log, buscar=False)
    partes = separar_guion(texto)
    escribir(c / "guion.md", (partes.get("GUION") or texto).strip() + "\n")
    escribir(c / "guion_ia.md", (partes.get("GUION") or texto).strip() + "\n")  # para saber qué cambió el editor
    (c / "guion_edicion.html").unlink(missing_ok=True)  # guion nuevo: sin marcas viejas
    lineas = lambda k: [l for l in partes.get(k, "").splitlines() if l.strip()]  # noqa: E731
    escribir_meta(c, {
        "tipo": tipo or partes.get("TIPO", "").strip(), "tipo_editor": tipo, "redactor": IAS[ia][0],
        "tension": partes.get("TENSIÓN", "").strip(), "datos": partes.get("DATOS ESENCIALES", "").strip(),
        "observaciones": partes.get("OBSERVACIONES", "").strip(),
        "titulos": lineas("TÍTULOS")[:3],
        "verificar": [{"texto": l, "ok": False} for l in lineas("VERIFICAR")]})


def codex(prompt, c, log, buscar, imagenes=()):
    exe = shutil.which("codex")
    if not exe:
        raise Falla("No está instalado Codex (ChatGPT). Corré INSTALAR.bat.")
    salida = c / ".codex_salida.md"
    salida.unlink(missing_ok=True)
    adjuntos = [x for img in imagenes for x in ("-i", str(img))]
    # -i acepta varios valores: después va otra opción (-s) para que "-" no se tome como imagen
    cmd = [exe] + (["--search"] if buscar else []) + [
        "exec", "--skip-git-repo-check", "--ephemeral", *adjuntos, "-s", "read-only",
        "-C", str(c), "-o", str(salida), "-"]
    log("ChatGPT trabajando" + (" (con búsqueda web)" if buscar else "") + "...")
    codigo, out = correr(cmd, entrada=prompt, log=None)
    texto = leer(salida).strip()
    salida.unlink(missing_ok=True)
    if codigo != 0 or not texto:
        if "login" in out.lower():
            raise Falla("Codex no tiene sesión de ChatGPT. En una terminal: codex login")
        raise Falla("ChatGPT no devolvió nada.\n" + out[-800:])
    return texto + "\n"


def claude(prompt, c, log, herramientas=""):
    exe = shutil.which("claude")
    if not exe:
        raise Falla("No está instalado Claude Code. Corré INSTALAR.bat.")
    cmd = [exe, "-p", "--output-format", "text"]
    if herramientas:
        cmd += ["--allowedTools", herramientas]
    log("Claude trabajando...")
    codigo, out = correr(cmd, cwd=str(c), entrada=prompt)
    if codigo != 0 or not out.strip():
        if "login" in out.lower():
            raise Falla("Claude Code no tiene sesión. En una terminal escribí: claude  (y después /login)")
        raise Falla("Claude no devolvió nada.\n" + out[-800:])
    return out.strip()


def gemini(instruccion, contenido, c, log, modelo=None):
    """Gemini por Antigravity CLI. agy no lee la entrada estándar: el pedido va en un archivo que
    abre con su herramienta de lectura. Sin interfaz, agy rechaza solo todo lo que no esté permitido
    en su settings.json (comandos, escribir archivos): solo lee páginas y sus propios archivos."""
    exe = agy_exe()
    if not exe:
        raise Falla("No está instalado Gemini (Antigravity). Corré INSTALAR.bat.")
    ajustes = AGY_DIR / "settings.json"
    if not ajustes.exists():
        escribir(ajustes, json.dumps({"permissions": {"allow": [
            "read_url(*)", f"read_file({AGY_DIR.as_posix()}/**)"]}}, indent=2))
    pedido = c / f".pedido_gemini_{threading.get_ident()}.md"
    escribir(pedido, contenido)
    cmd = [exe] + (["--model", modelo] if modelo else []) + ["-p",
           f"{instruccion} El pedido completo está en el archivo {pedido.name} de esta carpeta: abrilo con "
           f"tu herramienta para leer archivos (sin ejecutar comandos) y cumplilo al pie de la letra. No crees "
           f"archivos ni artefactos ni pidas aprobación: respondé con el resultado completo en tu respuesta."]
    log(("Claude" if modelo and "claude" in modelo else "Gemini") + " trabajando...")
    try:
        codigo, out = correr(cmd, cwd=str(c))
    finally:
        pedido.unlink(missing_ok=True)
    if "Authentication required" in out:
        raise Falla("Gemini no tiene sesión. En una terminal escribí: agy  (y entrá con tu cuenta de Google)")
    if codigo != 0 or not out.strip() or out.startswith("jetski:"):
        raise Falla("Gemini no devolvió nada.\n" + out[-800:])
    # agy linkea archivos locales como file:///...; en el texto alcanza con el nombre
    return re.sub(r"\[([^\]]+)\]\(file:///[^)]+\)", r"\1", out).strip() + "\n"


def separar_guion(texto):
    """Reparte la respuesta de ChatGPT en sus secciones (=== TIPO ===, === GUION ===, ...)."""
    partes, actual = {}, None
    for linea in texto.splitlines():
        if linea.strip().startswith("```"):  # algunas IA envuelven la respuesta en bloques de código
            continue
        m = re.fullmatch(r"\s*=+\s*([A-ZÁÉÍÓÚÑ ]+?)\s*=+\s*", linea)
        if m:
            actual = m.group(1).strip()
            partes[actual] = ""
        elif actual:
            limpia = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s+", "", linea).replace("**", "")
            partes[actual] += (limpia if actual != "GUION" else linea) + "\n"
    return partes


def meta_de(c):
    try:
        return json.loads(leer(c / "guion_meta.json") or "{}")
    except ValueError:
        return {}


def escribir_meta(c, meta):
    escribir(c / "guion_meta.json", json.dumps(meta, ensure_ascii=False, indent=2))


def marcar_cambios(antes, despues):
    """HTML del editor: lo que se sacó en <del> (tachado rojo), lo que se agregó en <ins> (verde)."""
    partes = lambda s: re.findall(r"\s+|\w+|[^\w\s]", s)  # noqa: E731
    a, b = partes(antes), partes(despues)
    salida = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            salida.append(html.escape("".join(a[i1:i2])))
            continue
        if i2 > i1:
            salida.append(f"<del>{html.escape(''.join(a[i1:i2]))}</del>")
        if j2 > j1:
            salida.append(f"<ins>{html.escape(''.join(b[j1:j2]))}</ins>")
    return "".join(salida)


def tarea_ortografia(c, log):
    guion = guion_de(c).strip()
    if not guion:
        raise Falla("Falta el guion.")
    prompt = plantilla("ortografia", GUION=guion)
    corregido = codex(prompt, c, log, buscar=False).strip()
    guardar_reescritura(c, guion, corregido, "Revisión ortográfica")


def guardar_reescritura(c, antes, despues, cual, notas=None):
    """Deja la reescritura marcada y guarda la versión de Jordy para "Prefiero mi guion"."""
    escribir(c / "guion_previo.md", leer(c / "guion.md"))
    escribir(c / "guion_edicion_previo.html", leer(c / "guion_edicion.html"))
    escribir(c / "guion_edicion.html", marcar_cambios(antes, despues))
    escribir(c / "guion_edicion_ia.html", leer(c / "guion_edicion.html"))
    escribir(c / "guion.md", despues + "\n")
    meta = meta_de(c)
    meta["revision_pendiente"] = cual
    if notas is not None:
        meta["notas_revision"] = notas
    escribir_meta(c, meta)


def guion_con_marcas(c):
    """El guion con las correcciones del editor escritas como [[AGREGADO: ...]] y [[BORRADO: ...]]."""
    h = leer(c / "guion_edicion.html")
    if not re.search(r"<(ins|del)>", h):  # sin marcas: comparo con lo que entregó la IA
        original = leer(c / "guion_ia.md").strip()
        h = marcar_cambios(original, guion_de(c).strip()) if original else html.escape(guion_de(c).strip())
    h = re.sub(r"<del>(.*?)</del>", r"[[BORRADO: \1]]", h, flags=re.S)
    h = re.sub(r"<ins>(.*?)</ins>", r"[[AGREGADO: \1]]", h, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", h)).strip()


def tarea_completa(c, log):
    guion = guion_de(c).strip()
    if not guion:
        raise Falla("Falta el guion.")
    manual = sin_numerales(leer(RAIZ / "modelos" / "MANUAL_DE_ESTILO.md"))
    prompt = plantilla("revision_completa", EDITOR=bloque_editor(c), GUION_CON_MARCAS=guion_con_marcas(c),
                       MANUAL=manual, INVESTIGACION=material_investigacion(c))
    partes = separar_guion(codex(prompt, c, log, buscar=True))
    final = partes.get("GUION", "").strip()
    if not final:
        raise Falla("ChatGPT no devolvió el guion revisado.")
    guardar_reescritura(c, guion, final, "Revisión completa", partes.get("NOTAS", "").strip())


def tarea_revisar(c, log):
    guion = guion_de(c).strip()
    if not guion:
        raise Falla("Falta el guion.")
    contenido = plantilla("revisar_datos", GUION=guion, EDITOR=bloque_editor(c),
                          INVESTIGACION=material_investigacion(c))
    escribir(c / "revision_guion.md", gemini(
        "Revisá el guion de noticias.", contenido, c, log))


def describir_videos(c, log):
    """Gemini mira cada video completo (los cuadros, no el sonido) y deja la descripción junto a la miniatura."""
    if not (agy_exe() and gemini_conectado()):
        return
    videos = [f for f in sorted((c / "material").iterdir())
              if f.is_file() and f.suffix.lower() in VIDEOS and not descripcion_de(c, f)]
    for i, f in enumerate(videos, 1):
        log(f"Gemini mirando {f.name} ({i}/{len(videos)})...")
        try:
            texto = gemini(
                f"Mirá completo el video material/{f.name} (abrilo con tu herramienta para leer archivos).",
                plantilla("mirar_videos"), c, log)
            escribir(c / ".mini" / (f.name + ".txt"), texto)
        except Falla as e:
            log(f"(no pude describir {f.name}: {str(e).splitlines()[0]})")


def tarea_describir(c, log):
    if not (agy_exe() and gemini_conectado()):
        raise Falla("Gemini no está conectado. En una terminal escribí: agy  (y entrá con tu cuenta de Google)")
    describir_videos(c, log)


def claude_conectado():
    if "claude_login" not in HERRAMIENTAS:
        refrescar_herramientas()
    return HERRAMIENTAS.get("claude_login", False)


def redactor():
    """Asignación y textos: Claude si está conectado (necesita plan Pro), si no ChatGPT."""
    return "claude" if claude_conectado() else "chatgpt"


def tarea_transcribir(c, log):
    voz = voz_de(c)
    if not voz:
        raise Falla("Falta la grabación de voz.")
    srt = c / "voz.srt"
    if not srt.exists() or srt.stat().st_size == 0 or srt.stat().st_mtime < voz.stat().st_mtime:
        log("Transcribiendo la voz (la primera vez baja el modelo, ~500 MB)...")
        codigo, out = correr([python_cmd(), str(SCRIPTS / "transcribir.py"), str(voz)], log=log)
        if codigo != 0:
            raise Falla("Falló la transcripción.\n" + out[-800:])
    codigo, out = correr([python_cmd(), str(SCRIPTS / "srt_a_marcas.py"), str(c / "voz.srt"),
                          "--min-seg", "0", "--salida", str(c / "marcas.txt")], log=log)
    if codigo != 0:
        raise Falla("No pude sacar las marcas.\n" + out[-800:])


ARCHIVOS_PASO = {  # lo que produce cada paso; "Reiniciar paso" lo guarda aparte (no se borra nada)
    "investigacion": ["investigacion*.md"],
    "guion": ["guion.md", "guion_ia.md", "guion_edicion*.html", "guion_meta.json", "guion_previo.md", "revision_guion.md"],
    "voz": ["voz.srt", "marcas.txt"],
    "material": ["asignacion.txt"],
    "editor": ["edicion.json"],
    "video": ["short.mp4"],
}


def reiniciar_paso(c, paso):
    if paso not in ARCHIVOS_PASO:
        raise Falla("Paso inválido.")
    destino = c / ".anterior" / f"{time.strftime('%Y%m%d-%H%M%S')}-{paso}"
    movidos = 0
    for patron in ARCHIVOS_PASO[paso]:
        for f in c.glob(patron):
            destino.mkdir(parents=True, exist_ok=True)
            f.rename(destino / f.name)
            movidos += 1
    return {"ok": True, "movidos": movidos}


def tramos_que_quedan(quitar, total):
    """[[ini, fin], ...] a quitar -> los tramos que quedan, en orden y sin solaparse."""
    quedan, t = [], 0.0
    for a, b in sorted((max(0.0, float(a)), min(total, float(b))) for a, b in quitar):
        if a > t + 0.01:
            quedan.append((t, a))
        t = max(t, b)
    if total > t + 0.01:
        quedan.append((t, total))
    return quedan


def cortar_voz(c, d):
    """Saca de la voz los tramos marcados en "Tu grabación". La primera vez guarda la original
    (voz_original.*) para poder volver. Después hay que transcribir de nuevo."""
    voz = voz_de(c)
    if not voz:
        raise Falla("No hay grabación.")
    original = next((f for f in c.iterdir() if f.stem == "voz_original"), None)

    def soltar(f):  # Windows no deja borrar mientras el navegador todavía la está leyendo
        for _ in range(20):
            try:
                return f.unlink()
            except PermissionError:
                time.sleep(0.25)
        raise Falla("La grabación está en uso. Pausala y probá de nuevo.")
    if d.get("restaurar"):
        if not original:
            raise Falla("No hay original guardada.")
        soltar(voz)
        shutil.copy2(original, c / f"voz{original.suffix}")
    else:
        _, out = correr([ffmpeg_bin(), "-i", str(voz)])
        m = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", out)
        total = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
        quedan = tramos_que_quedan(d.get("quitar") or [], total)
        if not quedan:
            raise Falla("No podés cortar toda la grabación.")
        if not original:
            shutil.copy2(voz, c / f"voz_original{voz.suffix}")
        grafo = ";".join(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[a{i}]" for i, (a, b) in enumerate(quedan))
        grafo += ";" + "".join(f"[a{i}]" for i in range(len(quedan))) + f"concat=n={len(quedan)}:v=0:a=1[out]"
        nueva = c / ".voz_cortada.wav"  # wav: cortar varias veces no pierde calidad
        codigo, out = correr([ffmpeg_bin(), "-y", "-i", str(voz), "-filter_complex", grafo, "-map", "[out]", str(nueva)])
        if codigo != 0:
            raise Falla("No se pudo cortar.\n" + out[-600:])
        soltar(voz)
        nueva.rename(c / "voz.wav")
    for derivado in ("voz.srt", "marcas.txt"):  # la transcripción vieja ya no coincide
        (c / derivado).unlink(missing_ok=True)
    return {"ok": True}


def tarea_asignar(c, log):
    if not (c / "marcas.txt").exists():
        tarea_transcribir(c, log)
    if not material_de(c):
        raise Falla("No hay fotos ni videos en el material.")
    describir_videos(c, log)
    material = material_de(c)
    lista = "\n".join(
        f"- {m['nombre']} ({m['tipo']})" + (f" -> imagen: {m['mini']}" if m["mini"] else " (sin imagen)")
        + (f"\n  Lo que se ve y escucha en el video completo: {' '.join(m['descripcion'].split())}"
           if m["descripcion"] else "")
        for m in material)
    quien = redactor()
    if quien == "claude":
        como_ver = ("Estás en la carpeta del episodio. Antes de asignar, abrí cada imagen de la lista con la "
                    "herramienta Read (de los videos, el fotograma indicado): la asignación depende de lo que muestra.")
    else:
        como_ver = ("Te adjunto una imagen por archivo, en el mismo orden de la lista (de los videos, "
                    "un fotograma). Miralas todas antes de asignar.")
    prompt = plantilla("asignacion", COMO_VER=como_ver, MATERIAL=lista, GUION=guion_de(c),
                       MARCAS=leer(c / "marcas.txt"))
    if quien == "claude":
        texto = claude(prompt, c, log, herramientas="Read")
    else:
        imagenes = [c / m["mini"] for m in material if m["mini"]]
        texto = codex(prompt, c, log, buscar=False, imagenes=imagenes)
    lineas = [l.strip() for l in texto.splitlines() if re.match(r"^\s*\[\d", l)]
    if not lineas:
        raise Falla("Claude no devolvió una asignación válida.\n" + texto[-600:])
    escribir(c / "asignacion.txt", "\n".join(lineas) + "\n")


def edicion_de(c):
    """Cortes del editor (edicion.json), si son más nuevos que la asignación."""
    """Lo del editor. "vigente" = sus cortes son más nuevos que la asignación; las capas valen siempre."""
    e, a = c / "edicion.json", c / "asignacion.txt"
    if not e.exists():
        return None
    try:
        d = json.loads(leer(e))
    except ValueError:
        return None
    d["vigente"] = bool(d.get("segmentos")) and not (a.exists() and a.stat().st_mtime > e.stat().st_mtime)
    return d


def preparar_desde_edicion(c, edicion, log):
    """Arma imagenes/ con cada corte en su segundo y su encuadre."""
    segmentos = edicion["segmentos"]
    destino = c / "imagenes"
    shutil.rmtree(destino, ignore_errors=True)
    destino.mkdir()
    encuadres = {}
    for s in segmentos:
        origen = c / "material" / Path(s["archivo"]).name
        if not origen.is_file():
            log(f"(falta {origen.name})")
            continue
        nombre = f"{float(s['t']):.2f}{origen.suffix.lower()}"
        shutil.copy2(origen, destino / nombre)
        encuadres[nombre] = {"modo": s.get("modo", "recorte"), "crop": s.get("crop"), "mov": s.get("mov")}
    escribir(destino / "encuadre.json", json.dumps(encuadres, indent=2))


def escribir_capas(c, capas):
    """imagenes/capas.json con rutas completas: videos encima, audios extra y textos ya dibujados."""
    destino = c / "imagenes"
    salida = {"videos": [], "audios": [], "textos": []}
    for v in capas.get("videos", []):
        f = c / "material" / Path(v["archivo"]).name
        if f.is_file():
            salida["videos"].append({**v, "archivo": str(f)})
    for a in capas.get("audios", []):
        f = c / "audios" / Path(a["archivo"]).name
        if f.is_file():
            salida["audios"].append({**a, "archivo": str(f)})
    for x in capas.get("textos", []):
        f = c / "textos_png" / f"{Path(str(x['id'])).name}.png"
        if f.is_file():
            salida["textos"].append({"archivo": str(f), "ini": x["ini"], "fin": x["fin"]})
    if (capas.get("subtitulos") or {}).get("activo"):
        for n, s in enumerate(subtitulos_de(c)):
            f = c / "textos_png" / f"sub_{n}.png"
            ini, fin = (segundos_srt(x) for x in s["tiempo"].split("-->"))
            if f.is_file():
                salida["textos"].append({"archivo": str(f), "ini": ini, "fin": fin})
    escribir(destino / "capas.json", json.dumps(salida, indent=2))


def segundos_srt(x):
    h, m, s = x.strip().replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def subtitulos_de(c):
    salida = []
    for bloque in re.split(r"\n\s*\n", leer(c / "voz.srt").strip()):
        lineas = bloque.strip().splitlines()
        for i, l in enumerate(lineas):
            if "-->" in l:
                salida.append({"tiempo": l.strip(), "texto": "\n".join(lineas[i + 1:]).strip()})
                break
    return salida


def guardar_subtitulos(c, items):
    """Reescribe voz.srt con los textos corregidos (los tiempos no cambian) y rehace las marcas."""
    if not items:  # una lista vacía borraría la transcripción
        raise Falla("No hay subtítulos para guardar.")
    escribir(c / "voz.srt", "".join(f"{n}\n{s['tiempo']}\n{s['texto'].strip()}\n\n" for n, s in enumerate(items, 1)))
    correr([python_cmd(), str(SCRIPTS / "srt_a_marcas.py"), str(c / "voz.srt"), "--min-seg", "0",
            "--salida", str(c / "marcas.txt")])  # una marca por subtítulo


def tarea_armar(c, log):
    voz = voz_de(c)
    if not voz or not ((c / "asignacion.txt").exists() or (edicion_de(c) or {}).get("vigente")):
        raise Falla("Falta la voz o la asignación.")
    log("Copiando el material a cada marca...")
    edicion = edicion_de(c)
    if edicion and edicion["vigente"]:
        preparar_desde_edicion(c, edicion, log)
    else:
        codigo, out = correr([python_cmd(), str(SCRIPTS / "asignar_material.py"),
                              str(c / "asignacion.txt")], log=log)
        if codigo != 0:
            raise Falla("Falló la asignación.\n" + out[-800:])
    escribir_capas(c, (edicion or {}).get("capas") or {})
    log("Armando el video (puede tardar un par de minutos)...")
    cmd = [python_cmd(), str(SCRIPTS / "armar_video.py"), "--audio", str(voz),
           "--imagenes", str(c / "imagenes"), "--salida", str(c / "short.mp4")]
    subs_propios = (((edicion or {}).get("capas") or {}).get("subtitulos") or {}).get("activo")
    if (c / "voz.srt").exists() and not subs_propios:  # con estilo propio ya van como capas
        cmd += ["--subs", str(c / "voz.srt")]
    codigo, out = correr(cmd, log=log)
    if codigo != 0:
        raise Falla("Falló el armado del video.\n" + out[-800:])


def tarea_textos(c, log):
    guion = guion_de(c)
    if not guion.strip():
        raise Falla("Falta el guion.")
    instr = re.sub(r"GUION:.*$", "", sin_numerales(leer(PROMPTS / "03_publicacion.md")),
                   flags=re.S).strip()
    prompt = f"""{instr}

Español rioplatense, voseo. Nunca inventes datos, cifras ni citas: solo lo que está en el guion.
Texto plano, listo para pegar en Instagram, YouTube y X: sin markdown (nada de **, [texto](link) ni #títulos); los links van pegados tal cual.
Respondé SOLO con estas secciones, cada una con su título exacto:
### Caption IG
### Título YouTube
### Descripción YouTube
### Post X
### Recordatorio
(En Recordatorio poné solo lo del punto 4, o "Nada." si no aplica.)

GUION:
{guion}"""
    creditos = sorted({x["fuente"] for x in creditos_de(c).values() if x.get("fuente")})
    if creditos:
        prompt += "\n\nCRÉDITOS DEL MATERIAL (van en la descripción de YouTube): " + ", ".join(creditos)
    texto = claude(prompt, c, log) if redactor() == "claude" else codex(prompt, c, log, buscar=False)
    escribir(c / "textos.md", texto.strip() + "\n")


# ------------------------------------------------------------------ buscar material en la web
def creditos_de(c):
    try:
        return json.loads(leer(c / "material" / "creditos.json") or "{}")
    except ValueError:
        return {}


def bajar_foto(url, destino_sin_ext):
    import urllib.request
    pedido = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(pedido, timeout=25) as r:
        tipo = r.headers.get("Content-Type", "")
        datos = r.read(15_000_000 + 1)
    ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}.get(tipo.split(";")[0].strip())
    if not ext or len(datos) > 15_000_000:
        raise Falla(f"no es una imagen utilizable ({tipo or 'sin tipo'})")
    destino = destino_sin_ext.with_suffix(ext)
    destino.write_bytes(datos)
    return destino


def bajar_video(url, inicio, destino_sin_ext, largo=10):
    """Baja un tramo de `largo` s desde `inicio` (o el video entero si inicio es None), en mp4 (yt-dlp)."""
    ff = ffmpeg_bin()
    tramo = ["--download-sections", f"*{inicio:.0f}-{inicio + largo:.0f}"] if inicio is not None \
        else ["--max-filesize", "300M"]
    cmd = [python_cmd(), "-m", "yt_dlp", url, "--no-playlist", "--quiet", "--no-warnings", *tramo,
           "-f", "mp4/bv*+ba/b", "--merge-output-format", "mp4", "-o", str(destino_sin_ext) + ".%(ext)s"]
    if ff and ff != "ffmpeg":
        cmd += ["--ffmpeg-location", ff]
    codigo, out = correr(cmd)
    bajados = [f for f in destino_sin_ext.parent.glob(destino_sin_ext.name + ".*") if f.suffix.lower() in VIDEOS]
    if codigo != 0 or not bajados:
        raise Falla(out.strip().splitlines()[-1] if out.strip() else "no se pudo bajar")
    return bajados[0]


def buscar_youtube(consulta, cuantos, vistos=()):
    """Los primeros `cuantos` videos de YouTube para la consulta (ni muy cortos ni transmisiones de horas).
    Devuelve [(url, duración, canal)]."""
    codigo, out = correr([python_cmd(), "-m", "yt_dlp", f"ytsearch{cuantos * 3}:{consulta}", "--flat-playlist",
                          "--quiet", "--no-warnings", "--print", "%(url)s|%(duration)s|%(channel)s"])
    salida = []
    for l in out.splitlines():
        partes = l.strip().split("|")
        if len(partes) < 3 or not partes[0].startswith("http") or partes[0] in vistos:
            continue
        try:
            dur = float(partes[1])
        except ValueError:
            continue
        if 20 <= dur <= 1800:
            salida.append((partes[0], dur, partes[2]))
        if len(salida) >= cuantos:
            break
    return salida


def tarea_buscar(c, log):
    guion = guion_de(c).strip()
    if not guion:
        raise Falla("Primero hace falta el guion.")
    texto = codex(plantilla("buscar_material", EDITOR=bloque_editor(c), GUION=guion), c, log, buscar=True)
    pedidos = [[p.strip() for p in l.split("|")] for l in texto.splitlines()
               if re.match(r"^\s*(foto|video|buscar)\s*\|", l, re.I)]
    if not pedidos:
        raise Falla("ChatGPT no propuso material.\n" + texto[-600:])
    # las búsquedas se resuelven con yt-dlp (YouTube): cada una se convierte en 1 a 3 videos
    vistos, lista = set(), []
    for p in pedidos:
        if p[0].lower() != "buscar":
            lista.append(p)
            continue
        cuantos = min(3, max(1, int(re.sub(r"\D", "", p[2]) or 1))) if len(p) > 2 else 1
        log(f"Buscando en YouTube: {p[1][:60]}")
        for url, dur, canal in buscar_youtube(p[1], cuantos, vistos):
            vistos.add(url)
            lista.append(["video", url, str(min(15, dur * 0.15)), canal, "no", p[3] if len(p) > 3 else ""])
    pedidos = lista
    creditos, bajados = creditos_de(c), 0
    for n, p in enumerate(pedidos, 1):
        tipo, url = p[0].lower(), p[1]
        nombre = c / "material" / f"web_{time.strftime('%H%M%S')}_{n:02d}"
        try:
            if tipo == "foto":
                archivo = bajar_foto(url, nombre)
                fuente, segura, para = (p[2:5] + ["", "", ""])[:3]
            else:
                inicio = float(re.sub(r"[^\d.]", "", p[2]) or 0) if len(p) > 2 else 0
                archivo = bajar_video(url, inicio, nombre)
                fuente, segura, para = (p[3:6] + ["", "", ""])[:3]
            creditos[archivo.name] = {"url": url, "fuente": fuente, "segura": segura, "para": para}
            bajados += 1
            log(f"✓ {archivo.name} · {fuente}")
        except Exception as e:  # una URL rota no frena al resto
            log(f"✗ {tipo} {url[:70]}: {str(e)[:120]}")
    escribir(c / "material" / "creditos.json", json.dumps(creditos, ensure_ascii=False, indent=2))
    if not bajados:
        raise Falla("No se pudo bajar ningún archivo.")
    log(f"Bajé {bajados} de {len(pedidos)}.")


def tarea_link(c, log, datos):
    """Un link pegado a mano: foto directa o video de cualquier sitio que soporte yt-dlp."""
    url = (datos.get("url") or "").strip()
    if not re.match(r"https?://", url):
        raise Falla("Pegá un link que empiece con http.")
    desde = datos.get("desde")
    nombre = c / "material" / f"link_{time.strftime('%H%M%S')}"
    log("Bajando...")
    if re.search(r"\.(jpe?g|png|webp)(\?|$)", url, re.I):
        archivo = bajar_foto(url, nombre)
    else:
        archivo = bajar_video(url, float(desde) if desde not in (None, "") else None, nombre, largo=20)
    creditos = creditos_de(c)
    creditos[archivo.name] = {"url": url, "fuente": urllib.parse.urlparse(url).netloc.removeprefix("www.")}
    escribir(c / "material" / "creditos.json", json.dumps(creditos, ensure_ascii=False, indent=2))
    log(f"✓ {archivo.name}")


# ------------------------------------------------------------------ editar con Claude (tu cuenta, por Claude Code CLI)


MOVIMIENTOS = ("zoom_in", "zoom_out", "pan_der", "pan_izq", "pan_arriba", "pan_abajo")


def dims_de(f):
    """Ancho y alto de una foto o video (leído de ffmpeg)."""
    _, out = correr([ffmpeg_bin(), "-i", str(f)])
    m = re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", out)
    return (int(m.group(1)), int(m.group(2))) if m else None


def recorte_con_foco(f, foco):
    """El recuadro 9:16 más grande, corrido hacia el foco que eligió Claude."""
    d = dims_de(f)
    if not d:
        return None
    w, h = d
    cw, ch = w, w * 16 / 9
    if ch > h:
        cw, ch = h * 9 / 16, h
    fx = {"izquierda": 0, "derecha": 1}.get(foco, 0.5)
    fy = {"arriba": 0, "abajo": 1}.get(foco, 0.5)
    return {"x": (w - cw) * fx / w, "y": (h - ch) * fy / h, "w": cw / w, "h": ch / h}


def estilo_texto_base():
    """Estilo principal del graph de StreamDash, agrandado para el short (igual que la interfaz)."""
    e = {"fuente": "FixtureItalic-CondensedBlack", "tamano": 58, "color": "#ffffff", "negrita": True, "cursiva": False,
         "mayusculas": True, "degrade": True, "degrade_tipo": "vertical", "degrade_colores": ["#ffffff", "#ffffff", "#9e9e9e"],
         "sombra": True, "posicion": "abajo-izq", "margen_x": 32, "margen_y": 36}
    e.update({k: v for k, v in (estilos_streamdash().get("principal") or {}).items() if k not in ("titulo", "archivo_fuente")})
    e["tamano"] = round(e["tamano"] * 1.6)
    e.update(x=0.08, y=0.12, posicion="arriba-izq", margen_x=60, margen_y=230)  # arriba: abajo van los subtítulos
    return e


def json_con(texto, clave):
    """El primer objeto JSON del texto que tenga esa clave (la IA a veces escribe algo antes o después)."""
    dec = json.JSONDecoder()
    for m in re.finditer(r"\{", texto):
        try:
            obj, _ = dec.raw_decode(texto, m.start())
        except ValueError:
            continue
        if isinstance(obj, dict) and clave in obj:
            return obj
    return None


def tarea_editar(c, log):
    marcas = marcas_de(c)
    if not marcas:
        raise Falla("Primero transcribí la voz (pestaña Asignación).")
    material = material_de(c)
    if not material:
        raise Falla("No hay material.")
    lista = "\n".join(
        f"- {m['nombre']} ({m['tipo']}; fuente: {m['fuente'] or 'sin dato'})"
        + (f" -> mirala en {m['mini']}" if m["mini"] else "")
        + (f"\n  Lo que se ve en el video: {' '.join(m['descripcion'].split())}" if m["descripcion"] else "")
        for m in material)
    prompt = plantilla("editar", EDITOR=bloque_editor(c), GUION=guion_de(c),
                       MARCAS="\n".join(f"[{m['t']:.2f}] {m['texto']}" for m in marcas), MATERIAL=lista)
    # tu Claude si la terminal tiene sesión (pide plan Pro); si no, Claude gratis por Antigravity
    refrescar_herramientas()
    if claude_conectado():
        texto = claude(prompt, c, log, herramientas="Read")
    else:
        texto = gemini("Sos el editor de video.", prompt, c, log, modelo="claude-sonnet-4-6")
    plan = json_con(texto, "segmentos")
    if not plan:
        escribir(c / ".respuesta_editar.txt", texto)
        raise Falla("Claude no devolvió una edición válida.\n" + texto[-600:])
    segmentos, hechas, videos = [], 0, []
    for s in plan.get("segmentos", []):
        archivo = str(s.get("archivo", "")).strip()
        if archivo.upper().startswith("IA:"):
            if hechas >= 6:
                continue
            log(f"ChatGPT generando imagen: {archivo[3:70].strip()}...")
            codigo, out = correr([python_cmd(), str(SCRIPTS / "generar_imagen.py"), str(c), archivo[3:].strip()])
            if codigo != 0:
                log("(no se pudo generar esa imagen)")
                continue
            archivo, hechas = Path(out.strip().splitlines()[-1]).name, hechas + 1
            if s.get("animar"):  # video con IA en esta PC (Wan2GP); si falla, queda el pedido para Gemini
                log(f"Animando {archivo} en tu PC (varios minutos)...")
                codigo, out = correr([python_cmd(), str(SCRIPTS / "animar_imagen.py"),
                                      str(c / "material" / archivo), s["animar"]])
                if codigo == 0:
                    archivo = Path(out.strip().splitlines()[-1]).name
                else:
                    videos.append(f"## {archivo} (segundo {float(s.get('t', 0)):.1f})\nSubí material/{archivo} a Gemini "
                                  f"y pedile: Animá esta imagen como video vertical 9:16 de 5 segundos. {s['animar']}\n")
        f = c / "material" / Path(archivo).name
        if not f.is_file():
            continue
        modo = s.get("modo") if s.get("modo") in ("blur", "centrado", "recorte") else "recorte"
        segmentos.append({"t": float(s.get("t", 0)), "archivo": f.name, "modo": modo,
                          "crop": recorte_con_foco(f, s.get("foco")) if modo == "recorte" else None,
                          "mov": s.get("mov") if s.get("mov") in MOVIMIENTOS else None})
    if not segmentos:
        raise Falla("Claude no armó ningún corte con el material.\n" + texto[-600:])
    segmentos.sort(key=lambda s: s["t"])
    segmentos[0]["t"] = 0
    capas = (edicion_de(c) or {}).get("capas") or {}
    nuevos, vistos = [], set()
    for x in sorted((x for x in plan.get("textos", []) if x.get("texto")), key=lambda x: float(x["ini"])):
        if x["texto"].strip().upper() in vistos:  # el mismo texto dos veces, no
            continue
        vistos.add(x["texto"].strip().upper())
        ini, fin = float(x["ini"]), float(x["fin"])
        if nuevos and ini < nuevos[-1]["fin"]:  # que no se pisen: el anterior termina donde empieza este
            nuevos[-1]["fin"] = max(nuevos[-1]["ini"] + 0.5, ini)
        nuevos.append({"id": f"ia{len(nuevos)}_{int(time.time())}", "ia": True, "texto": x["texto"], "ini": ini,
                       "fin": fin, "estilo": estilo_texto_base()})
    capas["textos"] = [x for x in capas.get("textos", []) if not x.get("ia")] + nuevos
    escribir(c / "edicion.json", json.dumps({"segmentos": segmentos, "capas": capas}, ensure_ascii=False, indent=2))
    log(f"{len(segmentos)} cortes, {hechas} imágenes generadas, {len(capas['textos'])} textos.")
    if videos:
        escribir(c / "videos_gemini.md", "# Videos para hacer en Gemini (gemini.google.com)\n"
                 "Bajá cada video a material/ y cambialo en el Editor por su imagen.\n\n" + "\n".join(videos))
        log(f"{len(videos)} videos para Gemini: abrí videos_gemini.md en la carpeta del video.")


def tarea_pedir(c, log):
    """Deja la edición pendiente para tu Claude (la app de escritorio): la toma con /pendientes."""
    if not marcas_de(c) or not material_de(c):
        raise Falla("Primero la voz transcripta y el material.")
    escribir(c / ".pedido_claude", time.strftime("%Y-%m-%d %H:%M"))
    log("Pedido guardado. Tu Claude lo hace en la próxima revisión (o escribile /pendientes).")


FUNCIONES = {"investigar": tarea_investigar, "guion": tarea_guion,
             "transcribir": tarea_transcribir, "asignar": tarea_asignar,
             "armar": tarea_armar, "textos": tarea_textos,
             "revisar": tarea_revisar, "describir": tarea_describir, "ortografia": tarea_ortografia,
             "completa": tarea_completa, "buscar": tarea_buscar, "editar": tarea_editar, "pedir": tarea_pedir}


def lanzar_tarea(slug, nombre, datos=None):
    c = carpeta(slug)
    with CANDADO:
        actual = TAREAS.get(c.name)
        if actual and actual["estado"] == "corriendo":
            raise Falla("Ya hay una tarea corriendo en este short.")
        estado = {"tarea": nombre, "estado": "corriendo", "log": [], "inicio": time.time()}
        TAREAS[c.name] = estado
    if nombre == "investigar":
        funcion = lambda c, log: tarea_investigar(c, log, estado, datos or {})  # noqa: E731
    elif nombre == "guion":
        funcion = lambda c, log: tarea_guion(c, log, datos)  # noqa: E731
    else:
        funcion = FUNCIONES[nombre]

    def log(linea):
        estado["log"] = (estado["log"] + [linea])[-40:]

    def trabajo():
        try:
            funcion(c, log)
            estado["estado"] = "ok"
            log("Listo.")
        except Falla as e:
            estado["estado"] = "error"
            log(str(e))
        except Exception as e:  # que nunca quede colgada en "corriendo"
            estado["estado"] = "error"
            log(f"Error inesperado: {e}")
        estado["fin"] = time.time()

    threading.Thread(target=trabajo, daemon=True).start()


# ------------------------------------------------------------------ servidor
ULTIMO_PING = [time.time()]


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    # --- respuestas
    def _json(self, data, codigo=200):
        cuerpo = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)

    def _error(self, texto, codigo=400):
        self.close_connection = True  # si no se leyó el cuerpo del pedido, no reusar la conexión
        self._json({"error": texto}, codigo)

    def _archivo(self, path):
        if not path.is_file():
            return self._error("no existe", 404)
        tam = path.stat().st_size
        tipo = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        ini, fin = 0, tam - 1
        rango = self.headers.get("Range")
        m = re.match(r"bytes=(\d*)-(\d*)", rango or "")
        if m and tam:
            if m.group(1):
                ini = int(m.group(1))
                fin = int(m.group(2)) if m.group(2) else tam - 1
            else:
                ini = max(0, tam - int(m.group(2)))
            fin = min(fin, tam - 1)
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {ini}-{fin}/{tam}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(fin - ini + 1))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        with path.open("rb") as f:
            f.seek(ini)
            falta = fin - ini + 1
            try:
                while falta > 0:
                    trozo = f.read(min(1 << 16, falta))
                    if not trozo:
                        break
                    self.wfile.write(trozo)
                    falta -= len(trozo)
            except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
                pass

    def _cuerpo_json(self):
        if not hasattr(self, "_cuerpo"):  # se lee una sola vez
            largo = int(self.headers.get("Content-Length") or 0)
            self._cuerpo = json.loads(self.rfile.read(largo) or b"{}") if largo else {}
        return self._cuerpo

    def _host_valido(self):
        """Evita que una página web use el panel a escondidas (DNS rebinding)."""
        host = (self.headers.get("Host") or "").split(":")[0]
        return host in ("127.0.0.1", "localhost")

    # --- GET
    def do_GET(self):
        if not self._host_valido():
            return self._error("prohibido", 403)
        url = urllib.parse.urlparse(self.path)
        q = dict(urllib.parse.parse_qsl(url.query))
        ruta = urllib.parse.unquote(url.path)
        try:
            if ruta in ("/", "/index.html"):
                return self._archivo(WEB / "index.html")
            if ruta == "/api/ping":
                ULTIMO_PING[0] = time.time()
                return self._json({"ok": True, "v": (WEB / "index.html").stat().st_mtime})
            if ruta == "/api/herramientas":
                if q.get("refrescar") or not HERRAMIENTAS:
                    refrescar_herramientas()
                return self._json(HERRAMIENTAS)
            if ruta == "/api/episodios":
                return self._json(listar_episodios())
            if ruta == "/api/prompts":
                return self._json(prompts_editables())
            if ruta == "/api/recorte":
                return self._json({"carpeta": str(RECORTE), "archivos": exportados_recorte()})
            if ruta.startswith("/recorte-mini/"):
                return self._archivo(MINIS_RECORTE / (Path(ruta).name))
            if ruta.startswith("/recorte/"):
                return self._archivo(RECORTE / Path(ruta).name)
            if ruta == "/api/ep":
                return self._json(datos_episodio(q.get("e", "")))
            if ruta.startswith("/ep/"):
                _, _, slug, resto = ruta.split("/", 3)
                c = carpeta(slug)
                p = (c / resto).resolve()
                if c not in p.parents:
                    return self._error("ruta inválida", 403)
                return self._archivo(p)
            if ruta.startswith("/web/"):
                p = (WEB / ruta[5:]).resolve()
                if WEB.resolve() not in p.parents:
                    return self._error("ruta inválida", 403)
                return self._archivo(p)
            self._error("no existe", 404)
        except FileNotFoundError:
            self._error("No encontré ese short.", 404)
        except Exception as e:
            self._error(str(e), 500)

    # --- POST
    def do_POST(self):
        # Solo pedidos que un navegador no puede mandar desde otra página sin permiso (CORS):
        # JSON o subida con X-Nombre. Así ninguna web puede borrar material ni lanzar tareas.
        tipo = self.headers.get("Content-Type", "")
        if not self._host_valido() or not (tipo.startswith("application/json") or self.headers.get("X-Nombre")):
            return self._error("prohibido", 403)
        self.__dict__.pop("_cuerpo", None)  # la conexión se reusa: el cuerpo es de este pedido, no del anterior
        if tipo.startswith("application/json"):
            # leer siempre el cuerpo: si queda sin leer, ensucia el pedido siguiente de la misma conexión
            # (el navegador reusa la conexión y el servidor veía cosas como "{}GET")
            try:
                self._cuerpo_json()
            except ValueError:
                return self._error("JSON inválido")
        url = urllib.parse.urlparse(self.path)
        q = dict(urllib.parse.parse_qsl(url.query))
        ruta = url.path
        try:
            if ruta == "/api/prompts":
                d = self._cuerpo_json()
                guardar_prompt(d.get("id"), None if d.get("restaurar") else d.get("texto", ""))
                return self._json({"ok": True, "prompts": prompts_editables()})

            if ruta == "/api/nuevo":
                tema = (self._cuerpo_json().get("tema") or "").strip()
                if not tema:
                    return self._error("Escribí el tema.")
                return self._json({"slug": nuevo_episodio(tema)})

            c = carpeta(q.get("e", ""))

            if ruta == "/api/guardar":
                d = self._cuerpo_json()
                archivos = {"tema": "tema.txt", "eje": "eje.txt", "guion": "guion.md",
                            "textos": "textos.md", "guion_edicion": "guion_edicion.html",
                            **{f"investigacion_{ia}": archivo for ia, (_, archivo) in IAS.items()}}
                if d.get("campo") not in archivos:
                    return self._error("campo inválido")
                escribir(c / archivos[d["campo"]], d.get("texto", ""))
                return self._json({"ok": True})

            if ruta == "/api/fuentes":
                d = self._cuerpo_json()
                if d.get("accion") == "agregar":
                    agregar_fuente(c, d.get("texto", ""))
                elif d.get("accion") == "borrar":
                    borrar_fuente(c, int(d.get("i", -1)))
                return self._json({"ok": True, "fuentes": fuentes_de(c)})

            if ruta == "/api/meta":
                d, meta = self._cuerpo_json(), meta_de(c)
                if d.get("accion") == "verificar":
                    item = meta.get("verificar", [])[int(d["i"])]
                    item["ok"] = not item["ok"]
                elif d.get("accion") == "tipo":
                    meta["tipo"] = meta["tipo_editor"] = d.get("tipo", "")
                elif d.get("accion") == "prefiero_mi_guion":  # vuelve a la versión de antes de la reescritura
                    escribir(c / "guion.md", leer(c / "guion_previo.md"))
                    escribir(c / "guion_edicion.html", leer(c / "guion_edicion_previo.html"))
                    meta.pop("revision_pendiente", None)
                    meta.pop("notas_revision", None)
                elif d.get("accion") == "aceptar_revision":
                    meta.pop("revision_pendiente", None)
                escribir_meta(c, meta)
                return self._json({"ok": True, "meta": meta})

            if ruta == "/api/importar":
                d = self._cuerpo_json()
                origen = d.get("ruta") or str(RECORTE / Path(d.get("recorte", "")).name)
                return self._json({"ok": True, "nombre": importar_material(c, origen)})

            if ruta == "/api/edicion":
                d = self._cuerpo_json()
                if d.get("reset"):
                    (c / "edicion.json").unlink(missing_ok=True)
                else:
                    escribir(c / "edicion.json", json.dumps(
                        {"segmentos": d.get("segmentos", []), "capas": d.get("capas", {})}, indent=2))
                return self._json({"ok": True})

            if ruta == "/api/texto_png":  # el texto ya dibujado por la interfaz (igual que se ve)
                import base64
                d = self._cuerpo_json()
                datos = base64.b64decode(d.get("png", "").split(",", 1)[-1])
                destino = c / "textos_png" / f"{Path(str(d.get('id'))).name}.png"
                destino.parent.mkdir(exist_ok=True)
                destino.write_bytes(datos)
                return self._json({"ok": True})

            if ruta == "/api/subtitulos":
                guardar_subtitulos(c, self._cuerpo_json().get("items", []))
                return self._json({"ok": True})

            if ruta == "/api/estilos_streamdash":
                return self._json(estilos_streamdash())

            if ruta == "/api/mis_estilos":
                d = self._cuerpo_json()
                archivo = WEB / "estilos.json"
                estilos = json.loads(leer(archivo) or "{}")
                if d.get("nombre"):
                    if d.get("borrar"):
                        estilos.pop(d["nombre"], None)
                    else:
                        estilos[d["nombre"]] = d.get("estilo", {})
                    escribir(archivo, json.dumps(estilos, ensure_ascii=False, indent=2))
                return self._json(estilos)

            if ruta == "/api/asignacion":
                escribir_asignacion(c, self._cuerpo_json().get("filas", []))
                return self._json({"ok": True})

            if ruta == "/api/subir":
                return self._subir(c, q.get("tipo"))

            if ruta == "/api/borrar":
                f = c / "material" / Path(q.get("nombre", "")).name
                if f.is_file():
                    f.unlink()
                (c / ".mini" / (f.name + ".jpg")).unlink(missing_ok=True)
                return self._json({"ok": True})

            if ruta == "/api/elegir_voz":
                f = c / Path(q.get("nombre", "")).name
                if f.is_file() and f.suffix.lower() in AUDIOS:
                    self._poner_voz(c, f)
                return self._json({"ok": True})

            if ruta == "/api/reiniciar":
                return self._json(reiniciar_paso(c, self._cuerpo_json().get("paso")))

            if ruta == "/api/cortar_voz":
                return self._json(cortar_voz(c, self._cuerpo_json()))

            if ruta == "/api/link":
                log = []
                tarea_link(c, log.append, self._cuerpo_json())
                return self._json({"ok": True, "log": log})

            if ruta == "/api/tarea":
                d = self._cuerpo_json()
                nombre = d.get("tarea")
                if nombre not in FUNCIONES:
                    return self._error("tarea inválida")
                lanzar_tarea(c.name, nombre, d)
                return self._json({"ok": True})

            if ruta == "/api/abrir":
                destino = c / "short.mp4" if q.get("que") == "video" else c
                os.startfile(str(destino if destino.exists() else c))
                return self._json({"ok": True})

            self._error("no existe", 404)
        except Falla as e:
            self._error(str(e))
        except FileNotFoundError:
            self._error("No encontré ese short.", 404)
        except Exception as e:
            self._error(str(e), 500)

    def _poner_voz(self, c, f):
        """Deja f como voz.<ext>; si cambia la voz, la transcripción vieja no sirve más."""
        for vieja in c.iterdir():
            if vieja.is_file() and vieja.stem == "voz" and vieja != f:
                vieja.unlink()
        for derivado in ("marcas.txt",):
            (c / derivado).unlink(missing_ok=True)
        f.rename(c / f"voz{f.suffix.lower()}")

    def _subir(self, c, tipo):
        nombre = Path(urllib.parse.unquote(self.headers.get("X-Nombre", ""))).name
        ext = Path(nombre).suffix.lower()
        largo = int(self.headers.get("Content-Length") or 0)
        if tipo == "voz" and ext not in AUDIOS:
            return self._error("La voz tiene que ser mp3, m4a, wav, ogg, opus o aac.")
        if tipo == "material" and ext not in IMAGENES | VIDEOS:
            return self._error(f"{nombre}: solo fotos (png, jpg, webp) o videos (mp4, mov, webm).")
        if tipo == "audio" and ext not in AUDIOS:
            return self._error("El audio tiene que ser mp3, m4a, wav, ogg, opus o aac.")
        if tipo not in ("voz", "material", "audio") or not nombre:
            return self._error("subida inválida")
        destino = {"voz": c / f".subiendo{ext}", "audio": c / "audios" / nombre}.get(tipo, c / "material" / nombre)
        destino.parent.mkdir(exist_ok=True)
        with destino.open("wb") as f:
            falta = largo
            while falta > 0:
                trozo = self.rfile.read(min(1 << 20, falta))
                if not trozo:
                    break
                f.write(trozo)
                falta -= len(trozo)
        if tipo == "voz":
            self._poner_voz(c, destino)
        return self._json({"ok": True})


# ------------------------------------------------------------------ arranque
def puerto_ocupado(puerto):
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", puerto)) == 0


def abrir_ventana(url):
    """Abre la interfaz como ventana propia (Edge modo app). Devuelve el proceso o None."""
    candidatos = [os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
                  os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
                  os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe")]
    perfil = Path(os.environ.get("LOCALAPPDATA", RAIZ)) / "JordyEstudio"
    for exe in candidatos:
        if os.path.isfile(exe):
            return subprocess.Popen([exe, f"--app={url}", f"--user-data-dir={perfil}",
                                     "--window-size=1180,820", "--no-first-run",
                                     "--no-default-browser-check"])
    webbrowser.open(url)
    return None


def main():
    global PUERTO
    if "--puerto" in sys.argv:  # para pruebas; El Recorte siempre habla con el 8430
        PUERTO = int(sys.argv[sys.argv.index("--puerto") + 1])
    url = f"http://127.0.0.1:{PUERTO}/"
    if puerto_ocupado(PUERTO):  # ya está abierto: solo muestro otra ventana
        abrir_ventana(url)
        return
    servidor = ThreadingHTTPServer(("127.0.0.1", PUERTO), Handler)
    servidor.daemon_threads = True
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    threading.Thread(target=refrescar_herramientas, daemon=True).start()

    if "--sin-ventana" in sys.argv:  # para probar desde otro navegador
        threading.Event().wait()
    if "--reinicio" not in sys.argv:  # al reiniciarse solo, la ventana ya está abierta
        abrir_ventana(url)
    # Vive mientras la ventana hace ping. Si cambia este archivo, se reinicia solo (sin cerrar la ventana).
    ULTIMO_PING[0], codigo = time.time(), Path(__file__).stat().st_mtime
    while time.time() - ULTIMO_PING[0] < 30 or any(t["estado"] == "corriendo" for t in TAREAS.values()):
        time.sleep(2)
        libre = not any(t["estado"] == "corriendo" for t in TAREAS.values())
        if libre and Path(__file__).stat().st_mtime != codigo:
            servidor.shutdown()
            servidor.server_close()
            args = [a for a in sys.argv[1:] if a != "--reinicio"]
            subprocess.Popen([sys.executable, str(Path(__file__)), *args, "--reinicio"], creationflags=SIN_VENTANA)
            return
    servidor.shutdown()


if __name__ == "__main__":
    main()
