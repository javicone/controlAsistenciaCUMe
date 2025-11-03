# Sustituir por consultas MySQL. MVP en memoria:
DEVICES = {
    # Ejemplo: registrar cada nodo con su api_key
    "node-001": {"api_key": "REEMPLAZA_ESTA_API_KEY_SEGURA"},
    # "node-002": {"api_key": "..."},
}

def get_device(device_id: str) -> dict | None:
    return DEVICES.get(device_id)
