"""P05: classify one image with the checkpoint locked before test."""
import argparse
import json
from pathlib import Path

import torch
from PIL import Image
from torchvision.models import DenseNet121_Weights

from evaluation.scene import OUT
from src.common import ROOT, read_json, sha256
from src.phases.phase_02_data import RAW
from src.phases.phase_03_models import build

EXAMPLE = RAW / 'seg_pred/seg_pred/10004.jpg'


def predict(image_path=EXAMPLE):
    image_path = Path(image_path).resolve()
    with Image.open(image_path) as image:
        rgb = image.convert('RGB')
    version = read_json(OUT / 'metrics.json')['version']
    name = version['model']
    folder = ROOT / 'outputs/training-scene-v1' / name
    checkpoint = folder / 'best.pt'
    if sha256(checkpoint) != version['checkpoint_sha256']:
        raise ValueError('Checkpoint differs from P04')
    ck = torch.load(checkpoint, map_location='cpu', weights_only=False)
    transform = DenseNet121_Weights.IMAGENET1K_V1.transforms()
    if (ck['epoch'], ck['model_name'], ck['eval_transform']) != (version['epoch'], name, str(transform)):
        raise ValueError('Checkpoint metadata differs from P04')
    device = read_json(folder / 'identity.json')['device']
    model = build(name, ck['stage']).to(device).eval()
    model.load_state_dict(ck['model'], strict=True)
    with torch.inference_mode():
        logits = model(transform(rgb).unsqueeze(0).to(device))
        if logits.shape != (1, len(ck['classes'])) or not torch.isfinite(logits).all():
            raise ValueError('Invalid model output')
        score, index = logits.softmax(1).max(1)
    return dict(image=str(image_path), image_sha256=sha256(image_path), run=folder.name,
                model=name, stage=ck['stage'], epoch=ck['epoch'], checkpoint_sha256=version['checkpoint_sha256'],
                index=index.item(), label=ck['classes'][index.item()], softmax=score.item())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image', nargs='?', default=EXAMPLE)
    print(json.dumps(predict(parser.parse_args().image), indent=2))
