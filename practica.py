import asyncio
import aiohttp
import time
import json
from datetime import datetime

FUENTES = [
    ("edad_nombre", "https://api.agify.io?name=laura"),
    ("cambio_divisas", "https://api.exchangerate.host/latest?base=EUR&symbols=USD,GBP,JPY,CHF"),
    ("bitcoin", "https://api.coindesk.com/v1/bpi/currentprice.json"),
    ("genero_nombre", "https://api.genderize.io?name=andrea"),
    ("universo", "https://api.le-systeme-solaire.net/rest/bodies/mars")
]

HEADERS = {"Accept": "application/json"}

async def obtener_articulo(session, nombre, url):
    for intento in range(3):
        try:
            async with session.get(url, headers=HEADERS, timeout=5) as resp:
                if resp.status != 200:
                    raise Exception(f"Código de estado HTTP {resp.status}")
                data = await resp.json()
                return estandarizar(nombre, data)
        except Exception as e:
            print(f"[⚠️  Reintento {intento+1}] Error en '{nombre}': {e}")
            await asyncio.sleep(1.5 * (intento + 1))
    return None

def estandarizar(nombre, data):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if nombre == "edad_nombre":
        return {
            "titulo": "Estimación de edad para el nombre 'Laura'",
            "fecha": fecha,
            "contenido": f"Edad estimada: {data.get('age', 'N/A')} años (basado en {data.get('count', 'N/A')} registros)"
        }
    elif nombre == "cambio_divisas":
        tasas = data.get("rates")
        if tasas:
            contenido = "\n".join(f"1 EUR = {valor:.2f} {moneda}" for moneda, valor in tasas.items())
        else:
            contenido = "No se pudieron obtener tasas de cambio."
        return {
            "titulo": "Tipos de cambio frente al Euro",
            "fecha": fecha,
            "contenido": contenido
        }
    elif nombre == "bitcoin":
        info = data.get("bpi", {}).get("USD", {})
        return {
            "titulo": "Precio actual del Bitcoin",
            "fecha": fecha,
            "contenido": f"1 BTC = {info.get('rate', 'N/A')} USD"
        }
    elif nombre == "genero_nombre":
        return {
            "titulo": "Probabilidad de género para el nombre 'Andrea'",
            "fecha": fecha,
            "contenido": f"Género más probable: {data.get('gender', 'N/A')} ({int(data.get('probability', 0) * 100)}%)"
        }
    elif nombre == "universo":
        masa = data.get('mass', {})
        return {
            "titulo": "Información sobre el planeta Marte",
            "fecha": fecha,
            "contenido": f"Gravedad: {data.get('gravity', 'N/A')} m/s²\nMasa: {masa.get('massValue', '?')}e{masa.get('massExponent', '')} kg"
        }
    else:
        return {
            "titulo": f"Datos de {nombre}",
            "fecha": fecha,
            "contenido": json.dumps(data)[:300]
        }

async def enviar_al_servidor(articulo):
    try:
        await asyncio.sleep(0.1)
        print("\n--- Envío de artículo ---")
        print(f"Título     : {articulo['titulo']}\nFecha      : {articulo['fecha']}\nContenido  :\n{articulo['contenido']}\n")
    except Exception as e:
        print(f"❌ Error al enviar artículo: {e}")

async def main():
    inicio = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        tareas = [obtener_articulo(session, nombre, url) for nombre, url in FUENTES]
        resultados = await asyncio.gather(*tareas)

        articulos = [res for res in resultados if res is not None]
        await asyncio.gather(*(enviar_al_servidor(a) for a in articulos))

    fin = time.perf_counter()
    print("\n=== RESUMEN DE EJECUCIÓN ===")
    print(f"📝 Total de artículos procesados : {len(articulos)}")
    print(f"⏱️  Tiempo total de ejecución   : {fin - inicio:.2f} segundos")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario")
