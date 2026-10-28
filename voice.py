import numpy as np, librosa, torch
from speechbrain.inference.speaker import EncoderClassifier
from speechbrain.utils.fetching import LocalStrategy

_model = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_ecapa",
    local_strategy=LocalStrategy.COPY)

def embed(path_or_file):
    wav, _ = librosa.load(path_or_file, sr=16000, mono=True)
    wav, _ = librosa.effects.trim(wav, top_db=25)
    if len(wav) < 16000:
        raise ValueError("audio too short")
    peak = np.max(np.abs(wav))
    if peak > 0:
        wav = wav / peak * 0.9
    with torch.no_grad():
        e = _model.encode_batch(torch.tensor(wav).unsqueeze(0))
    e = e.squeeze().numpy()
    return e / np.linalg.norm(e)