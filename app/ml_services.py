import collections
import re
import unicodedata
from typing import Dict, List, Any, Optional, Tuple


PESOS = {
    "criticos": 5,
    "fuertes": 3,
    "contexto": 1,
    "demanda": 2,
}

UMBRAL_CATEGORIA_MINIMO = 3


DICCIONARIO_PONDERADO: Dict[str, Dict[str, Any]] = {
    "seguridad_ciudadana": {
        "etiqueta": "Seguridad Ciudadana",
        "entidad": "Mininter",
        "criticos": [
            "sicariato", "extorsion", "balacera", "secuestro",
            "cobro de cupos", "cupos", "gota a gota", "homicidio",
            "robo armado", "asalto a mano armada"
        ],
        "fuertes": [
            "delincuencia", "robos", "robo", "asalto", "asaltos",
            "inseguridad", "raqueteros", "choro", "choros",
            "cogoteo", "marcaje", "amenazas", "me robaron", "nos roban"
        ],
        "contexto": [
            "seguridad", "policia", "policias", "serenazgo",
            "comisaria", "patrullaje", "patrullero", "camaras", "miedo"
        ],
        "demanda": [
            "mas policias", "mas serenazgo", "mayor patrullaje",
            "mas camaras", "presencia policial"
        ],
    },
    "salud": {
        "etiqueta": "Salud",
        "entidad": "Minsa",
        "criticos": [
            "negligencia", "negligencia medica", "sin medicinas",
            "no hay medicinas", "no hay citas", "hospital colapsado",
            "muertes", "sin ambulancia", "falta de medicos",
            "falta de especialistas", "dengue", "anemia", "desnutricion"
        ],
        "fuertes": [
            "posta abandonada", "postas abandonadas", "no atienden",
            "sin atencion", "no hay doctor", "no hay medico",
            "emergencia saturada", "falta de camas", "sin vacunas", "sin equipos"
        ],
        "contexto": [
            "posta", "postas", "hospital", "salud", "medico", "medicos",
            "doctor", "doctores", "emergencias", "essalud", "farmacia",
            "cita", "citas", "ambulancia"
        ],
        "demanda": [
            "necesitamos medicos", "necesitamos especialistas",
            "que manden medicinas", "mas citas", "equipar la posta"
        ],
    },
    "infraestructura_vial": {
        "etiqueta": "Infraestructura y Vías",
        "entidad": "MTC",
        "criticos": [
            "pistas rotas", "obra paralizada", "obras paralizadas",
            "puente caido", "puente colapsado", "huaico", "huayco",
            "carretera bloqueada", "via interrumpida", "deslizamiento",
            "trocha intransitable"
        ],
        "fuertes": [
            "huecos", "baches", "veredas rotas", "carretera en mal estado",
            "sin asfaltado", "desmonte", "calle destruida",
            "pista malograda", "acceso vial"
        ],
        "contexto": [
            "pistas", "veredas", "asfalto", "calle", "construccion",
            "carretera", "peaje", "obra", "obras", "transito", "puente", "via"
        ],
        "demanda": [
            "arreglo de pistas", "asfaltado", "mantenimiento vial",
            "construccion de puente", "rehabilitar la carretera", "mantenimiento"
        ],
    },
    "servicios_basicos": {
        "etiqueta": "Servicios Básicos",
        "entidad": "Vivienda / Gob. local / prestadoras",
        "criticos": [
            "sin agua", "sin luz", "corte de agua", "corte de luz",
            "apagones", "desague colapsado", "desborde de desague",
            "agua contaminada", "no llega el agua", "sin alcantarillado"
        ],
        "fuertes": [
            "baja presion", "falta de agua", "falta de luz", "tuberia rota",
            "aniego", "basura acumulada", "recojo de basura",
            "internet inestable", "internet lento", "electrodomesticos quemados"
        ],
        "contexto": [
            "agua", "luz", "desague", "alcantarillado",
            "electricidad", "saneamiento", "presion"
        ],
        "demanda": [
            "queremos agua potable", "necesitamos desague",
            "restablezcan el servicio", "que vuelva la luz"
        ],
    },
    "educacion": {
        "etiqueta": "Educación",
        "entidad": "Minedu",
        "criticos": [
            "colegios cayendose", "colegio se cae", "sin profesores",
            "huelga de maestros", "bullying", "violencia escolar",
            "universidad cerrada", "sin vacantes", "sin internet para clases"
        ],
        "fuertes": [
            "falta de docentes", "aulas prefabricadas", "colegio abandonado",
            "techo en mal estado", "baños insalubres", "ugel no responde",
            "no hay clases", "clases suspendidas"
        ],
        "contexto": [
            "educacion", "colegio", "profesor", "profesores", "clases",
            "alumnos", "matricula", "universidad", "ugel", "escuela",
            "docentes", "aula"
        ],
        "demanda": [
            "necesitamos profesores", "mejorar colegios",
            "mantenimiento del colegio", "mas vacantes"
        ],
    },
    "mineria_conflictos": {
        "etiqueta": "Minería y Conflictos",
        "entidad": "Minem",
        "criticos": [
            "mineria ilegal", "contaminacion minera", "relaves", "derrame",
            "paro minero", "conflicto minero", "rio contaminado por mineria",
            "pasivos ambientales"
        ],
        "fuertes": [
            "concesion minera", "protesta minera", "antimineros",
            "extraccion ilegal", "canon mal distribuido", "afectacion ambiental"
        ],
        "contexto": [
            "mina", "mineria", "canon", "huelga", "conflicto",
            "oro", "cobre", "concesion", "relave"
        ],
        "demanda": [
            "fiscalizacion minera", "remediacion ambiental",
            "control de mineria ilegal", "que no contaminen"
        ],
    },
    "agricultura_agro": {
        "etiqueta": "Agricultura y Agro",
        "entidad": "Midagri",
        "criticos": [
            "sequia", "plagas", "falta de fertilizantes", "perdida de cosecha",
            "heladas", "inundacion de cultivos", "fenomeno del nino",
            "ganado muriendo", "falta de agua para riego"
        ],
        "fuertes": [
            "campo seco", "sin abono", "sin urea", "cultivos afectados",
            "riego insuficiente", "precio del fertilizante",
            "enfermedades del ganado", "agricultores perjudicados"
        ],
        "contexto": [
            "agricultura", "chacra", "campesinos", "lluvias", "abono",
            "urea", "semillas", "riego", "cosecha", "ganado", "agro"
        ],
        "demanda": [
            "apoyo al agricultor", "fertilizantes", "mejorar riego",
            "reservorios", "seguro agrario"
        ],
    },
    "cultura_turismo": {
        "etiqueta": "Cultura y Turismo",
        "entidad": "Mincetur / Cultura",
        "criticos": [
            "maltrato al turista", "ruinas abandonadas", "venta de entradas",
            "estafa al turista", "desorganizacion machupicchu",
            "patrimonio abandonado", "saqueo arqueologico"
        ],
        "fuertes": [
            "turismo afectado", "falta de promocion", "mal servicio turistico",
            "basura en zona turistica", "acceso restringido", "artesanos perjudicados"
        ],
        "contexto": [
            "turismo", "cultura", "machupicchu", "turistas", "pasajes",
            "boletos", "museo", "artesanos", "patrimonio"
        ],
        "demanda": [
            "mejor organizacion", "promocion turistica",
            "cuidar patrimonio", "mejor trato al visitante"
        ],
    },
    "economia_empleo": {
        "etiqueta": "Economía y Empleo",
        "entidad": "MEF / MTPE",
        "criticos": [
            "desempleo", "inflacion", "despidos", "quiebra", "hambre",
            "no alcanza para comer", "cierre de negocios", "subida de precios"
        ],
        "fuertes": [
            "no alcanza", "todo esta caro", "sin chamba", "falta de trabajo",
            "sueldo bajo", "negocio quebrado", "mercado caro", "deudas"
        ],
        "contexto": [
            "chamba", "trabajo", "sueldo", "precios", "plata",
            "mercado", "caro", "economia", "negocio", "ingresos", "empleo"
        ],
        "demanda": [
            "mas empleo", "apoyo a mypes", "bajar precios",
            "reactivacion economica", "oportunidades laborales"
        ],
    },
    "corrupcion_gestion": {
        "etiqueta": "Corrupción y Gestión",
        "entidad": "PCM / Contraloría / gobiernos",
        "criticos": [
            "alcalde corrupto", "obras fantasma", "coima", "nepotismo",
            "robo de presupuesto", "colusion", "sobrevaloracion", "desvio de fondos"
        ],
        "fuertes": [
            "corrupcion", "cutra", "gobernador corrupto", "municipio no responde",
            "tramites demorados", "burocracia", "autoridades no hacen nada",
            "mermelada", "favores politicos"
        ],
        "contexto": [
            "alcalde", "gobernador", "tramites", "burocracia",
            "autoridades", "municipio", "gestion publica",
            "licitacion", "obra publica"
        ],
        "demanda": [
            "fiscalizacion", "transparencia", "rendicion de cuentas",
            "investigacion", "cambio de autoridades"
        ],
    },
    "transporte_movilidad": {
        "etiqueta": "Transporte y Movilidad",
        "entidad": "MTC / gobiernos locales",
        "criticos": [
            "accidentes constantes", "transporte informal",
            "cobro excesivo de pasaje", "chofer ebrio"
        ],
        "fuertes": [
            "trafico", "congestion", "pasaje caro", "combis",
            "mototaxis informales", "falta de rutas", "transporte desordenado"
        ],
        "contexto": [
            "transporte", "pasaje", "combi", "bus", "mototaxi", "terminal"
        ],
        "demanda": [
            "mejor transporte", "ordenar rutas", "fiscalizacion del transporte"
        ],
    },
    "medio_ambiente": {
        "etiqueta": "Medio Ambiente",
        "entidad": "Minam / municipios",
        "criticos": [
            "rio contaminado", "aire contaminado", "botadero informal", "quema de basura"
        ],
        "fuertes": [
            "basural", "contaminacion", "mal olor", "humo", "residuos"
        ],
        "contexto": [
            "ambiente", "aire", "residuos"
        ],
        "demanda": [
            "limpieza publica", "relleno sanitario", "cuidar el rio"
        ],
    },
}


