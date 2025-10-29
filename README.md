# Extracción de tuplas (entidad, relación, objeto) desde documentos históricos

Este repositorio contiene un proyecto que procesa documentos históricos que se encuentran en formato Markdown ubicados en la carpeta `docs/`, los divide en chunks manejables y usa la API de Anthropic para extraer tuplas del tipo (entidad, relación, objeto) presentes en los textos.

## Flujo general

1. Coloca tus documentos históricos en `docs/` (formato `.md`).
2. La función `create_chunked_files.py` presente en el script `chunks.py` toma cada documento y lo divide en fragmentos  que respetan la ventana de contexto del modelo y aseguran una buena calidad de respuesta. Los chunks resultantes se escriben como archivos en la carpeta `chunks/`.
3. El script principal (`main.py`) crea mensajes por cada chunk y agrupa esas solicitudes en batches conforme al formato requerido por la API de Anthropic.
4. Los batches se envían a la API de Anthropic, que procesa cada chunk y devuelve las respuestas con las tuplas encontradas.
5. Las respuestas de la API se guardan en la carpeta `response/`.

## Estructura de carpetas

```
Desafio/
├── docs/                   # Documentos de entrada (.md)
├── chunks/                 # Chunks generados por chunks.py
├── response/               # Respuestas guardadas de la API de Anthropic
├── results.py              # Script para recuperar y streamear resultados de batches desde Anthropic
├── main.py                 # Orquestador: crea chunks, batches y envía a Anthropic
├── chunks.py               # Lógica para dividir documentos en chunks
├── batch.py                # Utilidades para crear Request / batches para la API
├── tokens.py               # Función auxiliar count_tokens (conteo de tokens)
├── requirements.txt / pyproject.toml
└── README.md
```

## Configuración

- Crea un archivo `.env` o exporta la variable de entorno `ANTHROPIC_API_KEY` con tu API key de Anthropic.
- Instala dependencias:

```bash
uv sync
```

## Uso

1. Coloca tus archivos en `docs/`.
2. Ajusta si hace falta el prompt en `prompt.md` (o `prompt_eeuu.md`) para controlar la instrucción que se dará al modelo sobre cómo extraer las tuplas.
3. Ejecuta el orquestador:

```bash
uv run main.py
```

El script realizará:
- División en chunks (guardados en `chunks/`).
- Creación de batches y envío a Anthropic.
- Guardado del identificador del batch en `message_batch_id_*.txt`.

## Formato de salida

- `chunks/`: archivos con nombres del tipo `original_chunk_1.md`, `original_chunk_2.md`, ...
- `message_batch_id_*.txt`: archivo(s) con los IDs de batch enviados (uno por línea).