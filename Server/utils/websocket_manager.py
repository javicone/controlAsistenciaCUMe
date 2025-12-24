import json
from typing import List, Dict, Any, Optional
from fastapi import WebSocket
import logging
import time

class ConnectionManager:
    def __init__(self):
        # 1. Dispositivos (ESP32): Diccionario para acceder rápido por ID
        self.device_connections: Dict[str, WebSocket] = {}
        
        # 2. Última actividad de cada dispositivo (para heartbeat)
        self.device_last_activity: Dict[str, float] = {}
        
        # 3. Admins: Lista simple (pueden haber varios admins conectados a la vez)
        self.admin_websockets: List[WebSocket] = []
        
        # 4. Conserjes: Lista simple
        self.conserje_websockets: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, client_type: str, client_id: Optional[str] = None):
        """
        Acepta la conexión y clasifica al cliente según su rol.
        IMPORTANTE: Este método hace el 'accept()', no hacerlo en el router.
        """
        await websocket.accept()
        
        if client_type == "device" and client_id:
            self.device_connections[client_id] = websocket
            self.device_last_activity[client_id] = time.time()
            logging.info(f"✅ Dispositivo conectado: {client_id}. Total: {len(self.device_connections)}")
            
        elif client_type == "admin":
            self.admin_websockets.append(websocket)
            logging.info(f"✅ Admin conectado. Total admins: {len(self.admin_websockets)}")
            
        elif client_type == "conserje":
            self.conserje_websockets.append(websocket)
            logging.info(f"✅ Conserje conectado. Total conserjes: {len(self.conserje_websockets)}")
            
        else:
            logging.warning(f"⚠️ Tipo de cliente desconocido intentó conectar: {client_type}")

    def update_activity(self, client_id: str):
        """Actualiza el timestamp de última actividad de un dispositivo."""
        if client_id:
            self.device_last_activity[client_id] = time.time()

    def disconnect(self, websocket: WebSocket, client_id: Optional[str] = None):
        """
        Elimina la conexión de la lista correspondiente de forma segura.
        """
        # 1. Desconectar Dispositivo
        if client_id and client_id in self.device_connections:
            del self.device_connections[client_id]
            if client_id in self.device_last_activity:
                del self.device_last_activity[client_id]
            logging.info(f"❌ Dispositivo desconectado: {client_id}")
        
        # 2. Desconectar Admin
        if websocket in self.admin_websockets:
            self.admin_websockets.remove(websocket)
            logging.info(f"❌ Admin desconectado. Restantes: {len(self.admin_websockets)}")
        
        # 3. Desconectar Conserje
        if websocket in self.conserje_websockets:
            self.conserje_websockets.remove(websocket)
            logging.info(f"❌ Conserje desconectado. Restantes: {len(self.conserje_websockets)}")

    async def send_to_device(self, device_id: str, message: dict) -> bool:
        """Envía mensaje directo a un ESP32"""
        if device_id not in self.device_connections:
            logging.warning(f"⚠️ Intento de envío a dispositivo offline: {device_id}")
            return False
        websocket = self.device_connections[device_id]
        try:
            message["device_id"] = device_id
            await websocket.send_json(message)
            return True
        except Exception as e:
            logging.error(f"❌ Error enviando a {device_id}: {e}")
            self.disconnect(websocket, device_id)
            return False

    async def notify_admins(self, message: dict):
        """Notifica solo a los administradores"""
        for websocket in list(self.admin_websockets): # Usamos list() para evitar errores si se modifica la lista
            try:
                await websocket.send_json(message)
            except Exception:
                self.disconnect(websocket)

    async def notify_conserjes(self, message: dict):
        """Notifica solo a los conserjes"""
        for websocket in list(self.conserje_websockets):
            try:
                await websocket.send_json(message)
            except Exception:
                self.disconnect(websocket)

    async def notify_staff(self, message: dict):
        """Notifica a todo el personal humano (Admins + Conserjes)"""
        await self.notify_admins(message)
        await self.notify_conserjes(message)

    async def broadcast(self, message: dict):
        """Envía a TODO EL MUNDO (incluidos dispositivos)"""
        # A dispositivos
        for device_id, ws in list(self.device_connections.items()):
            try:
                await ws.send_json(message)
            except:
                self.disconnect(ws, device_id)
        
        # A staff
        await self.notify_staff(message)

    def get_connected_devices(self) -> List[str]:
        return list(self.device_connections.keys())

# Instancia global
manager = ConnectionManager()