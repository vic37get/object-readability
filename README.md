# Legibilidade de Objetos de Licitação

## Objetivo

Este repositório contém um pipeline para classificar a legibilidade da seção **OBJETO** de um edital de licitação. O modelo atribui uma das seguintes categorias:

- **Baixa**
- **Média**
- **Alta**

A classificação reflete o quão compreensível é o texto em termos de completude e facilidade de entendimento. Além disso, o modelo fornece uma justificativa para a classificação atribuída.

## Tecnologias Utilizadas

- **Python**
- **Flask** (para a API)
- **LangChain** (para processamento de linguagem natural)
- **Google Gemini API** (para geração de respostas)
- **Docker** (para conteinerização)

## Instalação e Execução

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/object-readability.git
cd object-readability
```

### 2. Configurar as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto e defina sua chave de API do Google:

```
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Construir e Rodar o Container Docker

```bash
docker build -t object-readability .
docker run -d --env-file=.env --restart always -p 5002:5002 --name object-readability object-readability
```

A API estará rodando em `http://localhost:5002`.

## Uso da API

### Verificar Status

```bash
curl -X GET http://localhost:5002/status
```

**Resposta esperada:**

```json
{
  "message": "success",
  "status": 0
}
```

### Analisar um Objeto de Licitação

Envie um JSON com o campo `objeto` contendo o texto a ser analisado:

```bash
curl -X POST http://localhost:5002/object_analysis \
     -H "Content-Type: application/json" \
     -d '{"objeto": "Aquisição de materiais de construção para reforma de escola municipal."}'
```

**Resposta esperada:**

```json
{
  "message": "success",
  "status": 0,
  "output": {
    "clf_legibilidade": "Alta",
    "justificativa": "O texto é claro, conciso e apresenta explicitamente o objetivo da licitação sem ambiguidades."
  }
}
```

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.