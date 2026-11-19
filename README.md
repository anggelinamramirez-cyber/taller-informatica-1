# Taller Informática 1 – Unidades 3 y 4

Sistema en Python para gestionar registros biomédicos (signos vitales):
generación, ordenamiento, validación con regex, archivos TXT/CSV/JSON,
organización con `pathlib`/`shutil`, log y almacenamiento en MongoDB Atlas.

## Formato de los registros

|Campo|Formato|Ejemplo|
|-|-|-|
|id|`ID-###`|ID-001|
|fr (edad)|`## Años`|18 Años|
|fc|`###ppm`|090ppm|
|spo2|`##%`|95%|

## Instalación

```bash
pip install -r requirements.txt
export MONGO\_URI="mongodb+srv://USUARIO:CLAVE@cluster.mongodb.net/"   # Windows: set MONGO\_URI=...
python main.py
```

## Estructura

```
main.py
data/txt/datos.txt
data/csv/datos.csv
data/json/datos.json, resultados\_mongo.json
log.txt
```

## Menú

1. Generar 50 registros aleatorios
2. Ingresar registro manual (validado con regex)
3. Ordenar por frecuencia cardiaca (Merge Sort propio)
4. Exportar TXT, CSV y JSON (se mueven automáticamente a `data/`)
5. Importar JSON
6. Validar datos
7. MongoDB: insertar validados en la colección `signos\_vitales`
8. MongoDB: promedio de FC y documentos con SpO2 < 94 → `resultados\_mongo.json`
9. MongoDB: consultar por ID

## Autor

Maria Anggelina Benitez Ramirez – Informática 1, Universidad de Antioquia

