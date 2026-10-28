---
name: storytelling-reels
description: "Use when turning a YouTube video into a storytelling Reel."
version: 1.0.0
author: Well Pires (AI Makers Club) + Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [reels, shorts, storytelling, notebooklm, elevenlabs, higgsfield, kling, ffmpeg]
    related_skills: [youtube-content]
---

# Storytelling Reels: do vídeo longo ao Reels narrado

Transforma um vídeo do YouTube (seu ou de referência) num Reels 9:16 de ~50s: uma história com personagem fixo, narrada com a SUA voz, cenas animadas por IA, legenda queimada e um CTA de palavra-chave no final.

Pipeline: **NotebookLM** (entende o vídeo e ajuda no roteiro) → **ElevenLabs** (1 áudio por cena) → **Higgsfield / Kling** (1 cena por fala) → **ffmpeg** (monta tudo com `scripts/assemble.py`).

## When to Use (quando usar)
- "Transforma esse vídeo num Reels de storytelling"
- Conteúdo sem aparecer na câmera, mas com a sua voz e uma história real
- Série com o mesmo personagem (sempre a mesma cara e estilo)

## O que precisa
| Item | Para quê |
|---|---|
| Conta Google com NotebookLM | Ler o vídeo e construir o roteiro |
| ElevenLabs + uma voz (clone da sua) | Narração. API key em `ELEVENLABS_API_KEY` ou ElevenLabs conectado via MCP/Composio |
| Higgsfield com créditos (Kling) | Gerar as cenas. MCP do Higgsfield conectado ou uso manual no site |
| `ffmpeg` com libass + Python 3 | Montagem. Fonte opcional (ex.: Montserrat do Google Fonts) numa pasta `fonts/` |
| 1 imagem de referência do personagem | Mantém o personagem igual em todas as cenas |

Nunca peça senha ou API key no chat. O usuário faz login no navegador e coloca as chaves no ambiente ou no conector.

## Passo a passo

### 1. Subir o vídeo no NotebookLM
1. Abra notebooklm.google.com (às vezes redireciona para notebook.google.com) e crie um notebook, ex.: "Reels - <tema>".
2. **Adicionar fonte → YouTube** → cole o link do vídeo.
3. Se o agente tem navegador, ele faz isso. Se o clique em "Novo notebook" não responder no navegador do agente, peça para o usuário clicar uma vez e continue dali.
4. Plano B se o NotebookLM falhar: pegue a transcrição (skill `youtube-content`, ou um site de transcrição logado) e siga o passo 2 com o mesmo roteiro de perguntas direto no LLM.

### 2. Conversar com o NotebookLM até ter um roteiro forte
Use a sequência de perguntas de `references/notebooklm-prompts.md`, nesta ordem:
1. **Extrair o case**: quem, o problema, o momento concreto (hora, valor, ferramenta), o custo, a virada, o resultado.
2. **Achar a metáfora** que explica o problema em uma imagem (ex.: "empresa é encanamento; o entupimento era o dono").
3. **Escrever o roteiro em 6 cenas** (formato abaixo).
4. **Cortar**: pedir uma versão 25% mais curta, sem perder números e nomes.

Formato do roteiro (6 cenas, ~120–140 palavras no total, ~50s):
1. **Gancho/personagem**: quem é e qual o problema em 1 frase
2. **Incidente**: um momento concreto com hora/valor
3. **Escalada**: o custo se repetindo (tempo, dinheiro, assinatura)
4. **Virada**: a metáfora, o "aí ele entendeu"
5. **Sistema**: a solução (o robô/IA) funcionando no dia a dia
6. **Resultado + CTA**: o antes e depois, e então `Comenta <PALAVRA> que eu te mando <isca>`

Regras do roteiro:
- História real, tirada do vídeo. Nada inventado.
- Frases curtas. Cada ponto final vira uma pausa e uma troca de legenda.
- **Sem episódios** ("EP 1") e sem votação. O final é sempre um CTA de palavra-chave que entrega algo (aula, template, skill).
- Grave o roteiro em `roteiro.json` (ver `references/projeto-exemplo.md`), com o texto narrado de cada cena e o prompt visual de cada cena.

### 3. Narração com ElevenLabs (1 áudio POR CENA)
Gere um arquivo por cena. Nunca gere uma narração única: a fala atravessa os cortes e a legenda fica fora de sincronia.

