import base64
import os

import requests
from flask import Flask, jsonify, request

KEY = os.environ.get("GNANI_API_KEY")
HEAD = {"X-API-Key-ID": KEY} if KEY else {}

app = Flask(__name__)

ANSWERS = [
    (
        ["जला", "आग", "jala", "burn", "जलाना"],
        "पराली जलाने से हवा खराब होती है और खेत की मिट्टी के जरूरी पोषक तत्व और मित्र कीट नष्ट हो जाते हैं। "
        "पराली को जलाने की जगह खेत में ही मिलाएं या उसका दूसरा उपयोग करें।",
    ),
    (
        ["हैप्पी", "सीडर", "happy", "seeder", "मशीन", "machine", "बुवाई", "गेहूं", "gehu"],
        "हैप्पी सीडर मशीन से पराली हटाए बिना सीधे गेहूं की बुवाई हो जाती है। "
        "मशीन किराए पर कहां मिलेगी, यह अपने ब्लॉक कृषि कार्यालय या कृषि विज्ञान केंद्र से पूछें।",
    ),
    (
        ["खाद", "compost", "decompose", "डीकंपोज", "सड़ा", "सड़ाना"],
        "पराली को डीकंपोजर घोल के साथ खेत में मिलाने से वह सड़कर खाद बन जाती है और मिट्टी की उर्वरता बढ़ती है। "
        "इसमें कुछ हफ्ते लगते हैं, इसलिए कटाई के तुरंत बाद शुरू करें।",
    ),
    (
        ["बेच", "बिक", "sell", "चारा", "fodder", "बायोमास", "biomass", "कमाई", "पैसा"],
        "पराली को पशुओं के चारे के लिए इकट्ठा करके या बायोमास और बिजली संयंत्रों को बेचकर आप कमाई कर सकते हैं। "
        "अपने नजदीकी खरीदार की जानकारी कृषि विज्ञान केंद्र से लें।",
    ),
    (
        ["मिट्टी", "mitti", "soil", "उर्वरता", "जांच"],
        "मिट्टी की जांच अपने कृषि विज्ञान केंद्र या कृषि कार्यालय में कराएं। "
        "जांच की रिपोर्ट के अनुसार ही खाद डालें, इससे पैसे की बचत होती है और फसल अच्छी होती है।",
    ),
    (
        ["कीटनाशक", "दवा", "छिड़काव", "spray", "pesticide"],
        "कीटनाशक छिड़कते समय मुंह पर कपड़ा या मास्क और हाथों में दस्ताने पहनें। "
        "हवा की दिशा में पीठ करके छिड़कें, पैकेट पर लिखी मात्रा ही डालें, और बाद में हाथ-मुंह अच्छी तरह धोएं। "
        "दवा बच्चों से दूर रखें।",
    ),
    (
        ["बीमा", "insurance"],
        "फसल बीमा की जानकारी के लिए अपने बैंक या ब्लॉक कृषि कार्यालय से संपर्क करें। "
        "आवेदन की आखिरी तारीख का ध्यान रखें, क्योंकि समय निकल जाने पर बीमा नहीं मिलता।",
    ),
    (
        ["प्रदूषण", "pollution", "aqi", "एक्यूआई", "धुआं", "मास्क", "mask"],
        "जब हवा में धुआं या प्रदूषण ज्यादा हो, तो सुबह-शाम बाहर की मेहनत कम करें और N95 मास्क पहनें। "
        "बच्चों और बुजुर्गों को घर के अंदर रखें।",
    ),
    (
        ["पराली", "parali", "पुआल", "paddy", "धान", "dhan", "stubble", "क्या करें", "kya"],
        "पराली के तीन अच्छे उपाय हैं। पहला, खेत में मिलाकर खाद बनाएं। दूसरा, हैप्पी सीडर से सीधी बुवाई करें। "
        "तीसरा, चारे या बायोमास के लिए बेचें। इनमें से किसी एक के बारे में और पूछें।",
    ),
]

FALLBACK = (
    "माफ कीजिए, मैं समझ नहीं पाया। आप पूछ सकते हैं: पराली का क्या करें, पराली क्यों न जलाएं, "
    "हैप्पी सीडर क्या है, पराली की खाद कैसे बनाएं, मिट्टी की जांच, कीटनाशक, फसल बीमा, या प्रदूषण।"
)


def pick_answer(text):
    text = (text or "").lower()
    for keywords, answer in ANSWERS:
        if any(keyword.lower() in text for keyword in keywords):
            return answer
    return FALLBACK