PATRONES_DOLENCIA: List[Tuple[str, str]] = [
    (r"\bno hay agua\b", "no hay agua"),
    (r"\bsin agua\b", "sin agua"),
    (r"\bno llega el agua\b", "no llega el agua"),
    (r"\bfalta de agua\b", "falta de agua"),
    (r"\bfalta agua para riego\b", "falta agua para riego"),
    (r"\bse fue la luz\b", "se fue la luz"),
    (r"\bcorte de luz\b", "corte de luz"),
    (r"\bno hay medicinas\b", "no hay medicinas"),
    (r"\bsin medicinas\b", "sin medicinas"),
    (r"\bno hay citas\b", "no hay citas"),
    (r"\bno atienden\b", "no atienden"),
    (r"\bfalta de medicos\b", "falta de medicos"),
    (r"\bfalta de especialistas\b", "falta de especialistas"),
    (r"\bme robaron\b", "me robaron"),
    (r"\bnos roban\b", "nos roban"),
    (r"\bextorsion\b", "extorsion"),
    (r"\bpistas rotas\b", "pistas rotas"),
    (r"\bveredas rotas\b", "veredas rotas"),
    (r"\bpuente caido\b", "puente caido"),
    (r"\bcarretera bloqueada\b", "carretera bloqueada"),
    (r"\bno hay clases\b", "no hay clases"),
    (r"\bsin profesores\b", "sin profesores"),
    (r"\bfaltan docentes\b", "faltan docentes"),
    (r"\btramites demorados\b", "tramites demorados"),
    (r"\bmunicipio no responde\b", "municipio no responde"),
    (r"\bquema de basura\b", "quema de basura"),
    (r"\bmototaxis informales\b", "mototaxis informales"),
]


