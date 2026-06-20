# NBA Watchlist Automation

Pipeline que lee una watchlist de jugadores NBA (cargada vía Google Form), revisa
sus últimos partidos contra la API de la NBA, y notifica por mail cuando alguno
cumple un umbral (puntos, doble-doble, triple-doble). Corre solo, todos los días,
vía GitHub Actions — sin servidor propio.

## Arquitectura (5 pasos)

| Paso | Implementación |
|---|---|
| **Trigger** | GitHub Actions, cron diario (+ `workflow_dispatch` para correrlo a mano) |
| **Input** | Google Sheet "watchlist" (alimentado por un Google Form) + NBA API (`nba_api`) |
| **Procesamiento** | `rules.py` — evalúa si el partido cumple el umbral o es doble/triple-doble |
| **Output** | Fila nueva en el Sheet "Historial" + mail si corresponde |
| **Observabilidad** | Logging en cada corrida, columna de estado para idempotencia, mail de error si algo de la cadena falla |

## Equivalencia con N8N / Make

Esto resuelve el mismo problema que armarías con un workflow de bajo código,
solo que en Python:

| Concepto en N8N/Make | Acá |
|---|---|
| Schedule Trigger | Cron de GitHub Actions |
| Form/Webhook Trigger | Google Form → Sheet vinculado |
| HTTP Request node | `nba_client.py` |
| Google Sheets node (read/write) | `sheets_client.py` (gspread) |
| IF / Filter node | `rules.py` |
| Send Email node | `notifier.py` |
| Error Trigger | try/except en `main.py` + mail de error |

## Estructura

```
src/
├── config.py          # variables de entorno y defaults
├── sheets_client.py    # leer watchlist, leer/escribir historial
├── nba_client.py        # resolver jugador, traer sus últimos partidos
├── rules.py              # qué cuenta como "buen partido"
├── notifier.py            # envío de mail (SMTP)
└── main.py                  # orquesta todo
```

## Setup

### 1. Infraestructura (ya hecha si seguiste la guía)
- Google Form + Sheet vinculado (pestaña "Respuestas de formulario 1")
- Pestaña "Historial" en el mismo Sheet con headers:
  `Jugador | Fecha_partido | Game_ID | Puntos | Rebotes | Asistencias | Cumple_umbral | Fecha_procesado`
- Service account de Google Cloud con Sheets API habilitada, compartida como Editor en el Sheet
- App Password de Gmail para mandar los mails

### 2. GitHub Secrets

En el repo: Settings → Secrets and variables → Actions → New repository secret

| Secret | Valor |
|---|---|
| `SHEET_ID` | El ID del Sheet (parte de la URL entre `/d/` y `/edit`) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | El contenido completo del JSON de la service account, pegado tal cual |
| `GMAIL_ADDRESS` | El mail que manda las notificaciones |
| `GMAIL_APP_PASSWORD` | El app password de 16 caracteres |
| `NOTIFY_TO` | El mail que recibe las notificaciones (puede ser el mismo que `GMAIL_ADDRESS`) |

### 3. Probar local

```bash
pip install -r requirements.txt
cp .env.example .env   # completar con tus datos
python -m src.main
```

### 4. Correr en GitHub Actions

Una vez pusheado con los secrets cargados, andá a la pestaña **Actions** del repo
y corré el workflow manualmente (`workflow_dispatch`) para la primera prueba,
sin esperar al cron.

## Nota sobre la temporada

`NBA_SEASON` y `NBA_SEASON_TYPE` en `.env` controlan qué temporada/tipo de
partido trae `nba_api`. Como la temporada 2025-26 recién terminó, por default
apunta ahí en modo Regular Season — para testear con los partidos de Playoffs/Finals,
cambiar `NBA_SEASON_TYPE=Playoffs`.
