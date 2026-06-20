from src import config


def evaluate_game(puntos, rebotes, asistencias, umbral=None):
    """Devuelve (cumple: bool, motivo: str)."""
    threshold = umbral if umbral else config.DEFAULT_THRESHOLD_PTS
    dobles = sum(1 for x in (puntos, rebotes, asistencias) if x >= 10)

    motivos = []
    if puntos >= threshold:
        motivos.append(f"{puntos} puntos (umbral: {threshold})")
    if dobles == 2:
        motivos.append("doble-doble")
    elif dobles >= 3:
        motivos.append("triple-doble")

    cumple = len(motivos) > 0
    return cumple, ", ".join(motivos)
