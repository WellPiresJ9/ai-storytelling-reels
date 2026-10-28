Scripts da skill (Python 3, só biblioteca padrão + ffmpeg):
- tts_elevenlabs.py: um mp3 por cena via API do ElevenLabs (chave em ELEVENLABS_API_KEY).
- assemble.py: monta o Reels (corte por fala, legenda ASS queimada, card de CTA, loudnorm).
Rode com o próprio arquivo de projeto: `python3 scripts/assemble.py projeto.json --out reels.mp4`.
