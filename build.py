import base64, hashlib, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).parent
TTS = HERE / "tts"
MARKER = "<!--TALK-DATA-->"
REPO_COPY = "/Users/perdos/prj/llama.cpp/docs/presentations/inside-qwen3.8-flash-next.html"


def mp3_for(seg):
    key = hashlib.sha1(seg.get("say", seg["text"]).encode()).hexdigest()[:12]
    wav, mp3 = TTS / "wav" / f"{key}.wav", TTS / "mp3" / f"{key}.mp3"
    if not wav.exists():
        return None
    if not mp3.exists() or mp3.stat().st_mtime < wav.stat().st_mtime:
        mp3.parent.mkdir(exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
                        "-af", "loudnorm=I=-18:TP=-1.5:LRA=11", "-ar", "24000", "-ac", "1",
                        "-c:a", "libmp3lame", "-b:a", "48k", str(mp3)], check=True)
    return mp3


talk = json.loads((TTS / "talk.json").read_text())
mp3s = [mp3_for(s) for s in talk]
missing = [i for i, m in enumerate(mp3s) if m is None]
if "--partial" in sys.argv and missing:
    talk, mp3s, missing = talk[:missing[0]], mp3s[:missing[0]], []
deck = (HERE / "deck.html").read_text()
if missing:
    print(f"missing audio for {len(missing)} segments, building without the talk", file=sys.stderr)
    data = ""
else:
    segs = [{"slide": s["slide"], "text": s["text"], "cues": s.get("cues", []),
             "audio": "data:audio/mpeg;base64," + base64.b64encode(m.read_bytes()).decode()}
            for s, m in zip(talk, mp3s)]
    data = "<script>window.TALK = " + json.dumps(segs, separators=(",", ":")) + ";</script>"
if "--partial" in sys.argv:
    out = HERE / "talk-test.html"
    out.write_text(deck.replace(MARKER, data))
    sys.exit(print(f"{out.name}: {len(talk)} segments"))
out = HERE / "inside-qwen.html"
out.write_text(deck.replace(MARKER, data))
subprocess.run(["sh", str(HERE / "export.sh"), str(out), REPO_COPY], check=True)
subprocess.run(["sh", str(HERE / "export.sh"), str(out), str(HERE / "index.html")], check=True)
print(f"{out.name}: {out.stat().st_size / 1e6:.1f} MB, {len(talk) - len(missing)}/{len(talk)} segments")
