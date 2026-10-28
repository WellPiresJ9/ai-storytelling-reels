#!/usr/bin/env python3
"""Monta o Reels final: 1 clipe + 1 áudio por cena, legenda queimada e CTA.

Precisa de ffmpeg/ffprobe com libass. Só biblioteca padrão do Python.

Uso:
  python3 assemble.py projeto.json --out reels.mp4

projeto.json (caminhos relativos ao próprio json):
{
  "scenes": [
    {"video": "cenas/c1.mp4", "audio": "audios/a1.mp3", "video_start": 0,
     "narration": "Esse é o Dono. A empresa dele vai muito bem.",
     "captions": [["Esse é o Dono.", ""], ["A empresa dele", "vai muito bem."]]}
  ],
  "cta": {"keyword": "CÉREBRO", "top_line": "COMENTA", "trigger": "Comenta"},
  "highlight": ["Dono", "robô", "CÉREBRO"],
  "style": {"font": "Montserrat", "fonts_dir": "fonts", "accent_bgr": "1E7BFF"},
  "tempo": 1.07
}
- "captions" é opcional: sem ele, o texto da narração é quebrado sozinho (máx 2 linhas de 21 caracteres).
- "accent_bgr" é a cor de destaque no formato do ASS (BGR). 1E7BFF = laranja.
"""
import argparse, json, os, re, subprocess, sys, tempfile

MAXL = 21


def run(*a):
    subprocess.run(list(a), check=True)


def dur(f):
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", f], capture_output=True, text=True).stdout
    return float(o)


def speech_segments(wav, total):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", wav, "-af",
                          "silencedetect=noise=-35dB:d=0.12", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    ss = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    se = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    segs, a = [], 0.0
    for x, y in zip(ss, se):
        if x > a + 0.05:
            segs.append((a, x))
        a = y
    if a < total:
        segs.append((a, total))
    return segs or [(0.0, total)]


def _split_even(words, k):
    """Divide palavras em k grupos de tamanho (em caracteres) parecido."""
    total = len(" ".join(words)); groups, cur = [], []
    for w in words:
        alvo = total * (len(groups) + 1) / k
        if cur and len(groups) < k - 1 and len(" ".join(sum(groups, []) + cur + [w])) > alvo + 2:
            groups.append(cur); cur = [w]
        else:
            cur.append(w)
    groups.append(cur)
    return groups


def _two_lines(words):
    if len(" ".join(words)) <= MAXL:
        return [" ".join(words), ""]
    a, b = _split_even(words, 2)
    return [" ".join(a), " ".join(b)]


def auto_captions(text):
    """Quebra cada frase em blocos equilibrados de no máx. 2 linhas x MAXL caracteres
    (evita sobrar uma palavra sozinha no último bloco)."""
    out = []
    for frase in [p for p in re.split(r"(?<=[.?!:])\s+", text) if p.strip()]:
        w = frase.split()
        for k in range(1, 12):
            blocos = [_two_lines(g) for g in _split_even(w, k)]
            if all(len(l) <= MAXL for b in blocos for l in b):
                out += blocos
                break
        else:
            out += [_two_lines([x]) for x in w]
    return out


