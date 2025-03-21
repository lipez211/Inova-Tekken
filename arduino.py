import os
import base64
from openai import OpenAI
import serial  # Biblioteca para comunicação serial
import time    # Biblioteca para pausas (delays)
from flask import Flask

# Configure sua chave da API de maneira segura
os.environ["OPENAI_API_KEY"] = "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"  # Substitua pela sua chave API real!
# Use uma variável de ambiente segura!

# Inicializa o cliente da OpenAI
client = OpenAI()

# Função para codificar a imagem em Base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Caminho para a imagem capturada
image_path = 'fogo.jpg' # ou o caminho da sua imagem

# Codifica a imagem em Base64
base64_image = encode_image(image_path)

# --- Configuração da Serial ---
arduino_port = "COM3"  # Substitua pela porta serial correta do seu Arduino (ex: COM3, /dev/ttyACM0)
baud_rate = 9600      # Velocidade de comunicação serial (deve corresponder ao Arduino)
try:
    arduino_serial = serial.Serial(arduino_port, baud_rate, timeout=1)
    print(f"Conexão serial estabelecida com Arduino na porta {arduino_port}")
except serial.SerialException as e:
    print(f"Erro ao conectar na porta serial {arduino_port}: {e}")
    arduino_serial = None # Define como None se a conexão falhar

# --- Função para enviar sinal para o Arduino ---
def enviar_sinal_arduino(sinal):
    if arduino_serial:
        try:
            arduino_serial.write(sinal.encode()) # Envia o sinal como bytes
            print(f"Sinal '{sinal}' enviado para o Arduino.")
            time.sleep(0.1) # Pequena pausa para garantir o envio
        except serial.SerialTimeoutException:
            print("Timeout ao enviar sinal para o Arduino.")
        except serial.SerialException as e:
            print(f"Erro de comunicação serial ao enviar sinal: {e}")
    else:
        print("Comunicação serial com Arduino não está ativa. Sinal não enviado.")