@app.post("/ask")
def ask():
    if not KEY:
        return jsonify(error="GNANI_API_KEY is not configured"), 503

    audio_file = request.files["audio"]
    try:
        stt_response = requests.post(
            "https://api.vachana.ai/stt/v3",
            headers=HEAD,
            files={"audio_file": ("q.wav", audio_file.read(), "audio/wav")},
            data={"language_code": "hi-IN"},
            timeout=60,
        )
        if stt_response.status_code != 200:
            return jsonify(error=f"STT {stt_response.status_code}: {stt_response.text[:300]}"), 500

        heard = stt_response.json().get("transcript", "")
        answer = pick_answer(heard)

        tts_response = requests.post(
            "https://api.vachana.ai/api/v1/tts/inference",
            headers={**HEAD, "Content-Type": "application/json"},
            json={"text": answer, "voice": "Nalini", "model": "timbre-v2.5",
                  "language": "hi-IN", "speed": 1.0,
                        "audio_config": {"sample_rate": 48000, "num_channels": 1,
                                               "sample_width": 2, "encoding": "linear_pcm",
                                                                      "container": "wav"}},
            timeout=60,
        )
        if tts_response.status_code != 200:
            return jsonify(error=f"TTS {tts_response.status_code}: {tts_response.text[:300]}"), 500

        return jsonify(
            heard=heard,
            answer=answer,
            audio=base64.b64encode(tts_response.content).decode(),
        )
    except requests.RequestException as error:
        app.logger.exception("Gnani API request failed")
        return jsonify(error=str(error)), 502
    except (ValueError, KeyError) as error:
        app.logger.exception("Invalid response or request data")
        return jsonify(error=str(error)), 500


PAGE = """<!doctype html><html lang="hi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>किसान वाणी</title>
<style>
body{font-family:system-ui,sans-serif;background:#f3f8ee;margin:0;padding:24px;text-align:center;color:#1f3a1f}
h1{margin:8px 0}p.sub{margin-top:0;color:#4a6b4a}
#mic{width:150px;height:150px;border-radius:50%;border:0;background:#2e7d32;color:#fff;font-size:20px;margin:24px 0}
#mic.rec{background:#c62828}
.box{background:#fff;border-radius:12px;padding:14px;margin:12px auto;max-width:480px;text-align:left;min-height:24px}
small{color:#6b7f6b}
</style></head><body>
<h1>🌾 किसान वाणी</h1><p class="sub">पराली के बारे में बोलकर पूछें</p>
<button id="mic">🎤 दबाकर बोलें</button>
<div class="box"><small>आपने कहा</small><div id="heard"></div></div>
<div class="box"><small>जवाब</small><div id="answer"></div></div>
<audio id="player" controls style="width:100%;max-width:480px"></audio>
<script>
const mic=document.getElementById('mic');let rec,chunks=[];
function wavFromBuffer(buf){const d=buf.getChannelData(0),n=d.length,v=new DataView(new ArrayBuffer(44+n*2));
const w=(o,s)=>{for(let i=0;i<s.length;i++)v.setUint8(o+i,s.charCodeAt(i))};
w(0,'RIFF');v.setUint32(4,36+n*2,true);w(8,'WAVEfmt ');v.setUint32(16,16,true);v.setUint16(20,1,true);
v.setUint16(22,1,true);v.setUint32(24,16000,true);v.setUint32(28,32000,true);v.setUint16(32,2,true);
v.setUint16(34,16,true);w(36,'data');v.setUint32(40,n*2,true);
for(let i=0;i<n;i++){const s=Math.max(-1,Math.min(1,d[i]));v.setInt16(44+i*2,s<0?s*0x8000:s*0x7FFF,true)}
return new Blob([v],{type:'audio/wav'})}
async function toWav(blob){const ab=await blob.arrayBuffer();const ctx=new AudioContext();
const dec=await ctx.decodeAudioData(ab);const off=new OfflineAudioContext(1,Math.ceil(dec.duration*16000),16000);
const src=off.createBufferSource();src.buffer=dec;src.connect(off.destination);src.start();
return wavFromBuffer(await off.startRendering())}
async function start(){const s=await navigator.mediaDevices.getUserMedia({audio:true});
rec=new MediaRecorder(s);chunks=[];rec.ondataavailable=e=>chunks.push(e.data);
rec.onstop=async()=>{s.getTracks().forEach(t=>t.stop());
document.getElementById('answer').textContent='सोच रहा हूँ...';
const wav=await toWav(new Blob(chunks));const fd=new FormData();fd.append('audio',wav,'q.wav');
const r=await fetch('/ask',{method:'POST',body:fd});const j=await r.json();
if(j.error){document.getElementById('answer').textContent='Error: '+j.error;return}
document.getElementById('heard').textContent=j.heard;document.getElementById('answer').textContent=j.answer;
const p=document.getElementById('player');p.src='data:audio/wav;base64,'+j.audio;p.play()};
rec.start();mic.classList.add('rec');mic.textContent='⏹ रोकें'}
mic.onclick=()=>{if(rec&&rec.state==='recording'){rec.stop();mic.classList.remove('rec');mic.textContent='🎤 दबाकर बोलें'}else start()};
</script></body></html>"""


@app.get("/")
def home():
    return PAGE


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    print(f"Kisan Vani is starting at http://localhost:{port}", flush=True)
    app.run(host="0.0.0.0", port=port)
