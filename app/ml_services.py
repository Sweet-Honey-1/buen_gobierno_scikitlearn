import collections
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Lista básica de palabras a ignorar para que el algoritmo sea preciso
stop_words_es = ["el", "la", "los", "las", "un", "una", "y", "o", "de", "del", "que", "en", "por", "para", "a", "con"]

def agrupar_textos(textos, ubicaciones, nombres, max_clusters=3):
    vectorizer = TfidfVectorizer(max_features=50, stop_words=stop_words_es)
    X = vectorizer.fit_transform(textos)

    num_clusters = min(max_clusters, len(textos))
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    kmeans.fit(X)

    mapeo = collections.defaultdict(list)
    for i, label in enumerate(kmeans.labels_):
        mapeo[ubicaciones[i]].append({
            "categoria_cluster": int(label),
            "descripcion": textos[i],
            "ciudadano": nombres[i]
        })
    return dict(mapeo)