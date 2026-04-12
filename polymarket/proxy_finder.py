import requests
import json
import time

# Lista ampliada de proxies potenciales
PROXY_SOURCES = [
    # Proxies públicos de Japón
    {"host": "163.49.156.197", "port": "3128", "country": "JP"},
    {"host": "160.202.46.9", "port": "8080", "country": "JP"},
    {"host": "36.92.27.162", "port": "8080", "country": "JP"},
    # Proxies de Singapur
    {"host": "103.214.112.50", "port": "8080", "country": "SG"},
    {"host": "45.125.224.138", "port": "8080", "country": "SG"},
    # Proxies de Hong Kong
    {"host": "45.125.224.138", "port": "8080", "country": "HK"},
    # Proxies HTTP alternativos
    {"host": "185.162.228.219", "port": "80", "country": "EU"},
]

def test_polymarket_access(proxy=None, name="Direct"):
    """Probar acceso a Polymarket CLOB API"""
    url = "https://clob.polymarket.com/markets"
    try:
        if proxy:
            proxies = {
                "http": f"http://{proxy['host']}:{proxy['port']}",
                "https": f"http://{proxy['host']}:{proxy['port']}"
            }
            resp = requests.get(url, proxies=proxies, timeout=15)
        else:
            resp = requests.get(url, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            return {"success": True, "status": resp.status_code, "name": name}
        else:
            return {"success": False, "status": resp.status_code, "name": name}
    except Exception as e:
        return {"success": False, "error": str(e)[:80], "name": name}

print("=== BUSCANDO SOLUCIÓN PARA POLYMARKET ===")
print()
print("1. Probando acceso directo...")
result = test_polymarket_access(name="Directo")
print(f"Directo: {result}")
print()

print("2. Probando proxies públicos...")
working_proxies = []

for p in PROXY_SOURCES:
    result = test_polymarket_access(proxy=p, name=f"{p['country']}-{p['host'][:15]}")
    print(f"{p['country']}: {result}")
    if result.get("success"):
        working_proxies.append(p)
        print(f"✅ FUNCIONA: {p}!")
    time.sleep(1)

print()
if working_proxies:
    print(f"🎉 PROXIES FUNCIONALES: {len(working_proxies)}")
    with open("/root/.openclaw/workspace/polymarket/working_proxy.json", "w") as f:
        json.dump(working_proxies[0], f)
    print(f"Guardado mejor proxy: {working_proxies[0]}")
else:
    print("❌ Ningún proxy público funciona.")
    print()
    print("=== ALTERNATIVAS ===")
    print("1. Usar servicio de proxy pagado (Smartproxy, Luminati)")
    print("2. Configurar OpenVPN manual con config de ProtonVPN")
    print("3. Operar Polymarket manualmente desde dispositivo del Jefe")
