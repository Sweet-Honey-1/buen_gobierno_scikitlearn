from pydantic import BaseModel, field_validator

class UserAnswer(BaseModel):
    nombre: str = "anónimo"
    ubicacion: str
    dolencia: str

    @field_validator('dolencia')
    def validar_palabras(cls, v):
        if len(v.split()) > 100:
            raise ValueError('La dolencia no puede exceder las 100 palabras')
        return v

class UserAsk(BaseModel):
    nombre: str = "anónimo"
    ubicacion: str
    pregunta: str

    @field_validator('pregunta')
    def validar_palabras(cls, v):
        if len(v.split()) > 100:
            raise ValueError('La pregunta no puede exceder las 100 palabras')
        return v