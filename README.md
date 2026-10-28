# AI Makers Skills

Skills gratuitas do [Well Pires](https://www.youtube.com/@WellPiresAI) e do AI Makers Club para o **Hermes Agent** (também funcionam no Claude Code e em outros agentes que leem `SKILL.md`).

## Skills

| Skill | O que faz |
|---|---|
| [`storytelling-reels`](skills/storytelling-reels) | Transforma um vídeo do YouTube num Reels de storytelling narrado com a sua voz: NotebookLM (roteiro) → ElevenLabs (narração) → Higgsfield/Kling (cenas) → ffmpeg (montagem com legenda e CTA). |

## Como instalar no Hermes

**Opção 1: pedir pro próprio Hermes.** Cole no chat:

```
Instala essa skill: https://github.com/WellPiresJ9/ai-makers-skills/tree/main/skills/storytelling-reels
```

**Opção 2: comando no terminal**

```bash
hermes skills install WellPiresJ9/ai-makers-skills/skills/storytelling-reels
```

**Opção 3: receber todas as skills do AI Makers** (elas passam a aparecer em *Capabilities → Skills* no app)

```bash
hermes skills tap add WellPiresJ9/ai-makers-skills
```

Depois de instalar, **abra uma sessão nova** e use:

```
/storytelling-reels https://www.youtube.com/watch?v=SEU_VIDEO
```

## O que você precisa ter

- Conta Google com o NotebookLM
- ElevenLabs com uma voz (o ideal é um clone da sua). A chave fica em `ELEVENLABS_API_KEY` no `~/.hermes/.env` ou num conector. **Nunca cole a chave no chat.**
- Higgsfield com créditos (Kling 4.0): MCP conectado ou uso manual pelo site
- `ffmpeg` instalado (Mac: `brew install ffmpeg`)

## Instalação manual (sem terminal)

Baixe este repositório (Code → Download ZIP), copie a pasta `skills/storytelling-reels` para `~/.hermes/skills/` e abra uma sessão nova no Hermes.

---
Feito para os membros e inscritos do AI Makers Club. Licença MIT.
