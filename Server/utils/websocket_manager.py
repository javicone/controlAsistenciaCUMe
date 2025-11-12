import json
from typing import List, Dict, Any, Optional
from fastapi import WebSocket
import logging

class ConnectionManager:
    def __init__(self):
        # Mapeo de device_id -> WebSocket (para nodos ESP32)
        self.device_connections: Dict[str, WebSocket] = {}
        
        # Lista simple de WebSockets admin (no necesitamos tracking por user_id)
        self.admin_websockets: List[WebSocket] = []
        
        # Lista simple de WebSockets conserje
        self.conserje_websockets: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, client_type: str = "generic", client_id: Optional[str] = None):
        """
        Conecta un cliente WebSocket.
        
        Args:
            websocket: Instancia de WebSocket
            client_type: Tipo de cliente ("device", "admin", "conserje", "generic")
            client_id: Identificador del cliente (solo para devices)
        """
        await websocket.accept()
        
        if client_type == "device" and client_id:
            self.device_connections[client_id] = websocket
            logging.info(f"✅ Dispositivo conectado: {client_id}. Total: {len(self.device_connections)}")
        elif client_type == "admin":
            self.admin_websockets.append(websocket)
            logging.info(f"✅ Admin conectado. Total admins: {len(self.admin_websockets)}")
        elif client_type == "conserje":
            self.conserje_websockets.append(websocket)
            logging.info(f"✅ Conserje conectado. Total conserjes: {len(self.conserje_websockets)}")
        else:
            logging.info(f"✅ Cliente genérico conectado")

    def disconnect(self, websocket: WebSocket, client_id: Optional[str] = None):
        """
        Desconecta un cliente WebSocket.
        
        Args:
            websocket: Instancia de WebSocket
            client_id: Identificador del dispositivo (si es un device)
        """
        # Remover de devices si es un dispositivo
        if client_id and client_id in self.device_connections:
            del self.device_connections[client_id]
            logging.info(f"❌ Dispositivo desconectado: {client_id}. Total: {len(self.device_connections)}")
        
        # Remover de admins si es un admin
        if websocket in self.admin_websockets:
            self.admin_websockets.remove(websocket)
            logging.info(f"❌ Admin desconectado. Total admins: {len(self.admin_websockets)}")
        
        # Remover de conserjes si es un conserje
        if websocket in self.conserje_websockets:
            self.conserje_websockets.remove(websocket)
            logging.info(f"❌ Conserje desconectado. Total conserjes: {len(self.conserje_websockets)}")

    async def send_to_device(self, device_id: str, message: dict) -> bool:
        """
        Envía un mensaje a un dispositivo ESP32 específico.
        
        Args:
            device_id: ID del dispositivo destinatario
            message: Diccionario con el mensaje a enviar
            
        Returns:
            True si se envió correctamente, False si el dispositivo no está conectado
        """
        if device_id not in self.device_connections:
            logging.warning(f"⚠️ Dispositivo {device_id} no está conectado")
            return False
        
        websocket = self.device_connections[device_id]
        try:
            # Asegurar que el mensaje incluye el device_id
            message["device_id"] = device_id
            await websocket.send_json(message)
            logging.info(f"📤 Mensaje enviado a dispositivo {device_id}: {message.get('tipo', 'unknown')}")
            return True
        except Exception as e:
            logging.error(f"❌ Error enviando a dispositivo {device_id}: {e}")
            self.disconnect(websocket, device_id)
            return False

    async def notify_admins(self, message: dict):
        """Envía un mensaje a todos los paneles de administración conectados"""
        disconnected = []
        
        for websocket in self.admin_websockets:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logging.error(f"❌ Error enviando a admin: {e}")
                disconnected.append(websocket)
        
        # Limpiar conexiones muertas
        for ws in disconnected:
            self.disconnect(ws)
        
        logging.info(f"📢 Notificación enviada a {len(self.admin_websockets)} admins")

    async def notify_conserjes(self, message: dict):
        """Envía un mensaje a todos los conserjes conectados"""
        disconnected = []
        
        for websocket in self.conserje_websockets:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logging.error(f"❌ Error enviando a conserje: {e}")
                disconnected.append(websocket)
        
        # Limpiar conexiones muertas
        for ws in disconnected:
            self.disconnect(ws)
        
        logging.info(f"📢 Notificación enviada a {len(self.conserje_websockets)} conserjes")

    async def notify_staff(self, message: dict):
        """Envía un mensaje a TODOS los usuarios staff (admins + conserjes)"""
        await self.notify_admins(message)
        await self.notify_conserjes(message)

    async def broadcast(self, message: dict):
        """Envía un mensaje a todos los clientes (devices + admins + conserjes)"""
        # Broadcast a devices
        for device_id, websocket in list(self.device_connections.items()):
            try:
                await websocket.send_json(message)
            except Exception as e:
                logging.error(f"❌ Error en broadcast a {device_id}: {e}")
                self.disconnect(websocket, device_id)
        
        # Broadcast a admins
        for websocket in list(self.admin_websockets):
            try:
                await websocket.send_json(message)
            except Exception as e:
                logging.error(f"❌ Error en broadcast a admin: {e}")
                self.disconnect(websocket)
        
        # Broadcast a conserjes
        for websocket in list(self.conserje_websockets):
            try:
                await websocket.send_json(message)
            except Exception as e:
                logging.error(f"❌ Error en broadcast a conserje: {e}")
                self.disconnect(websocket)
        
        logging.info(f"📢 Broadcast enviado a todos los clientes")

    def get_connected_devices(self) -> List[str]:
        """Retorna lista de device_ids conectados"""
        return list(self.device_connections.keys())

    def is_device_connected(self, device_id: str) -> bool:
        """Verifica si un dispositivo está conectado"""
        return device_id in self.device_connections

# Singleton
manager = ConnectionManager()