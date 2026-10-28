# Higgsfield: gerar as cenas

## Pelo MCP do Higgsfield (agente)
Nomes de ferramentas usados no MCP oficial (via Composio podem vir com prefixo `HIGGSFIELD_MCP_`):

1. `balance`: ver créditos.
2. `models_explore {action:"search", type:"video", query:"kling"}`: confira o id e os parâmetros (Kling 4.0 = `kling4_0`; modos text/image/reference-to-video; 3–30s; 720p/1080p).
3. Imagem local do personagem → `media_upload {files:[{filename, content_type}]}` → `curl -X PUT -H "Content-Type: image/png" --data-binary @personagem.png '<upload_url>'` (esperar 200) → `media_confirm {type:"image", media_ids:[...]}`.
4. Custo: `generate_video {params:{model:"kling4_0", ..., get_cost:true}}`. O preflight não funciona dentro do lote.
5. Lote (até 12): `generate_video_batch {requests:[{index:1, params:{model:"kling4_0", mode:"reference-to-video", prompt, duration:15, aspect_ratio:"9:16", resolution:"1080p", medias:[{role:"image_references", value:"<media_id>"}], use_unlim:false}}, ...]}`.
6. `jobs_wait {jobs:[{index, job_id}], timeout_seconds:15}`: repita até `all_terminal`; cada job traz `result_url` (mp4) para baixar com curl.
7. Item com `submission_failed` + `preset_recommendation`: reenviar com `declined_preset_id`.

## Pelo site (manual)
higgsfield.ai → Video → Kling 4.0 → Reference to video → envie a imagem do personagem → cole o prompt da cena → 9:16, 15s → gere as 6 e baixe como c1…c6.mp4.

## Dicas
- Gere 15s mesmo que a fala tenha 6–10s: o `video_start` escolhe o melhor trecho.
- Uma ação clara por cena. Prompts com 3+ ações viram cortes confusos.
- Se uma cena vier com texto no cenário ou o personagem com outra cara, gere só aquela de novo.