def ts(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--out", default="reels.mp4")
    a = ap.parse_args()
    base = os.path.dirname(os.path.abspath(a.project))
    P = json.load(open(a.project, encoding="utf-8"))
    st = P.get("style", {})
    font = st.get("font", "Montserrat")
    fonts_dir = os.path.join(base, st.get("fonts_dir", "fonts"))
    acc = st.get("accent_bgr", "1E7BFF")
    tempo = float(P.get("tempo", 1.07))
    hl = sorted(P.get("highlight", []), key=len, reverse=True)
    tmp = tempfile.mkdtemp(prefix="storyreels_")
    p = lambda x: x if os.path.isabs(x) else os.path.join(base, x)

    def deco(s):
        for w in hl:
            s = s.replace(w, "{\\c&H%s&}%s{\\c&HFFFFFF&}" % (acc, w))
        return s

    events, parts, auds, t0 = [], [], [], 0.0
    for i, sc in enumerate(P["scenes"], 1):
        wav = f"{tmp}/s{i}.wav"
        run("ffmpeg", "-v", "error", "-y", "-i", p(sc["audio"]), "-af",
            "silenceremove=start_periods=1:start_threshold=-40dB,areverse,"
            "silenceremove=start_periods=1:start_threshold=-40dB,areverse,"
            f"atempo={tempo},apad=pad_dur=0.25", "-ar", "44100", "-ac", "2", wav)
        d = dur(wav)
        last = i == len(P["scenes"])
        vd = d + (0.6 if last else 0)
        clip = f"{tmp}/p{i}.mp4"
        run("ffmpeg", "-v", "error", "-y", "-ss", str(sc.get("video_start", 0)), "-i", p(sc["video"]),
            "-an", "-vf", "fps=30,scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,setsar=1,tpad=stop_mode=clone:stop_duration=2",
            "-t", f"{vd:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", clip)
        parts.append(clip); auds.append(wav)
        caps = sc.get("captions") or auto_captions(sc["narration"])
        for c in caps:
            for line in c:
                if len(line) > MAXL:
                    print(f"aviso: linha com {len(line)} caracteres pode encostar na borda: {line!r}")
        segs = speech_segments(wav, d - 0.25)
        tot = sum(b - x for x, b in segs)
        L = [len(c[0] + c[1]) + 3 for c in caps]
        T = sum(L)

        def s2r(t):
            acc_ = 0
            for x, b in segs:
                if acc_ + (b - x) >= t:
                    return x + (t - acc_)
                acc_ += b - x
            return segs[-1][1]
        cum = 0
        for c, l in zip(caps, L):
            s0 = s2r(cum / T * tot); cum += l
            events.append([t0 + s0, t0 + s2r(cum / T * tot), c])
        t0 += d
    total = t0 + 0.6
    for k in range(len(events) - 1):
        if events[k + 1][0] - events[k][1] < 0.4:
            events[k][1] = events[k + 1][0]

    ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},70,&H00FFFFFF,&H00FFFFFF,&H00301A0F,&H96000000,1,0,0,0,100,100,0,0,1,7,4,2,110,110,520,1
Style: Big,{font},150,&H00FFFFFF,&H00FFFFFF,&H00301A0F,&H96000000,1,0,0,0,100,100,0,0,1,11,6,5,80,80,0,1
Style: Mid,{font},84,&H00FFFFFF,&H00FFFFFF,&H00301A0F,&H96000000,1,0,0,0,100,100,0,0,1,8,4,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    for s0, e0, (l1, l2) in events:
        txt = deco(l1) + ("\\N" + deco(l2) if l2 else "")
        ass += f"Dialogue: 2,{ts(s0)},{ts(e0)},Cap,,0,0,0,,{{\\fad(40,40)}}{txt}\n"
    cta = P.get("cta")
    if cta:
        trig = cta.get("trigger", "Comenta")
        hits = [e for e in events if trig.lower() in (e[2][0] + " " + e[2][1]).lower()]
        start = hits[0][0] if hits else max(0, total - 4)
        ass += f"Dialogue: 3,{ts(start)},{ts(total)},Mid,,0,0,0,,{{\\fad(150,0)\\pos(540,560)}}{cta.get('top_line', 'COMENTA')}\n"
        ass += f"Dialogue: 3,{ts(start + 0.15)},{ts(total)},Big,,0,0,0,,{{\\fad(150,0)\\pos(540,720)\\c&H{acc}&}}{cta['keyword']}\n"
    ass_path = f"{tmp}/legendas.ass"
    open(ass_path, "w", encoding="utf-8").write(ass)

    open(f"{tmp}/v.txt", "w").write("".join(f"file '{x}'\n" for x in parts))
    open(f"{tmp}/a.txt", "w").write("".join(f"file '{x}'\n" for x in auds))
    run("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/v.txt", "-c", "copy", f"{tmp}/mudo.mp4")
    run("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/a.txt", "-c", "pcm_s16le", f"{tmp}/voz.wav")
    sub = f"subtitles={ass_path}" + (f":fontsdir={fonts_dir}" if os.path.isdir(fonts_dir) else "")
    run("ffmpeg", "-v", "error", "-y", "-i", f"{tmp}/mudo.mp4", "-i", f"{tmp}/voz.wav", "-filter_complex",
        f"[0:v]{sub}[v];[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,apad[a]", "-map", "[v]", "-map", "[a]",
        "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "6M",
        "-bufsize", "12M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.out)
    import shutil
    shutil.copy(ass_path, os.path.splitext(a.out)[0] + ".ass")
    print(f"pronto: {a.out} ({total:.1f}s) | legenda editável: {os.path.splitext(a.out)[0]}.ass")


if __name__ == "__main__":
    main()
