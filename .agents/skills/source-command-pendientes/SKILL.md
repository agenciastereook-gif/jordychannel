---
name: "source-command-pendientes"
description: "Hace las ediciones que Jordy pidió desde Estudio (\"Pedir a mi Codex\")"
---

# source-command-pendientes

Use this skill when the user asks to run the migrated source command `pendientes`.

## Command Template

Buscá en `episodios/*/` las carpetas con el archivo `.pedido_claude`.
Si no hay ninguna, respondé solo "Sin pendientes." y terminá.
Por cada una, hacé todos los pasos de `.Codex/commands/editar.md` con esa carpeta.
