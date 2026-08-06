import os
from flask import Flask,request,jsonify,render_template_string
import requests
app=Flask(__name__)
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
URL="https://api.groq.com/openai/v1/chat/completions"
MODEL="llama-3.3-70b-versatile"
HTML="<h2>Markez Chat (Groq)</h2><div id=c></div><input id=m><button onclick=s()>Enviar</button><script>async function s(){let t=m.value;let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mensagem:t})});let j=await r.json();c.innerHTML+='<p><b>Você:</b>'+t+'</p><p><b>IA:</b>'+j.resposta+'</p>';}</script>"
@app.route("/")
def h(): return render_template_string(HTML)
@app.route("/chat",methods=["POST"])
def ch():
    if not GROQ_API_KEY: return jsonify({"resposta":"Configure GROQ_API_KEY no Render."})
    msg=request.json.get("mensagem","")
    hd={"Authorization":"Bearer "+GROQ_API_KEY,"Content-Type":"application/json"}
    pl={"model":MODEL,"messages":[{"role":"user","content":msg}]}
    rr=requests.post(URL,headers=hd,json=pl,timeout=60)
    if rr.status_code!=200: return jsonify({"resposta":rr.text})
    return jsonify({"resposta":rr.json()["choices"][0]["message"]["content"]})
if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000)
