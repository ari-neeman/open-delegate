# open_delegate.py
# Prototipo OpenDelegate - Etapa 1 (Linux)
# Licencia: Apache 2.0
#
# Persistencia en JSON. Nada de contraseñas reales.

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional
import uuid
import json
import os

app = FastAPI(title="OpenDelegate", version="0.2.0")

# --- Rutas de datos ---
DIR_DATOS = "datos"
ARCHIVO_PERMISOS = os.path.join(DIR_DATOS, "permisos.json")
ARCHIVO_SOLICITUDES = os.path.join(DIR_DATOS, "solicitudes.json")
ARCHIVO_AUDITORIA = os.path.join(DIR_DATOS, "auditoria.json")

os.makedirs(DIR_DATOS, exist_ok=True)

# --- Modelos ---
class Permiso(BaseModel):
    recurso: str
    acciones: List[str]
    max_gasto: Optional[float] = None
    requiere_aprobacion: bool = True
    caducidad: Optional[str] = None

class SolicitudCompra(BaseModel):
    producto: str
    precio: float
    tienda: str

class Aprobacion(BaseModel):
    solicitud_id: str
    aprobado: bool

# --- Persistencia ---
def cargar_json(ruta, valor_por_defecto):
    if os.path.exists(ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return valor_por_defecto
    return valor_por_defecto

def guardar_json(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)

# --- Estado (cargado desde disco al arrancar) ---
def cargar_permisos_iniciales():
    guardados = cargar_json(ARCHIVO_PERMISOS, None)
    if guardados:
        return [Permiso(**p) for p in guardados]
    # Si no hay, creamos los de ejemplo
    iniciales = [
        Permiso(
            recurso="tienda-ejemplo.com",
            acciones=["buscar", "comparar", "preparar_compra"],
            max_gasto=100.0,
            requiere_aprobacion=True,
            caducidad=(datetime.utcnow() + timedelta(days=30)).isoformat(),
        ),
        Permiso(
            recurso="vuelos",
            acciones=["buscar", "reservar"],
            max_gasto=None,
            requiere_aprobacion=True,
        ),
    ]
    guardar_json(ARCHIVO_PERMISOS, [p.model_dump() for p in iniciales])
    return iniciales

PERMISOS = cargar_permisos_iniciales()
SOLICITUDES = cargar_json(ARCHIVO_SOLICITUDES, {})
AUDITORIA = cargar_json(ARCHIVO_AUDITORIA, [])

def guardar_permisos():
    guardar_json(ARCHIVO_PERMISOS, [p.model_dump() for p in PERMISOS])

def guardar_solicitudes():
    guardar_json(ARCHIVO_SOLICITUDES, SOLICITUDES)

def guardar_auditoria():
    guardar_json(ARCHIVO_AUDITORIA, AUDITORIA)

def registrar(evento: str, detalle: dict):
    AUDITORIA.append({
        "ts": datetime.utcnow().isoformat(),
        "evento": evento,
        "detalle": detalle,
    })
    guardar_auditoria()

def buscar_permiso(recurso: str) -> Optional[Permiso]:
    for p in PERMISOS:
        if p.recurso == recurso:
            return p
    return None

# --- Endpoints ---

@app.get("/")
def raiz():
    return {
        "nombre": "OpenDelegate",
        "version": "0.2.0",
        "principios": [
            "El usuario manda",
            "Nunca contrasenas reales",
            "El agente se identifica como IA",
            "Todo queda auditado",
            "Aprobacion humana antes de pagar",
        ],
    }

@app.get("/permisos")
def listar_permisos():
    return {"permisos": PERMISOS, "nota": "Nunca se usan contrasenas reales."}

@app.get("/auditoria")
def ver_auditoria():
    return {"eventos": AUDITORIA}

@app.get("/solicitudes")
def listar_solicitudes():
    return {"solicitudes": list(SOLICITUDES.values())}

@app.post("/solicitar-compra")
def solicitar_compra(s: SolicitudCompra):
    permiso = buscar_permiso(s.tienda)
    if not permiso:
        registrar("denegado_sin_permiso", {"tienda": s.tienda})
        raise HTTPException(403, f"Sin permiso para {s.tienda}")

    if permiso.max_gasto is not None and s.precio > permiso.max_gasto:
        registrar("denegado_limite", {"precio": s.precio, "max": permiso.max_gasto})
        raise HTTPException(403, "Precio supera el limite autorizado")

    sol_id = str(uuid.uuid4())
    SOLICITUDES[sol_id] = {
        "id": sol_id,
        "producto": s.producto,
        "precio": s.precio,
        "tienda": s.tienda,
        "estado": "pendiente_aprobacion",
        "agente_se_identifica_como": "open-delegate-v1 (IA)",
        "actua_en_nombre_de": "usuario@local",
    }
    guardar_solicitudes()
    registrar("solicitud_creada", {"id": sol_id, "producto": s.producto})
    return SOLICITUDES[sol_id]

@app.post("/aprobar")
def aprobar(a: Aprobacion):
    sol = SOLICITUDES.get(a.solicitud_id)
    if not sol:
        raise HTTPException(404, "Solicitud no encontrada")

    if not a.aprobado:
        sol["estado"] = "rechazado_por_usuario"
        guardar_solicitudes()
        registrar("rechazo_usuario", {"id": a.solicitud_id})
        return sol

    sol["estado"] = "aprobado"
    sol["credencial_generada"] = {
        "tipo": "token_de_un_solo_uso",
        "contrasenas_reales": False,
        "tarjeta_virtual": "****-****-****-0000",
    }
    guardar_solicitudes()
    registrar("aprobado_y_token_emitido", {"id": a.solicitud_id})
    return sol
