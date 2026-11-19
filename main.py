"""Taller Informática 1 - Unidades 3 y 4
Gestión de información biomédica: ordenamiento, archivos, regex y MongoDB.
"""
import csv
import json
import os
import random
import re
import shutil
from datetime import datetime
from pathlib import Path

# ------------------------------------------------------------------
# Configuración
# ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CARPETAS = {
    "txt": DATA_DIR / "txt",
    "csv": DATA_DIR / "csv",
    "json": DATA_DIR / "json",
}
LOG_FILE = BASE_DIR / "log.txt"

# La URI NO se escribe en el código (no subirla a GitHub).
# Defínela como variable de entorno: export MONGO_URI="mongodb+srv://..."
MONGO_URI = os.getenv("MONGO_URI", "")
DB_NAME = "biomedico"
COLECCION = "signos_vitales"

# Patrones del apartado 1
PATRONES = {
    "id": re.compile(r"^ID-\d{3}$"),
    "fr": re.compile(r"^\d{1,3} Años$"),      # edad, ej. "18 Años"
    "fc": re.compile(r"^\d{3}ppm$"),          # ej. "090ppm"
    "spo2": re.compile(r"^\d{2,3}%$"),        # ej. "95%"
}
CAMPOS = ["id", "fr", "fc", "spo2"]

registros = []  # lista en memoria


