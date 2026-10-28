# Arquivos do projeto

Estrutura de pastas:
```
meu-reels/
  roteiro.json      # texto narrado de cada cena (entrada do tts_elevenlabs.py)
  projeto.json      # montagem (entrada do assemble.py)
  audios/a1.mp3 ... a6.mp3
  cenas/c1.mp4 ... c6.mp4
  fonts/            # opcional: Montserrat-*.ttf
```

## roteiro.json
```json
{
  "scenes": [
    {"narration": "Esse é o Dono. A empresa dele vai muito bem. Mas só funciona quando ele está olhando.",
     "visual": "Manhã no escritório; o dono atrás do balcão cheio de papéis, o celular soltando dezenas de balões de notificação verdes."},
    {"narration": "Quatro da tarde. Reunião ótima, o cliente quer a proposta hoje. Só que o Dono precisa sair. E só ele tem a senha.",
     "visual": "Ele sai correndo com a mochila; o sócio tenta abrir o sistema e aparece um cadeado gigante na tela."}
  ]
}
```

## projeto.json
```json
{
  "scenes": [
    {"video": "cenas/c1.mp4", "audio": "audios/a1.mp3", "video_start": 0,
     "narration": "Esse é o Dono. A empresa dele vai muito bem. Mas só funciona quando ele está olhando.",
     "captions": [["Esse é o Dono.", ""], ["A empresa dele", "vai muito bem."], ["Mas só funciona", "quando ele"], ["está olhando.", ""]]}
  ],
  "cta": {"keyword": "CÉREBRO", "top_line": "COMENTA", "trigger": "Comenta"},
  "highlight": ["Dono", "robô", "CÉREBRO", "WhatsApp", "gargalo"],
  "style": {"font": "Montserrat", "fonts_dir": "fonts", "accent_bgr": "1E7BFF"},
  "tempo": 1.07
}
```
- `video_start`: segundo do clipe do Kling onde a cena começa (use para pular um começo fraco).
- `accent_bgr`: cor de destaque no formato BGR do ASS. Laranja = `1E7BFF`, verde = `5BD25B`, azul = `E2A04A`.
- `captions` é opcional; sem ele o script quebra sozinho.

## Bloco fixo de personagem/estilo (cole no fim de TODO prompt do Kling)
```
Same character as the reference image: <descrição física exata: cabelo, pele, barba, óculos sim/não, roupa, acessório>.
Same <estilo da marca: ex. bright, warm, colorful illustrated 3D-cartoon style, golden sunlight, saturated orange/blue/green palette>.
Expressive comedic animation, smooth cinematic camera. No on-screen text, no subtitles, no logos, no talking or lip sync. Vertical 9:16.
```
