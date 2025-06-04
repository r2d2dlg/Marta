#!/bin/bash

# Script para desplegar la app Next.js en Google Cloud Run
# Uso: ./deploy-cloudrun.sh

# Configura estos valores antes de ejecutar
SERVICE_NAME="marta-webapp"           # Cambia el nombre si lo deseas
REGION="us-central1"                 # Cambia la región si lo deseas
PORT=9002                             # Puerto expuesto por la app

# Si necesitas variables de entorno, agrégalas aquí, por ejemplo:
# ENV_VARS="VAR1=valor1,VAR2=valor2"
ENV_VARS=""

# Despliegue
if [ -n "$ENV_VARS" ]; then
  gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --port "$PORT" \
    --set-env-vars "$ENV_VARS"
else
  gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --port "$PORT"
fi

echo "\nDespliegue iniciado. Cuando termine, Google te dará la URL pública de tu app."
echo "Recuerda agregar esa URL como redirección autorizada en Google Cloud Console para OAuth." 