# ------------------------------------------------------------------
# Log y herramientas del sistema (os / pathlib / shutil)
# ------------------------------------------------------------------
def log(mensaje):
    """Agrega una línea con fecha y hora a log.txt."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {mensaje}\n")
    except OSError as e:
        print(f"No se pudo escribir el log: {e}")


def crear_estructura():
    for ruta in CARPETAS.values():
        ruta.mkdir(parents=True, exist_ok=True)
    log("Estructura de carpetas verificada/creada (data/txt, data/csv, data/json)")


def mover_a_carpeta(nombre_archivo, tipo):
    """Mueve un archivo generado en BASE_DIR a data/<tipo>/."""
    origen = BASE_DIR / nombre_archivo
    destino = CARPETAS[tipo] / nombre_archivo
    if not origen.exists():
        raise FileNotFoundError(f"No existe {origen}")
    CARPETAS[tipo].mkdir(parents=True, exist_ok=True)
    shutil.move(str(origen), str(destino))
    log(f"Archivo movido: {nombre_archivo} -> {destino.relative_to(BASE_DIR)}")
    return destino


# ------------------------------------------------------------------
# 1. Generación y ordenamiento
# ------------------------------------------------------------------
def generar_registros(n=50):
    """Genera n registros aleatorios con el formato pedido."""
    nuevos = []
    for i in range(1, n + 1):
        nuevos.append({
            "id": f"ID-{i:03d}",
            "fr": f"{random.randint(18, 90)} Años",
            "fc": f"{random.randint(50, 130):03d}ppm",
            "spo2": f"{random.randint(88, 100)}%",
        })
    return nuevos


def numero(texto):
    """Extrae el número de un texto ('090ppm' -> 90)."""
    return int(re.search(r"\d+", texto).group())


def merge_sort(lista, clave):
    """Algoritmo de ordenamiento Merge Sort (estable)."""
    if len(lista) <= 1:
        return lista
    medio = len(lista) // 2
    izq = merge_sort(lista[:medio], clave)
    der = merge_sort(lista[medio:], clave)
    resultado, i, j = [], 0, 0
    while i < len(izq) and j < len(der):
        if clave(izq[i]) <= clave(der[j]):
            resultado.append(izq[i])
            i += 1
        else:
            resultado.append(der[j])
            j += 1
    resultado.extend(izq[i:])
    resultado.extend(der[j:])
    return resultado


def ordenar_por_fc(lista):
    return merge_sort(lista, lambda r: numero(r["fc"]))


# ------------------------------------------------------------------
# 4. Validación con expresiones regulares
# ------------------------------------------------------------------
def validar_registro(reg):
    """Devuelve lista de errores (vacía si el registro es válido)."""
    errores = []
    for campo in CAMPOS:
        valor = str(reg.get(campo, ""))
        if not PATRONES[campo].match(valor):
            errores.append(f"{campo}='{valor}' no cumple el formato")
    return errores


def validar_todos(lista):
    validos, invalidos = [], []
    for r in lista:
        errs = validar_registro(r)
        if errs:
            invalidos.append((r, errs))
        else:
            validos.append(r)
    log(f"Validación: {len(validos)} válidos, {len(invalidos)} inválidos")
    return validos, invalidos


# ------------------------------------------------------------------
# 2. Archivos TXT, CSV, JSON (con excepciones y verificación de rutas)
# ------------------------------------------------------------------
def guardar_txt(lista, nombre="datos.txt"):
    try:
        with open(BASE_DIR / nombre, "w", encoding="utf-8") as f:
            for r in lista:
                f.write(",".join(r[c] for c in CAMPOS) + "\n")
        destino = mover_a_carpeta(nombre, "txt")
        print(f"TXT guardado en {destino}")
    except (OSError, FileNotFoundError) as e:
        print(f"Error al guardar TXT: {e}")
        log(f"ERROR guardar_txt: {e}")


def guardar_csv(lista, nombre="datos.csv"):
    try:
        with open(BASE_DIR / nombre, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=CAMPOS)
            w.writeheader()
            w.writerows(lista)
        destino = mover_a_carpeta(nombre, "csv")
        print(f"CSV guardado en {destino}")
    except (OSError, FileNotFoundError) as e:
        print(f"Error al guardar CSV: {e}")
        log(f"ERROR guardar_csv: {e}")


def exportar_json(lista, nombre="datos.json"):
    try:
        with open(BASE_DIR / nombre, "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False, indent=4)
        destino = mover_a_carpeta(nombre, "json")
        print(f"JSON exportado en {destino}")
    except (OSError, FileNotFoundError) as e:
        print(f"Error al exportar JSON: {e}")
        log(f"ERROR exportar_json: {e}")


def importar_json(nombre="datos.json"):
    ruta = CARPETAS["json"] / nombre
    if not ruta.exists():
        print(f"La ruta {ruta} no existe. Exporta primero.")
        log(f"ERROR importar_json: ruta inexistente {ruta}")
        return []
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
        log(f"JSON importado: {len(datos)} registros desde {ruta.name}")
        return datos
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error al importar JSON: {e}")
        log(f"ERROR importar_json: {e}")
        return []


# ------------------------------------------------------------------
# 5. MongoDB Atlas
# ------------------------------------------------------------------
def conectar_mongo():
    """Devuelve la colección signos_vitales o None si falla."""
    if not MONGO_URI:
        print("Define la variable de entorno MONGO_URI con tu cadena de Atlas.")
        return None
    try:
        from pymongo import MongoClient
        from pymongo.errors import PyMongoError
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        log("Conexión a MongoDB Atlas exitosa")
        return client[DB_NAME][COLECCION]
    except ImportError:
        print("Instala pymongo: pip install -r requirements.txt")
    except Exception as e:  # errores de red/autenticación
        print(f"No se pudo conectar a MongoDB: {e}")
        log(f"ERROR conexión MongoDB: {e}")
    return None


def insertar_validados(col, lista):
    validos, _ = validar_todos(lista)
    n = 0
    for r in validos:
        doc = dict(r)
        # Se guardan también valores numéricos para poder consultar
        doc["fc_valor"] = numero(r["fc"])
        doc["spo2_valor"] = numero(r["spo2"])
        col.replace_one({"id": r["id"]}, doc, upsert=True)  # evita duplicados
        n += 1
    print(f"{n} registros validados insertados/actualizados.")
    log(f"MongoDB: {n} registros insertados en {COLECCION}")


def consultas_mongo(col):
    prom = list(col.aggregate([{"$group": {"_id": None,
                                           "promedio": {"$avg": "$fc_valor"}}}]))
    promedio = round(prom[0]["promedio"], 2) if prom else None
    bajos = list(col.find({"spo2_valor": {"$lt": 94}}, {"_id": 0}))
    print(f"Promedio de frecuencia cardiaca: {promedio} ppm")
    print(f"Documentos con SpO2 < 94: {len(bajos)}")
    for d in bajos:
        print("  ", d)
    resultado = {"promedio_fc": promedio, "spo2_menor_94": bajos}
    try:
        ruta = BASE_DIR / "resultados_mongo.json"
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=4)
        mover_a_carpeta("resultados_mongo.json", "json")
        print("Consultas exportadas a data/json/resultados_mongo.json")
    except (OSError, FileNotFoundError) as e:
        print(f"Error al exportar consultas: {e}")
    log("MongoDB: consultas ejecutadas y exportadas")


def consultar_por_id(col, id_):
    if not PATRONES["id"].match(id_):
        print("ID inválido. Formato: ID-001")
        return
    doc = col.find_one({"id": id_}, {"_id": 0})
    print(doc if doc else "No se encontró ese ID.")
    log(f"MongoDB: consulta por ID {id_}")


# ------------------------------------------------------------------
# 6. Menú principal
# ------------------------------------------------------------------
def ingresar_manual():
    print("Ingrese los datos (formatos: ID-001 | 18 Años | 090ppm | 95%)")
    reg = {
        "id": input("id: ").strip(),
        "fr": input("fr (edad): ").strip(),
        "fc": input("fc: ").strip(),
        "spo2": input("spo2: ").strip(),
    }
    errores = validar_registro(reg)
    if errores:
        print("Registro rechazado:")
        for e in errores:
            print("  -", e)
        log(f"Registro manual rechazado: {reg}")
        return
    registros.append(reg)
    print("Registro agregado.")
    log(f"Registro manual agregado: {reg['id']}")


def mostrar_menu():
    print("""
