#!/usr/bin/env python3
"""Gera um áudio por cena com a API do ElevenLabs (só biblioteca padrão).

Uso:
  export ELEVENLABS_API_KEY=...        # nunca coloque a chave no código
  python3 tts_elevenlabs.py roteiro.json --voice-id SEU_VOICE_ID --out audios/

roteiro.json:
  {"scenes": [{"narration": "Texto da cena 1"}, {"narration": "Texto da cena 2"}]}

Saída: audios/a1.mp3, audios/a2.mp3, ...
"""
import argparse, json, os, sys, time, urllib.request, urllib.error

API = "https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128"


def tts(text, voice, model, stability, similarity, key):
    body = json.dumps({
        "text": text,
        "model_id": model,
        "voice_settings": {"stability": stability, "similarity_boost": similarity},
    }).encode()
    req = urllib.request.Request(API.format(voice=voice), data=body, method="POST",
                                 headers={"xi-api-key": key, "Content-Type": "application/json",
                                          "Accept": "audio/mpeg"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="ignore")
            if e.code == 429 and attempt < 3:
                time.sleep(3 * (attempt + 1)); continue
            sys.exit(f"ElevenLabs HTTP {e.code}: {msg}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--voice-id", required=True)
    ap.add_argument("--model", default="eleven_v4")
    ap.add_argument("--stability", type=float, default=0.5)
    ap.add_argument("--similarity", type=float, default=1.0)
    ap.add_argument("--out", default="audios")
    a = ap.parse_args()
    key = os.environ.get("ELEVENLABS_API_KEY") or sys.exit("Defina ELEVENLABS_API_KEY no ambiente.")
    scenes = json.load(open(a.script, encoding="utf-8"))["scenes"]
    os.makedirs(a.out, exist_ok=True)
    for i, s in enumerate(scenes, 1):
        path = os.path.join(a.out, f"a{i}.mp3")
        open(path, "wb").write(tts(s["narration"], a.voice_id, a.model, a.stability, a.similarity, key))
        print("ok", path)


if __name__ == "__main__":
    main()