```bash
export ELEVENLABS_API_KEY=...
python3 scripts/tts_elevenlabs.py roteiro.json --voice-id SEU_VOICE_ID --model eleven_v4 --stability 0.5 --similarity 1.0 --out audios/
```
- `eleven_v4` aceita só `stability` e `similarity_boost`. O ajuste de estilo/intensidade da clonagem é feito no site.
- Para descobrir o voice_id: ElevenLabs → Vozes → sua voz → "ID", ou `GET /v1/voices`.
- Se o ElevenLabs estiver conectado via MCP/Composio, use a ferramenta TEXT_TO_SPEECH com os mesmos parâmetros, uma chamada por cena (máx. ~3 em paralelo para não tomar 429), e baixe cada arquivo como `audios/aN.mp3`.
- A montagem já corta o silêncio das pontas e acelera 7% (`tempo` no projeto). Para um ritmo ainda mais rápido, use 1.10 no máximo.

### 4. Cenas com Higgsfield (Kling)
Detalhes das chamadas: `references/higgsfield.md`.
1. **Personagem**: gere ou escolha 1 imagem do personagem no estilo da marca e envie para o Higgsfield (vira o `media_id` de referência).
2. **Custo antes de gerar**: `get_cost:true` (referência: Kling 4.0, 15s, 9:16, 1080p ≈ 49 créditos por cena; 720p ≈ 34). Informe o total ao usuário.
3. **Gere as 6 cenas num único lote**: modelo `kling4_0`, `mode: reference-to-video`, `image_references` = personagem, `duration` 15 (sobra para cortar), `aspect_ratio 9:16`.
4. Cada prompt = ação da cena + o MESMO bloco fixo de personagem/estilo + `No on-screen text, no subtitles, no logos, no talking or lip sync.`
5. Espere os jobs terminarem, baixe para `cenas/c1.mp4 ... c6.mp4` e confira com uma folha de frames antes de montar (veja QC).

### 5. Montagem
```bash
python3 scripts/assemble.py projeto.json --out reels.mp4
```
O script:
- corta cada cena exatamente no tamanho da sua fala (voz, legenda e imagem trocam juntas);
- descarta o áudio do Kling, que às vezes vem com fala sem sentido;
- queima a legenda em blocos de no máx. 2 linhas × 21 caracteres, com palavras destacadas na cor da marca;
- mostra o card `COMENTA / <PALAVRA>` a partir da frase do CTA;
- normaliza o volume para o Instagram (-14 LUFS) e salva também o `.ass` editável.

Para a melhor legenda, escreva `captions` à mão em cada cena (pares `[linha1, linha2]`, ≤21 caracteres cada). Sem isso, o script quebra sozinho.

### 6. Controle de qualidade e entrega
```bash
for t in 2 12 22 32 42; do ffmpeg -v error -y -ss $t -i reels.mp4 -frames:v 1 -vf scale=360:-1 q_$t.jpg; done
ffmpeg -y -i q_2.jpg -i q_12.jpg -i q_22.jpg -i q_32.jpg -i q_42.jpg -filter_complex hstack=inputs=5 qc.jpg
```
Confira na imagem: legenda inteira dentro da tela, CTA sem cobrir a legenda, personagem sempre igual, nenhum texto gerado pela IA no cenário.
Na entrega, avise: duração, créditos gastos, e que a música deve ser adicionada no próprio Instagram (áudio em alta ajuda no alcance). Se o arquivo for grande demais para baixar no chat, ofereça um link (ex.: upload para o storage do Higgsfield).

## Armadilhas
- **Texto dentro da imagem**: a IA erra letras e cria placas falsas. Todo texto vai na legenda.
- **Personagens secundários** costumam ganhar a cara do protagonista. Dê a eles uma imagem de referência própria.
- **Lote do Higgsfield com `submission_failed` + preset recomendado**: reenvie aquele item com `declined_preset_id`.
- **Legenda cortada na borda**: acontece com fonte >75px ou linhas >21 caracteres. Use os padrões do script.
- **Não estique o vídeo para bater 60/90s.** O vídeo tem o tamanho da narração.
- **NotebookLM no navegador do agente**: alguns botões não respondem a clique automatizado. Peça um clique ao usuário em vez de insistir.
