# Twitter Module - YhasClaw - Instrucciones para Elon

## Estado: ✅ CONFIGURADO

### Credenciales Guardadas
- Bearer Token: ✅ Configurado
- Consumer Key: ✅ Configurado
- Consumer Secret: ✅ Configurado
- Client ID: ✅ Configurado

### Capacidades Disponibles

| Función | Estado | Descripción |
|---------|--------|-------------|
| Search tweets | ✅ | Buscartweets por término |
| Get user info | ✅ | Obtener info de usuarios |
| Read timeline | ✅ | Leer timeline |
| Post tweets | ⚠️ | Requiere permisos Write |
| Like/Retweet | ⚠️ | Requiere permisos Write |

### Límites Twitter API Free Tier

- **Tweets por mes**: 1,500
- **Tweets por día**: ~50
- **Búsquedas**: 450/15 min

### Para Publicar Tweets

El Bearer Token actual es de **solo lectura**.

Para publicar necesitas:
1. Ir a Twitter Developer Portal
2. App Settings → User authentication settings
3. Habilitar OAuth 1.0a
4. Generar Access Token y Secret con permisos de **Read and Write**

### Módulos Creados

```
/workspace/twitter/
├── __init__.py      # Inicialización
├── client.py        # Cliente Twitter API v2
└── config.env       # Credenciales
```

### Uso por Elon

```python
from workspace.twitter import create_elon_agent

agent = create_elon_agent(bearer_token="...")
agent.tweet("Hola mundo desde YhasClaw!")
```