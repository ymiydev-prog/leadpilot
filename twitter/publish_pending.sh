#!/bin/bash
# Publicar thread pendiente de Elon
cd /root/.openclaw/workspace/twitter

# Verificar si hay thread pendiente
if [ -f "approval_pending.json" ] || [ -f "draft_thread.json" ]; then
    echo "Publicando thread pendiente..."
    
    # Usar el publisher
    python3 thread_publisher.py 2>&1
    
    echo "Publicación completada"
else
    echo "No hay thread pendiente"
fi