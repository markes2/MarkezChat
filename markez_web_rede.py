"""
Interface de chat no estilo ChatGPT, rodando no navegador.
Usa o Ollama (IA gratuita local) por baixo dos panos.

ANTES DE USAR:
1. Instale o Ollama: https://ollama.com
2. No terminal, rode: ollama pull llama3.2
3. Instale as bibliotecas: py -m pip install flask requests
4. Rode este arquivo: py markez_web.py
5. Abra o navegador em: http://localhost:5000
"""

try:
    from flask import Flask, render_template_string, request, jsonify
    import requests
except ImportError as e:
    print(f"ERRO: falta instalar uma biblioteca ({e}).")
    print("Abra o terminal e rode: py -m pip install flask requests")
    input("\nPressione Enter para sair...")
    exit()

app = Flask(__name__)

MODELO = "llama3.2"
OLLAMA_URL = "http://localhost:11434/api/chat"

historico = []

PAGINA_HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Markez Chat</title>
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: Segoe UI, Arial, sans-serif;
    background-color: #212121;
    color: #e5e5e5;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }
  header {
    padding: 16px 24px;
    background-color: #171717;
    font-size: 18px;
    font-weight: 600;
    border-bottom: 1px solid #2f2f2f;
  }
  #chat {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .msg {
    max-width: 70%;
    padding: 12px 16px;
    border-radius: 12px;
    line-height: 1.5;
    white-space: pre-wrap;
  }
  .user {
    align-self: flex-end;
    background-color: #2f2f2f;
  }
  .ia {
    align-self: flex-start;
    background-color: #171717;
    border: 1px solid #2f2f2f;
  }
  #area-input {
    padding: 16px 24px 24px;
    display: flex;
    gap: 12px;
    background-color: #212121;
  }
  #pergunta {
    flex: 1;
    padding: 12px 16px;
    border-radius: 24px;
    border: 1px solid #3f3f3f;
    background-color: #2f2f2f;
    color: #e5e5e5;
    font-size: 15px;
    outline: none;
  }
  #enviar {
    padding: 12px 20px;
    border-radius: 24px;
    border: none;
    background-color: #10a37f;
    color: white;
    font-weight: 600;
    cursor: pointer;
  }
  #enviar:hover { background-color: #0d8f6f; }
  #enviar:disabled { background-color: #555; cursor: not-allowed; }
</style>
</head>
<body>
  <header>Markez Chat</header>
  <div id="chat"></div>
  <div id="area-input">
    <input type="text" id="pergunta" placeholder="Digite sua mensagem..." autofocus>
    <button id="enviar">Enviar</button>
  </div>

<script>
const chat = document.getElementById('chat');
const input = document.getElementById('pergunta');
const botao = document.getElementById('enviar');

function adicionarMensagem(texto, quemFalou) {
  const div = document.createElement('div');
  div.className = 'msg ' + quemFalou;
  div.textContent = texto;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

async function enviarMensagem() {
  const texto = input.value.trim();
  if (!texto) return;

  adicionarMensagem(texto, 'user');
  input.value = '';
  botao.disabled = true;

  try {
    const resposta = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mensagem: texto })
    });
    const dados = await resposta.json();
    adicionarMensagem(dados.resposta, 'ia');
  } catch (erro) {
    adicionarMensagem('Erro ao conectar com a IA. Verifique se o Ollama esta aberto.', 'ia');
  } finally {
    botao.disabled = false;
    input.focus();
  }
}

botao.addEventListener('click', enviarMensagem);
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') enviarMensagem();
});
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(PAGINA_HTML)


@app.route("/chat", methods=["POST"])
def chat():
    global historico
    dados = request.get_json()
    mensagem = dados.get("mensagem", "")

    historico.append({"role": "user", "content": mensagem})

    try:
        resposta = requests.post(OLLAMA_URL, json={
            "model": MODELO,
            "messages": historico,
            "stream": False
        })
        resposta.raise_for_status()
        resultado = resposta.json()
        texto_resposta = resultado["message"]["content"]
        historico.append({"role": "assistant", "content": texto_resposta})
        return jsonify({"resposta": texto_resposta})
    except requests.exceptions.ConnectionError:
        return jsonify({"resposta": "Nao consegui conectar ao Ollama. Verifique se ele esta aberto no seu PC."})
    except Exception as e:
        return jsonify({"resposta": f"Ocorreu um erro: {e}"})


if __name__ == "__main__":
    try:
        print("=== Markez Chat ===")
        print("Abra o navegador e acesse: http://localhost:5000")
        print("Para parar, feche esta janela ou aperte Ctrl+C.\n")
        app.run(host="0.0.0.0", port=5000, debug=False)
    except Exception as e:
        print(f"\nOcorreu um erro ao iniciar: {e}")
        input("\nPressione Enter para sair...")
