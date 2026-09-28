---
description: Hace las ediciones que Jordy pidió desde Estudio ("Pedir a mi Claude")
---
Buscá en `episodios/*/` las carpetas con el archivo `.pedido_claude` (ignorá las que tengan `.pedido_en_curso` de menos de 3 horas: ya la está haciendo otra ejecución).
Si no hay ninguna, respondé solo "Sin pendientes." y terminá.
Por cada una: creá `.pedido_en_curso`, hacé todos los pasos de `.claude/commands/editar.md` con esa carpeta y al final borrá `.pedido_claude` y `.pedido_en_curso`.
No termines el turno con procesos en segundo plano trabajando: esperalos en primer plano.
