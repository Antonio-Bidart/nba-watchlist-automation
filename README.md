# NBA Watchlist Automation

Te avisa por mail cuando alguno de los jugadores que seguís tiene un partidazo.
Corre solo, todos los días, sin servidor propio.


## Qué hace

- Cargás jugadores a seguir desde un Google Form (con un umbral de puntos
  opcional para cada uno)
- Todos los días, un workflow revisa los últimos partidos de cada jugador
  contra la API pública de stats.nba.com
- Si alguno tuvo un buen partido (superó el umbral, o hizo doble-doble /
  triple-doble), te llega un mail
- Todo queda registrado en un Sheet de historial, para no repetir avisos del
  mismo partido dos veces

## Arquitectura

| Parte | Implementación |
|---|---|
| Disparador | GitHub Actions, cron diario (+ ejecución manual) |
| Entrada de datos | Google Sheet "watchlist" (alimentado por un Form) + API de la NBA |
| Lógica | `rules.py` — evalúa umbral, doble-doble, triple-doble |
| Salida | Fila nueva en el Sheet "Historial" + mail si corresponde |
| Manejo de errores | Logging por corrida, reintentos en la consulta a la API, mail aparte si algo de la cadena falla |

## Estructura
src/

├── config.py          # variables de entorno y defaults

├── sheets_client.py    # leer watchlist, leer/escribir historial

├── nba_client.py         # resolver jugador, traer sus últimos partidos

├── rules.py               # qué cuenta como "buen partido"

├── notifier.py             # envío de mail (SMTP)

└── main.py                  # orquesta todo

run.py                          # entrypoint simple para correrlo local

## Algunas decisiones técnicas

- **Idempotencia:** antes de notificar, el script chequea si ese partido
  específico ya está en el Historial (por jugador + ID de partido). Sin esto,
  cada corrida volvería a mandar el mismo aviso.
- **Reintentos:** la API de stats.nba.com a veces no responde bien desde
  runners en la nube (lo noté corriendo esto en GitHub Actions — local andaba
  perfecto, en Actions tiraba timeout). Le sumé reintentos con backoff y subí
  el timeout default.
- **Separación en módulos chicos:** cada archivo habla con un solo sistema
  externo (Sheets, NBA API, mail), así si algo falla es fácil saber dónde
  mirar.

## Correrlo vos mismo

1. Creá un Google Form con los campos "Nombre del jugador" y "Umbral de
   puntos", vinculalo a un Sheet
2. Agregá una pestaña "Historial" con columnas:
   `Jugador | Fecha_partido | Game_ID | Puntos | Rebotes | Asistencias | Cumple_umbral | Fecha_procesado`
3. Creá un proyecto en Google Cloud, habilitá la Sheets API, generá una
   cuenta de servicio y compartile el Sheet como Editor
4. Generá un App Password de Gmail para mandar los mails
5. Cargá los secrets en el repo (Settings → Secrets and variables → Actions):
   `SHEET_ID`, `GOOGLE_SERVICE_ACCOUNT_JSON`, `GMAIL_ADDRESS`,
   `GMAIL_APP_PASSWORD`, `NOTIFY_TO`

Para probar local:

```bash
pip install -r requirements.txt
cp .env.example .env   # completar con tus datos
python run.py
```

## Posibles mejoras

- Soportar Regular Season y Playoffs en la misma corrida, sin tener que
  cambiar el config a mano
- Notificación por Telegram además de mail
- Un dashboard simple para ver el historial sin entrar al Sheet
