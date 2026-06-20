import gspread
from src import config


def _open_sheet():
    gc = gspread.service_account_from_dict(config.SERVICE_ACCOUNT_INFO)
    return gc.open_by_key(config.SHEET_ID)


def get_watchlist():
    """Lee la pestaña de respuestas del Form. Devuelve lista de dicts {jugador, umbral}."""
    sh = _open_sheet()
    ws = sh.worksheet(config.WATCHLIST_TAB)
    rows = ws.get_all_records()
    watchlist = []
    for row in rows:
        jugador = (row.get("Nombre del jugador") or "").strip()
        if not jugador:
            continue
        umbral_raw = row.get("Umbral de puntos")
        umbral = int(umbral_raw) if str(umbral_raw).strip().isdigit() else None
        watchlist.append({"jugador": jugador, "umbral": umbral})
    return watchlist


def get_processed_game_ids():
    """Devuelve un set de tuplas (jugador, game_id) que ya están en el Historial."""
    sh = _open_sheet()
    ws = sh.worksheet(config.HISTORIAL_TAB)
    rows = ws.get_all_records(numericise_ignore=["all"])
    return {(str(r["Jugador"]).strip(), str(r["Game_ID"]).strip()) for r in rows}


def append_historial(row: dict):
    """row: Jugador, Fecha_partido, Game_ID, Puntos, Rebotes, Asistencias, Cumple_umbral, Fecha_procesado"""
    sh = _open_sheet()
    ws = sh.worksheet(config.HISTORIAL_TAB)
    ws.append_row([
        row["Jugador"], row["Fecha_partido"], row["Game_ID"],
        row["Puntos"], row["Rebotes"], row["Asistencias"],
        row["Cumple_umbral"], row["Fecha_procesado"],
    ])
