from typing import Dict, List
import unicodedata


DEPARTAMENTOS_PROVINCIAS: Dict[str, List[str]] = {
    "AMAZONAS": [
        "CHACHAPOYAS", "BAGUA", "BONGARA", "CONDORCANQUI", "LUYA",
        "RODRIGUEZ DE MENDOZA", "UTCUBAMBA",
    ],
    "ANCASH": [
        "HUARAZ", "AIJA", "ANTONIO RAYMONDI", "ASUNCION", "BOLOGNESI",
        "CARHUAZ", "CARLOS FERMIN FITZCARRALD", "CASMA", "CORONGO",
        "HUARI", "HUARMEY", "HUAYLAS", "MARISCAL LUZURIAGA", "OCROS",
        "PALLASCA", "POMABAMBA", "RECUAY", "SANTA", "SIHUAS", "YUNGAY",
    ],
    "APURIMAC": [
        "ABANCAY", "ANDAHUAYLAS", "ANTABAMBA", "AYMARAES",
        "CHINCHEROS", "COTABAMBAS", "GRAU",
    ],
    "AREQUIPA": [
        "AREQUIPA", "CAMANA", "CARAVELI", "CASTILLA",
        "CAYLLOMA", "CONDESUYOS", "ISLAY", "LA UNION",
    ],
    "AYACUCHO": [
        "HUAMANGA", "CANGALLO", "HUANCA SANCOS", "HUANTA", "LA MAR",
        "LUCANAS", "PARINACOCHAS", "PAUCAR DEL SARA SARA", "SUCRE",
        "VICTOR FAJARDO", "VILCASHUAMAN",
    ],
    "CAJAMARCA": [
        "CAJAMARCA", "CAJABAMBA", "CELENDIN", "CHOTA", "CONTUMAZA",
        "CUTERVO", "HUALGAYOC", "JAEN", "SAN IGNACIO", "SAN MARCOS",
        "SAN MIGUEL", "SAN PABLO", "SANTA CRUZ",
    ],
    "CALLAO": ["CALLAO"],
    "CUSCO": [
        "CUSCO", "ACOMAYO", "ANTA", "CALCA", "CANAS", "CANCHIS",
        "CHUMBIVILCAS", "ESPINAR", "LA CONVENCION", "PARURO",
        "PAUCARTAMBO", "QUISPICANCHI", "URUBAMBA",
    ],
    "HUANCAVELICA": [
        "HUANCAVELICA", "ACOBAMBA", "ANGARAES", "CASTROVIRREYNA",
        "CHURCAMPA", "HUAYTARA", "TAYACAJA",
    ],
    "HUANUCO": [
        "HUANUCO", "AMBO", "DOS DE MAYO", "HUACAYBAMBA", "HUAMALIES",
        "LEONCIO PRADO", "MARAÑON", "PACHITEA", "PUERTO INCA",
        "LAURICOCHA", "YAROWILCA",
    ],
    "ICA": ["ICA", "CHINCHA", "NAZCA", "PALPA", "PISCO"],
    "JUNIN": [
        "HUANCAYO", "CONCEPCION", "CHANCHAMAYO", "JAUJA",
        "JUNIN", "SATIPO", "TARMA", "YAULI", "CHUPACA",
    ],
    "LA LIBERTAD": [
        "TRUJILLO", "ASCOPE", "BOLIVAR", "CHEPEN", "JULCAN", "OTUZCO",
        "PACASMAYO", "PATAZ", "SANCHEZ CARRION", "SANTIAGO DE CHUCO",
        "GRAN CHIMU", "VIRU",
    ],
    "LAMBAYEQUE": ["CHICLAYO", "FERREÑAFE", "LAMBAYEQUE"],
    "LIMA": [
        "LIMA", "BARRANCA", "CAJATAMBO", "CANTA", "CAÑETE",
        "HUARAL", "HUAROCHIRI", "HUAURA", "OYON", "YAUYOS",
    ],
    "LORETO": [
        "MAYNAS", "ALTO AMAZONAS", "LORETO", "MARISCAL RAMON CASTILLA",
        "REQUENA", "UCAYALI", "DATEM DEL MARAÑON", "PUTUMAYO",
    ],
    "MADRE DE DIOS": ["TAMBOPATA", "MANU", "TAHUAMANU"],
    "MOQUEGUA": ["MARISCAL NIETO", "GENERAL SANCHEZ CERRO", "ILO"],
    "PASCO": ["PASCO", "DANIEL ALCIDES CARRION", "OXAPAMPA"],
    "PIURA": [
        "PIURA", "AYABACA", "HUANCABAMBA", "MORROPON",
        "PAITA", "SULLANA", "TALARA", "SECHURA",
    ],
    "PUNO": [
        "PUNO", "AZANGARO", "CARABAYA", "CHUCUITO", "EL COLLAO",
        "HUANCANE", "LAMPA", "MELGAR", "MOHO", "SAN ANTONIO DE PUTINA",
        "SAN ROMAN", "SANDIA", "YUNGUYO",
    ],
    "SAN MARTIN": [
        "MOYOBAMBA", "BELLAVISTA", "EL DORADO", "HUALLAGA", "LAMAS",
        "MARISCAL CACERES", "PICOTA", "RIOJA", "SAN MARTIN", "TOCACHE",
    ],
    "TACNA": ["TACNA", "CANDARAVE", "JORGE BASADRE", "TARATA"],
    "TUMBES": ["TUMBES", "CONTRALMIRANTE VILLAR", "ZARUMILLA"],
    "UCAYALI": ["CORONEL PORTILLO", "ATALAYA", "PADRE ABAD", "PURUS"],
}


def quitar_tildes(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def slug_geo(texto: str) -> str:
    texto = quitar_tildes(texto.upper()).strip()
    texto = texto.replace("Ñ", "N")
    texto = "".join(ch for ch in texto if ch.isalnum())
    return texto


def label_geo(provincia: str, departamento: str) -> str:
    return "{0} - {1}".format(provincia.title(), departamento.title())


def build_provincias_peru() -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []

    for departamento, provincias in DEPARTAMENTOS_PROVINCIAS.items():
        departamento_slug = slug_geo(departamento)

        for provincia in provincias:
            provincia_slug = slug_geo(provincia)

            items.append({
                "provincia": provincia_slug,
                "departamento": departamento_slug,
                "value": "{0}-{1}".format(provincia_slug, departamento_slug),
                "label": label_geo(provincia, departamento),
                "provincia_nombre": provincia.title(),
                "departamento_nombre": departamento.title(),
            })

    items.sort(key=lambda x: x["label"])
    return items


PROVINCIAS_PERU = build_provincias_peru()
PROVINCIAS_VALIDAS = set(item["value"] for item in PROVINCIAS_PERU)