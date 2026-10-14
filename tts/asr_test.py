import sys
from mlx_audio.stt import load
m = load("mlx-community/parakeet-tdt-0.6b-v3")
for p in sys.argv[1:]:
    print(p, "|", m.generate(p).text.strip(), flush=True)
