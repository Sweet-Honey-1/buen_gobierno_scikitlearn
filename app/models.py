from pydantic import BaseModel, Field, field_validator
import re


PATRON_UBICACION = re.compile(r"^[A-Z0-9]+-[A-Z0-9]+$")


class UserAnswer(BaseModel):
    nombre: str = Field(default="anónimo", max_length=120)
    ubicacion: str = Field(..., min_length=3, max_length=120)
    dolencia: str = Field(..., min_length=3, max_length=1200)

    @field_validator("nombre", mode="before")
    @classmethod
    def limpiar_nombre(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("ubicacion")
    @classmethod
    def validar_ubicacion(cls, v: str):
        valor = v.strip().upper()
        if not PATRON_UBICACION.match(valor):
            raise ValueError(
                "La ubicación debe venir en formato PROVINCIA-DEPARTAMENTO, por ejemplo: TRUJILLO-LALIBERTAD"
            )
        return valor

    @field_validator("dolencia")
    @classmethod
    def validar_dolencia(cls, v: str):
        texto = v.strip()
        if len(texto.split()) > 100:
            raise ValueError("La dolencia no puede exceder las 100 palabras")
        return texto


class UserAsk(BaseModel):
    nombre: str = Field(default="anónimo", max_length=120)
    ubicacion: str = Field(..., min_length=3, max_length=120)
    pregunta: str = Field(..., min_length=3, max_length=1200)

    @field_validator("nombre", mode="before")
    @classmethod
    def limpiar_nombre(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("ubicacion")
    @classmethod
    def validar_ubicacion(cls, v: str):
        valor = v.strip().upper()
        if not PATRON_UBICACION.match(valor):
            raise ValueError(
                "La ubicación debe venir en formato PROVINCIA-DEPARTAMENTO, por ejemplo: TRUJILLO-LALIBERTAD"
            )
        return valor

    @field_validator("pregunta")
    @classmethod
    def validar_pregunta(cls, v: str):
        texto = v.strip()
        if len(texto.split()) > 100:
            raise ValueError("La pregunta no puede exceder las 100 palabras")
        return texto