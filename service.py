import os
import torch
import logging
import traceback
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_classful import FlaskView, route
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

model = None
tokenizer = None
an_pipeline = None

class ObjectReadabilityService(FlaskView):
    def __init__(self):
        self.logger = self.initialize_logger()

    def initialize_logger(self):
        """Inicializa e configura o logger para a aplicação."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger
    
    @route('/', methods=['GET'])
    def index(self):
        return jsonify({'message': 'Object Readability Service', 'status': 0}), 200

    @route('/status', methods=['GET'])
    def get_status(self):
        return jsonify({'message': 'success', 'status': 0}), 200
    
    @route('/load', methods=['POST'])
    def load(self):
        global model, tokenizer, an_pipeline
        data = request.get_json()
        model_name = data.get('model')
        load_dotenv()
        
        if not model_name:
            return jsonify({'message': 'Missing or empty parameter: "model"', 'status': 1}), 400
    
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        
        try:
            model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=quantization_config, token=os.getenv('TOKEN_HF'))
            tokenizer = AutoTokenizer.from_pretrained(model_name, token=os.getenv('TOKEN_HF'))
            
            an_pipeline = pipeline(
                model=model,
                tokenizer=tokenizer,
                task="text-generation",
                temperature=0.1,
                max_new_tokens=512,
                do_sample=True,
                repetition_penalty=1.2,
                return_full_text=False
            )
            
            self.logger.info("Modelo e tokenizador carregados com sucesso.")
            return jsonify({'message': 'Model and tokenizer loaded successfully', 'status': 0}), 200

        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo: {e}")
            self.logger.error(traceback.format_exc())
            return jsonify({'message': 'Error loading model', 'status': 1}), 500
            
    @route('/object_analysis', methods=['POST'])
    def object_analysis(self):
        global an_pipeline
        
        data = request.get_json()
        object_text = data.get('objeto')
        
        if not object_text:
            return jsonify({'message': 'Missing or empty parameter: "objeto"', 'status': 1}), 400
        
        try:
            self.logger.info("Verificando a legibilidade do objeto...")
            
            with torch.no_grad():
                llm = HuggingFacePipeline(pipeline = an_pipeline)
                chat_model = ChatHuggingFace(llm = llm)

                prompt = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            "Assuma o papel de um auditor de controle externo especializado em avaliar a legibilidade de documentos oficiais, com foco na seção 'Objeto' de editais de licitação. Seu objetivo é analisar os textos desses objetos de licitação com base nos seguintes critérios: Verifique se o texto é claro e direto, identificando eventuais redundâncias ou complexidades desnecessárias que possam prejudicar a compreensão. Detecte possíveis contradições ou inconsistências no texto. Avalie a facilidade de leitura e compreensão do objeto, verificando se é possível identificar com clareza que produto está sendo licitado.",
                        ),
                        MessagesPlaceholder(variable_name="chat_history"),
                        ("human", "{input}"),
                    ]
                )
                
                chain = prompt | chat_model | StrOutputParser()
                
                demo_ephemeral_chat_history_for_chain = ChatMessageHistory()
                chain_with_message_history = RunnableWithMessageHistory(
                    chain,
                    lambda session_id: demo_ephemeral_chat_history_for_chain,
                    input_messages_key="input",
                    history_messages_key="chat_history",
                )
                
                response_clf = chain_with_message_history.invoke(
                    {"input": f"Classifique a legibilidade do seguinte objeto de licitação como 'baixa', 'média' ou 'alta'. Responda apenas com a classificação, sem nenhum comentário adicional. Texto do objeto de licitação: \n\n{object_text}"},
                    {"configurable": {"session_id": "unused"}},
                )

                response_justify = chain_with_message_history.invoke(
                    {"input": "Forneça uma justificativa para a sua avaliação, com base nos critérios. O texto de justificativa deve ser conciso e conter no máximo 512 tokens."},
                    {"configurable": {"session_id": "unused"}}
                )
                
                response_json = {
                    'clf_legibilidade': response_clf,
                    'justificativa': response_justify
                }
            
            return jsonify({'message': 'success', 'status': 0, 'output': response_json}), 200
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar objeto: {e}")
            self.logger.error(traceback.format_exc())
            return jsonify({'message': 'Error processing object', 'status': 1}), 500
        
        finally:
            torch.cuda.empty_cache()

app = Flask(__name__)
ObjectReadabilityService.register(app, route_base='/')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5002)
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--debug', type=bool, default=False)
    args = parser.parse_args()

    print('Running Object Readability Service...')
    print(f'Host: {args.host}')
    print(f'Port: {args.port}')
    print(f'Debug: {args.debug}')
    app.run(debug=args.debug, port=args.port, host=args.host)