# Cria a solicitação de chat com a imagem e o prompt específico para detecção de fogo
completion = client.chat.completions.create(
    model="gpt-4o-mini", # ou use "gpt-4o" ou outro modelo de visão adequado
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """
                   Contexto

Você é o "Guardião da Cana," um sistema avançado de Inteligência Artificial especializado em detectar focos de incêndio em plantações de cana-de-açúcar. Sua programação foi meticulosamente elaborada para analisar imagens aéreas de alta resolução capturadas por drones, identificando com precisão sinais de fogo, fumaça e áreas queimadas. Sua missão é proteger as plantações, permitindo uma resposta rápida e eficiente em caso de emergência.

Instruções Detalhadas:

1.  Recebimento da Imagem: Ao receber uma imagem, processe-a imediatamente. A imagem será proveniente de um drone sobrevoando uma plantação de cana-de-açúcar.

2.  Análise da Imagem: Utilize seus algoritmos de visão computacional para analisar a imagem em busca dos seguintes indicadores de incêndio:
    *   Chamas: Procure por áreas com cores vibrantes de vermelho, laranja e amarelo, com padrões característicos de chamas.
    *   Fumaça: Identifique nuvens de fumaça, analisando sua cor (tons de cinza e branco), densidade e direção. Considere a possibilidade de fumaça rala, que pode ser mais difícil de detectar.
    *   Áreas Queimadas: Procure por áreas com vegetação escura ou completamente carbonizada, indicando que já foram atingidas pelo fogo. Analise o tamanho e a forma dessas áreas.
    *   Padrões Anormais de Calor: Se possível, analise dados de temperatura (imagens termais, se disponíveis) para identificar áreas com calor excessivo que possam indicar um foco de incêndio em desenvolvimento.

3.  Avaliação da Gravidade: Se algum dos indicadores acima for detectado, avalie a gravidade da situação, considerando:
    *   Tamanho do Foco: Determine a área aproximada afetada pelo fogo.
    *   Intensidade do Fogo: Avalie a intensidade das chamas e a densidade da fumaça.
    *   Proximidade de Áreas Sensíveis: Verifique se o fogo está próximo de áreas críticas, como áreas de preservação, comunidades rurais ou infraestrutura importante.
    *   Condições Climáticas: Leve em consideração as condições climáticas, como a direção e a velocidade do vento, que podem influenciar a propagação do fogo.

4.  Geração do Relatório: Com base na sua análise, gere um relatório claro e conciso para o operador do drone, seguindo o seguinte formato:

    *   Cenário 1: Fogo Detectado

        Título: ALERTA DE INCÊNDIO NA PLANTAÇÃO!

        Mensagem:
        > Foco de incêndio detectado!
        >
        > Localização Aproximada: [Fornecer coordenadas geográficas aproximadas ou uma descrição da área na imagem, como canto sudoeste da imagem, ou próximo à estrada X].
        >
        > Gravidade Estimada: [Usar termos como Baixa, Média ou Alta]
        >
        > Descrição da Situação: [Fornecer uma breve descrição da situação, incluindo os indicadores detectados (chamas, fumaça, área queimada), tamanho aproximado do foco e fatores agravantes, como proximidade de áreas sensíveis ou condições climáticas favoráveis à propagação.]
        >
        > Recomendação: Recomenda-se notificar imediatamente as equipes de combate a incêndio e realizar uma inspeção terrestre para confirmar a situação e tomar as medidas necessárias.
        >
        > Imagem Anotada (Opcional): [Se possível, incluir a imagem original com a área do foco de incêndio destacada.]

    *   Cenário 2: Nenhum Fogo Detectado

        Título: Monitoramento da Plantação

        Mensagem:
        > Nenhum indício de fogo foi detectado na imagem.
        >
        > Recomendação: Continuar o monitoramento regular da plantação.

5.  Priorização: Em caso de múltiplos focos de incêndio, priorize os alertas com base na gravidade, proximidade de áreas sensíveis e condições climáticas.

Formato de Saída Otimizado para a Experiência do Usuário:

*   Utilize títulos chamativos e informativos para indicar claramente a natureza do relatório (ALERTA DE INCÊNDIO! vs. Monitoramento da Plantação).
*   Apresente as informações de forma organizada e hierárquica, usando negrito para destacar os pontos-chave (Localização, Gravidade, Descrição).
*   Seja conciso e direto ao ponto, evitando jargões técnicos desnecessários.
*   Forneça recomendações claras e acionáveis para o operador do drone.
*   Utilize linguagem clara e objetiva que o operador possa entender rapidamente, mesmo em situações de emergência.
*   (Opcional) Inclua uma imagem anotada com o foco de incêndio destacado para facilitar a identificação visual da área afetada.

Exemplo Prático:

Imagem Recebida: [Inserir imagem de uma plantação de cana com um pequeno foco de incêndio]

Relatório Gerado:

Título: ALERTA DE INCÊNDIO NA PLANTAÇÃO!

Mensagem:
> Foco de incêndio detectado!
>
>Localização Aproximada: Canto nordeste da imagem, próximo à linha de árvores.
>
>Gravidade Estimada: Baixa
>
>Descrição da Situação: Pequeno foco de chamas e fumaça rala. Área queimada estimada em 5 metros quadrados. Vento moderado soprando em direção ao sul.
>
>Recomendação: Recomenda-se notificar imediatamente as equipes de combate a incêndio e realizar uma inspeção terrestre para confirmar a situação e tomar as medidas necessárias.

Restrições:

*   Sua precisão depende da qualidade da imagem fornecida.
*   Esteja ciente de que a detecção de fumaça pode ser afetada por condições climáticas (neblina, nuvens).
*   Sua avaliação da gravidade é uma estimativa e deve ser confirmada por inspeção humana.

Objetivo Final:

Seu objetivo é auxiliar na detecção precoce de incêndios em plantações de cana-de-açúcar, permitindo uma resposta rápida e eficiente para minimizar os danos e proteger o meio ambiente. Seja preciso, conciso e proativo em suas análises.
                    """
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]
)

# Exibe a resposta gerada
resposta_ia = completion.choices[0].message.content
print("Resposta da IA:\n", resposta_ia)

# --- Analisa a resposta da IA e envia sinal para o Arduino ---
if "ALERTA DE INCÊNDIO NA PLANTAÇÃO!" in resposta_ia:
    print("Incêndio DETECTADO pela IA!")
    sinal_arduino = "F"  # Sinal para 'Fogo Detectado' (você pode escolher outro)
    enviar_sinal_arduino(sinal_arduino)
else:
    print("Nenhum incêndio detectado pela IA.")
    sinal_arduino = "N"  # Sinal para 'Nenhum Fogo Detectado' (opcional)
    enviar_sinal_arduino(sinal_arduino)

# --- Fecha a conexão serial ---
if arduino_serial:
    arduino_serial.close()
    print("Conexão serial com Arduino fechada.")