import sys, time
import numpy as np
import soundfile as sf
from mlx_audio.tts import load

VOICE = ("A warm, clear male presenter in his forties with a natural American accent. "
         "He explains technical ideas to engineers at a calm, steady, unhurried pace, "
         "friendly and confident, like a good conference speaker. Not theatrical.")
REF_TEXT = ("Hi, and welcome. Today we will look inside a large language model, "
            "step by step, and see how it turns a sentence into the next word.")

model = load("mlx-community/Breeze-TTS-2-mlx")
for seed in map(int, sys.argv[1:] or ["1"]):
    t0 = time.time()
    chunks = [np.array(r.audio) for r in model.generate(text=REF_TEXT, instruct=VOICE, cfg_scale=4, seed=seed)]
    audio = np.concatenate(chunks)
    sf.write(f"ref_{seed}.wav", audio, 24000)
    print(f"seed {seed}: {len(audio)/24000:.1f}s audio in {time.time()-t0:.1f}s", flush=True)
