# Usar a imagem base da NVIDIA com CUDA 12.3 e cuDNN 9
FROM nvidia/cuda:12.3.2-cudnn9-devel-ubuntu20.04

# Definir o diretório de trabalho no contêiner
WORKDIR /app

# Definir o fuso horário para evitar interação durante a instalação
ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Atualizar o repositório e instalar dependências essenciais
RUN apt-get update && apt-get install -y \
    software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
    python3.9 \
    python3.9-distutils \
    python3-pip \
    curl && \
    rm -rf /var/lib/apt/lists/*

# Definir o Python 3.9 como padrão
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1

# Atualizar o pip diretamente
RUN python3 -m pip install --upgrade pip

# Copiar o arquivo de requisitos do projeto para o container
COPY requirements.txt .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código para o diretório de trabalho
COPY . .

# Copiar o shell script para dentro do contêiner
COPY start_service.sh /start_service.sh

# Tornar o script executável
RUN chmod +x /start_service.sh

# Expor a porta usada pelo Flask
EXPOSE 5002

# Comando para rodar o shell script
CMD ["/start_service.sh"]
