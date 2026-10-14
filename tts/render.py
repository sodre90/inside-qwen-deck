import difflib, hashlib, json, re, sys, time
from pathlib import Path
import mlx.core as mx
import numpy as np
import soundfile as sf
from num2words import num2words
from mlx_audio.tts import load as load_tts
from mlx_audio.stt import load as load_stt

SR = 24000
REF_AUDIO = "ref_1.wav"
REF_TEXT = ("Hi, and welcome. Today we will look inside a large language model, "
            "step by step, and see how it turns a sentence into the next word.")
MIN_SCORE = 0.9
ATTEMPTS = 4

out = Path("wav"); out.mkdir(exist_ok=True)
manifest_path = Path("manifest.json")
manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
talk = json.loads(Path("talk.json").read_text())
only = {int(a) for a in sys.argv[1:]}


def spell_number(m):
    s = m.group(0).replace(",", "")
    if "." in s:
        whole, frac = s.split(".")
        return num2words(int(whole or 0)) + " point " + " ".join(num2words(int(d)) for d in frac)
    return num2words(int(s))


def words(text):
    text = re.sub(r"\d[\d,]*\.?\d*", spell_number, text.lower())
    return re.findall(r"[a-z]+", text.replace("-", " "))


def similarity(a, b):
    return difflib.SequenceMatcher(None, words(a), words(b)).ratio()


def trim(audio, pad=0.12):
    level = np.abs(audio)
    loud = np.where(level > 0.02 * level.max())[0]
    if len(loud) == 0:
        return audio
    a, b = max(0, loud[0] - int(0.05 * SR)), min(len(audio), loud[-1] + int(0.12 * SR))
    silence = np.zeros(int(pad * SR), dtype=audio.dtype)
    return np.concatenate([silence, audio[a:b], silence])


mx.set_cache_limit(1 << 30)
tts = load_tts("mlx-community/Breeze-TTS-2-mlx")
stt = load_stt("mlx-community/parakeet-tdt-0.6b-v3")
t_start = time.time()
for i, seg in enumerate(talk):
    say = seg.get("say", seg["text"])
    key = hashlib.sha1(say.encode()).hexdigest()[:12]
    done = manifest.get(key)
    if not only and done and (done["score"] >= MIN_SCORE or done.get("accepted")) and (out / f"{key}.wav").exists():
        continue
    if only and i not in only:
        continue
    best = None
    for attempt in range(ATTEMPTS):
        t0 = time.time()
        chunks = [np.array(r.audio) for r in tts.generate(
            text=say, ref_audio=REF_AUDIO, ref_text=REF_TEXT, temperature=0.8, seed=1000 * attempt + i)]
        audio = trim(np.concatenate(chunks).astype(np.float32))
        tmp = out / f"{key}.try.wav"
        sf.write(tmp, audio, SR)
        heard = stt.generate(str(tmp)).text.strip()
        mx.clear_cache()
        score = similarity(say, heard)
        dur = len(audio) / SR
        rate = len(words(say)) / dur
        ok = score >= MIN_SCORE and 1.6 <= rate <= 3.6
        print(f"[{key}] try {attempt} score {score:.3f} {dur:.1f}s {rate:.2f} w/s gen {time.time()-t0:.0f}s mem {mx.get_active_memory()/1e9:.1f}+{mx.get_cache_memory()/1e9:.1f} GB {'OK' if ok else 'RETRY'}", flush=True)
        if best is None or (ok, score) > (best[0], best[1]):
            best = (ok, score, audio, heard, dur)
        if ok:
            break
    ok, score, audio, heard, dur = best
    sf.write(out / f"{key}.wav", audio, SR)
    (out / f"{key}.try.wav").unlink(missing_ok=True)
    manifest[key] = {"say": say, "heard": heard, "score": round(score, 3), "sec": round(dur, 2), "ok": ok}
    manifest_path.write_text(json.dumps(manifest, indent=1))

bad = [k for k, v in manifest.items() if not v["ok"]]
total = sum(v["sec"] for v in manifest.values())
print(f"done in {(time.time()-t_start)/60:.1f} min; {len(manifest)} segments, {total/60:.1f} min audio; failed checks: {bad or 'none'}", flush=True)
