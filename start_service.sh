#!/bin/bash

# Iniciar o serviço Flask em segundo plano
python3 service.py &

# Aguardar o serviço subir
echo "Aguardando o serviço inicializar..."
sleep 5

# Definir o modelo a ser carregado
MODEL_NAME="meta-llama/Meta-Llama-3-8B-Instruct" # Substitua pelo nome do modelo correto

# Chamar o endpoint /load para carregar o modelo
echo "Chamando o endpoint /load para carregar o modelo..."
curl -X POST http://10.2.50.30:5002/load \
     -H "Content-Type: application/json" \
     -d "{\"model\": \"$MODEL_NAME\"}"

# Manter o processo rodando para não encerrar o contêiner
wait