def quitar_tildes(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def normalizar_texto(texto: str) -> str:
    texto = texto.lower().strip()
    texto = quitar_tildes(texto)
    texto = re.sub(r"[^a-z0-9ñ\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def capitalizar_legible(valor: str) -> str:
    return " ".join(parte.capitalize() for parte in valor.replace("_", " ").split())


def parsear_ubicacion_canonica(ubicacion: str) -> Dict[str, str]:
    valor = ubicacion.strip().upper()

    if "-" not in valor:
        return {
            "ubicacion_canonica": valor,
            "provincia": valor,
            "departamento": "NOESPECIFICADO",
            "provincia_legible": capitalizar_legible(valor),
            "departamento_legible": "No Especificado",
        }

    provincia, departamento = valor.split("-", 1)

    return {
        "ubicacion_canonica": valor,
        "provincia": provincia,
        "departamento": departamento,
        "provincia_legible": capitalizar_legible(provincia),
        "departamento_legible": capitalizar_legible(departamento),
    }


def encontrar_termino_en_texto(termino: str, texto_limpio: str) -> bool:
    termino = termino.strip()
    if not termino:
        return False

    if " " in termino:
        patron = r"(?<!\w){0}(?!\w)".format(re.escape(termino))
        return re.search(patron, texto_limpio) is not None

    patron = r"\b{0}\b".format(re.escape(termino))
    return re.search(patron, texto_limpio) is not None


def extraer_frases_dolencia(texto_limpio: str) -> List[str]:
    encontradas = []

    for patron, etiqueta in PATRONES_DOLENCIA:
        if re.search(patron, texto_limpio):
            encontradas.append(etiqueta)

    vistas = set()
    resultado = []
    for item in encontradas:
        if item not in vistas:
            vistas.add(item)
            resultado.append(item)

    return resultado


def analizar_texto_completo(texto: str) -> Dict[str, Any]:
    texto_limpio = normalizar_texto(texto)

    puntajes_sector = collections.defaultdict(int)
    terminos_matcheados = collections.defaultdict(int)
    detalles_sector = collections.defaultdict(list)

    for sector_id, config in DICCIONARIO_PONDERADO.items():
        for nivel in ("criticos", "fuertes", "contexto", "demanda"):
            peso = PESOS[nivel]

            for termino in config.get(nivel, []):
                termino_norm = normalizar_texto(termino)

                if encontrar_termino_en_texto(termino_norm, texto_limpio):
                    puntajes_sector[sector_id] += peso
                    terminos_matcheados[termino_norm] += peso
                    detalles_sector[sector_id].append({
                        "termino": termino_norm,
                        "nivel": nivel,
                        "peso": peso,
                    })

    frases_dolencia = extraer_frases_dolencia(texto_limpio)

    categoria_ganadora_id = "otras_dolencias"
    categoria_ganadora = "Otras Dolencias"
    confianza = 0

    if puntajes_sector:
        mejor_sector_id = max(puntajes_sector, key=puntajes_sector.get)
        mejor_puntaje = puntajes_sector[mejor_sector_id]

        if mejor_puntaje >= UMBRAL_CATEGORIA_MINIMO:
            categoria_ganadora_id = mejor_sector_id
            categoria_ganadora = DICCIONARIO_PONDERADO[mejor_sector_id]["etiqueta"]
            confianza = mejor_puntaje

    return {
        "texto_original": texto,
        "texto_normalizado": texto_limpio,
        "categoria_id": categoria_ganadora_id,
        "categoria": categoria_ganadora,
        "confianza": confianza,
        "puntajes_sector": dict(sorted(puntajes_sector.items(), key=lambda x: x[1], reverse=True)),
        "terminos_matcheados": dict(sorted(terminos_matcheados.items(), key=lambda x: x[1], reverse=True)),
        "detalles_sector": dict(detalles_sector),
        "frases_dolencia": frases_dolencia,
    }


def agrupar_textos(
    textos: List[str],
    ubicaciones: List[str],
    nombres: Optional[List[str]] = None
) -> Dict[str, Any]:
    ranking_sectores = collections.defaultdict(int)
    ranking_terminos = collections.defaultdict(int)
    ranking_frases = collections.defaultdict(int)

    palabras_por_ubicacion = collections.defaultdict(lambda: collections.defaultdict(int))
    sectores_por_ubicacion = collections.defaultdict(lambda: collections.defaultdict(int))
    sectores_por_departamento = collections.defaultdict(lambda: collections.defaultdict(int))
    sectores_por_provincia = collections.defaultdict(lambda: collections.defaultdict(int))

    respuestas_clasificadas = []

    for i, texto in enumerate(textos):
        ubicacion_raw = ubicaciones[i] if i < len(ubicaciones) else "NOESPECIFICADA-NOESPECIFICADO"
        nombre_raw = nombres[i] if nombres and i < len(nombres) else "anónimo"

        geo = parsear_ubicacion_canonica(ubicacion_raw)
        analisis = analizar_texto_completo(texto)

        for sector_id, puntos in analisis["puntajes_sector"].items():
            ranking_sectores[sector_id] += puntos
            sectores_por_ubicacion[geo["ubicacion_canonica"]][sector_id] += puntos
            sectores_por_departamento[geo["departamento"]][sector_id] += puntos
            sectores_por_provincia[geo["provincia"]][sector_id] += puntos

        for termino, puntos in analisis["terminos_matcheados"].items():
            ranking_terminos[termino] += puntos
            palabras_por_ubicacion[geo["ubicacion_canonica"]][termino] += puntos

        for frase in analisis["frases_dolencia"]:
            ranking_frases[frase] += 1

        respuestas_clasificadas.append({
            "nombre": nombre_raw,
            "ubicacion_original": ubicacion_raw,
            "ubicacion_canonica": geo["ubicacion_canonica"],
            "provincia": geo["provincia"],
            "departamento": geo["departamento"],
            "provincia_legible": geo["provincia_legible"],
            "departamento_legible": geo["departamento_legible"],
            "texto": texto,
            "categoria_id": analisis["categoria_id"],
            "categoria": analisis["categoria"],
            "confianza": analisis["confianza"],
            "frases_dolencia": analisis["frases_dolencia"],
            "terminos_relevantes": list(analisis["terminos_matcheados"].keys())[:8],
        })

    ranking_sectores_legibles = {}
    for sector_id, puntaje in sorted(ranking_sectores.items(), key=lambda x: x[1], reverse=True):
        ranking_sectores_legibles[sector_id] = {
            "etiqueta": DICCIONARIO_PONDERADO.get(sector_id, {}).get("etiqueta", sector_id),
            "entidad": DICCIONARIO_PONDERADO.get(sector_id, {}).get("entidad", ""),
            "puntaje": puntaje,
        }

    palabras_por_ubicacion_ordenadas = {}
    for ubicacion, palabras in palabras_por_ubicacion.items():
        palabras_por_ubicacion_ordenadas[ubicacion] = dict(
            sorted(palabras.items(), key=lambda x: x[1], reverse=True)[:5]
        )

    sectores_por_ubicacion_ordenadas = {}
    for ubicacion, sectores in sectores_por_ubicacion.items():
        sectores_por_ubicacion_ordenadas[ubicacion] = dict(
            sorted(sectores.items(), key=lambda x: x[1], reverse=True)
        )

    sectores_por_departamento_ordenadas = {}
    for departamento, sectores in sectores_por_departamento.items():
        sectores_por_departamento_ordenadas[departamento] = dict(
            sorted(sectores.items(), key=lambda x: x[1], reverse=True)
        )

    sectores_por_provincia_ordenadas = {}
    for provincia, sectores in sectores_por_provincia.items():
        sectores_por_provincia_ordenadas[provincia] = dict(
            sorted(sectores.items(), key=lambda x: x[1], reverse=True)
        )

    return {
        "total_registros_procesados": len(textos),
        "ranking_sectores": ranking_sectores_legibles,
        "ranking_terminos": dict(sorted(ranking_terminos.items(), key=lambda x: x[1], reverse=True)),
        "frases_recurrentes": dict(sorted(ranking_frases.items(), key=lambda x: x[1], reverse=True)),
        "palabras_clave_por_ubicacion": palabras_por_ubicacion_ordenadas,
        "sectores_por_ubicacion": sectores_por_ubicacion_ordenadas,
        "sectores_por_departamento": sectores_por_departamento_ordenadas,
        "sectores_por_provincia": sectores_por_provincia_ordenadas,
        "muestra_clasificada": respuestas_clasificadas[:50],
    }