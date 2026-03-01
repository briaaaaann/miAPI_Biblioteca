from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field, EmailStr
from typing import Literal, List, Optional
from datetime import datetime

app = FastAPI(title="API Biblioteca")

#Listas
libros = []
prestamos = []

#Modelos
class Libro(BaseModel):
    id: int
    nombre: str = Field(min_length=2, max_length=100)
    anio: int = Field
    paginas: int = Field(gt=1)
    estado: Literal["Disponible", "Prestado"] = "Disponible"

class Usuario(BaseModel):
    nombre: str
    correo: EmailStr

class Prestamo(BaseModel):
    id_prestamo: int
    id_libro: int
    usuario: Usuario

#Endpoints http://localhost:5000
    #Registrar libros disponibles
@app.post("/libros/", status_code=status.HTTP_201_CREATED, tags=['Libros'])
async def registrar_libro(libro: Libro):
    if any(l["id"] == libro.id for l in libros):
        raise HTTPException(status_code=400, detail="ID Existente")
    libros.append(libro.model_dump())
    return {"Mensaje":"Libro registrado exitosamente", "Libro": libro}

    #Listar libros disponibles
@app.get("/libros/disponibilidad", tags=['Libros'])
async def libros_disponibles():
    disponibles = [libro for libro in libros if libro["estado"] == "Disponible"]
    return {"total": len(disponibles), "libros": disponibles}

    #Buscar libros por nombre
@app.get("/libros/{nombre}", tags=['Libros'])
async def buscar_libro(nombre: str):
    resultados = [libro for libro in libros if nombre.lower() in libro["nombre"].lower()]
    if not resultados:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return {"Resultados": resultados}

    #Registrar prestamos 
@app.post("/prestamos/", status_code=status.HTTP_201_CREATED, tags=['Prestamos'])
async def registrar_prestamo(prestamo: Prestamo):
    libro_encontrado = next((l for l in libros if l['id'] == prestamo.id_libro), None)
    if not libro_encontrado:
        raise HTTPException(status_code=400, detail="Libro no econtrado")
    if libro_encontrado["estado"] == "Prestado":
        raise HTTPException(status_code=409, detail="Conflict: El libro ya esta prestado")
    libro_encontrado["estado"] = "Prestado"
    prestamos.append(prestamo.model_dump())
    return {'mensaje': "Prestamo resgistrado"}

    #Cambiar estatus de libro 
@app.put("/prestamos/{id_prestamo}/devolucion", status_code=status.HTTP_200_OK, tags=['Prestamos'])
async def devolver_libro(id_prestamo: int):
    prestamo = next((p for p in prestamos if p["id_prestamo"] == id_prestamo), None)
    if not prestamo:
        raise HTTPException(status_code=409, detail="Conflict: No existe registro de prestamo")
    for libro in libros:
        if libro["id"] == prestamo["id_libro"]:
            libro["estado"] = "Disponible"
            break
        return {"mensaje": "Libro devuelto"}
    
    #Eliminar registro de prestamo
@app.delete("/prestamos/{id_prestamo}", tags=['Prestamos'])
async def eliminar_prestamo(id_prestamo:int):
    for i, prestamo in enumerate(prestamos):
        if prestamo["id_prestamo"] == id_prestamo:
            prestamo_eliminado = prestamos.pop(i)
            return {"mensaje": "Resgistro eliminado", "datos": prestamo_eliminado}
        raise HTTPException(status_code=404, detail="Registro no econtrado")
    