===== SISTEMA DE SIGNOS VITALES =====
1. Generar registros aleatorios (50)
2. Ingresar un registro manualmente
3. Ordenar por frecuencia cardiaca y mostrar
4. Exportar (TXT, CSV y JSON)
5. Importar JSON
6. Validar datos
7. MongoDB: insertar registros validados
8. MongoDB: consultas (promedio FC y SpO2 < 94)
9. MongoDB: consultar por ID
0. Salir""")


def main():
    global registros
    crear_estructura()
    log("Programa iniciado")
    col = None
    while True:
        mostrar_menu()
        op = input("Opción: ").strip()
        if op == "1":
            registros = generar_registros(50)
            print("50 registros generados.")
            log("Generados 50 registros aleatorios")
        elif op == "2":
            ingresar_manual()
        elif op == "3":
            registros = ordenar_por_fc(registros)
            for r in registros:
                print(r)
            log("Datos ordenados por frecuencia cardiaca")
        elif op == "4":
            if not registros:
                print("No hay datos. Genere o importe primero.")
                continue
            registros = ordenar_por_fc(registros)
            guardar_txt(registros)
            guardar_csv(registros)
            exportar_json(registros)
        elif op == "5":
            datos = importar_json()
            if datos:
                registros = datos
                print(f"{len(datos)} registros importados.")
        elif op == "6":
            validos, invalidos = validar_todos(registros)
            print(f"Válidos: {len(validos)} | Inválidos: {len(invalidos)}")
            for r, errs in invalidos:
                print(r, "->", "; ".join(errs))
        elif op in ("7", "8", "9"):
            if col is None:
                col = conectar_mongo()
            if col is None:
                continue
            try:
                if op == "7":
                    insertar_validados(col, registros)
                elif op == "8":
                    consultas_mongo(col)
                else:
                    consultar_por_id(col, input("ID a buscar (ej. ID-001): ").strip())
            except Exception as e:
                print(f"Error en MongoDB: {e}")
                log(f"ERROR MongoDB: {e}")
        elif op == "0":
            log("Programa finalizado")
            print("Hasta luego.")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
