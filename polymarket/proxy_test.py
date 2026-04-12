import requests
import json

# Lista de proxies gratuitos para probar
PROXIES = [
    # Japón
    {"http": "http://163.49.156.197:3128", "https": "http://163.49.156.197:3128"},
    {"http": "http://160.202.46.9:8080", "https": "http://160.202.46.9:8080"},
    # Singapur
    {"http": "http://103.214.112.50:8080", "https": "http://103.214.112.50:8080"},
    # Alternativos
    {"http": "http://185.162.228.219:80", "https": "http://185.162.228.219:80"},
]

def test_proxy(proxy, name):
    """Probar proxy con Polymarket API"""
    try:
        print(f"Probando {name}...")
        resp = requests.get(
            "https://gamma-api.polymarket.com/markets?limit=1",
            proxies=proxy,
            timeout=10
        )
        if resp.status_code == 200:
            print(f"  ✅ {name} FUNCIONA!")
            return True
        else:
            print(f"  ❌ {name}: Status {resp.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ {name}: {str(e)[:50]}")
        return False

print("=== Buscando Proxy Funcional para Polymarket ===")
print()

# Probar sin proxy primero
print("1. Sin proxy (directo):")
try:
    resp = requests.get("https://gamma-api.polymarket.com/markets?limit=1", timeout=10)
    print(f" Status: {resp.status_code}")
    if resp.status_code == 200:
        print("  ❌ Bloqueo geográfico detectado")
    else:
        print(f"  Respuesta: {resp.status_code}")
except Exception as e:
    print(f" Error: {str(e)[:50]}")

print()
print("2. Proxies gratuitos:")

for i, proxy in enumerate(PROXIES):
    name = f"Proxy {i+1}"
    if test_proxy(proxy, name):
        print()
        print(f"🎉 Proxy {i+1} funciona! Guardando configuración...")# Guardar proxy funcional
        with open("/root/.openclaw/workspace/polymarket/working_proxy.txt", "w") as f:
            json.dump(proxy, f)
        print("Proxy guardado en: working_proxy.txt")
        break
else:
    print()
    print("Ningún proxy gratuito funciona.")
    print("Necesitamos ProtonVPN u otro método.")
