import os, numpy as np
from voice import embed

AUDIO_EXT = (".wav", ".mp3", ".m4a", ".ogg", ".opus", ".aac",
             ".flac", ".amr", ".3gp", ".mp4", ".wma", ".webm")

db = {}
for name in sorted(os.listdir("samples")):
    folder = os.path.join("samples", name)
    if not os.path.isdir(folder):
        continue
    all_files = [f for f in os.listdir(folder) if f != ".gitkeep"]
    files = [f for f in all_files if f.lower().endswith(AUDIO_EXT)]
    print(f"\n{name}: {len(all_files)} files mili, {len(files)} audio format ki")
    if all_files and not files:
        print("  Files ke naam:", all_files[:5])
    embs = []
    for f in files:
        try:
            embs.append(embed(os.path.join(folder, f)))
        except Exception as e:
            print(f"  skip {f}: {e}")
    if not embs:
        print(f"  {name}: koi valid sample nahi mila, skip")
        continue
    mean = np.mean(embs, axis=0)
    db[name] = mean / np.linalg.norm(mean)
    print(f"  {name}: {len(embs)} samples enrolled")

np.save("voices.npy", db, allow_pickle=True)
print("\nDone. Enrolled:", list(db))