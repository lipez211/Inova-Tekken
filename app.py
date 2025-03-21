from flask import Flask, request, jsonify
import base64
import os
from openai import OpenAI

# Configuração da API da OpenAI (NÃO exponha a chave em código público)
os.environ["OPENAI_API_KEY"] = "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"

# Inicializa o cliente da OpenAI
client = OpenAI()

# Configurações do Flask
app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "Nenhum arquivo foi enviado"}), 400  # Código 400 se não houver arquivo

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "Nome de arquivo inválido"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    return jsonify({"message": f"Upload concluído: {file.filename}"}), 200

if __name__ == '__main__':
    app.run(debug=True)

def analyze_image(image_path):
    """ Envia a imagem para análise na OpenAI e retorna o resultado """

    # Converte a imagem para base64
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    # Solicitação para a API da OpenAI
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Você é um sistema de IA que analisa incêndios em plantações de cana. Identifique sinais de fogo, fumaça e áreas queimadas nesta imagem."
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ]
    )

    # Retorna a resposta da OpenAI
    return completion.choices[0].message.content

if __name__ == "__main__":
    app.run(debug=True)
