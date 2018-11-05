import os
import sys
import base64
from io import BytesIO
from pathlib import Path
from operator import itemgetter

from jinja2 import Environment, FileSystemLoader
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse, HTMLResponse
import uvicorn

import torch
from torchvision.models import resnet18
from fastai.vision import (
    ImageDataBunch,
    open_image,
    get_transforms,
    create_cnn
)


ROOT_DIR = (Path().parent/'templates').as_posix()
MODEL_NAME = os.environ.get('MODEL_NAME', 'resnet50')


app = Starlette()
app.debug = True
app.mount('/static', StaticFiles(directory='static'))
env = Environment(loader=FileSystemLoader(ROOT_DIR), trim_blocks=True)

categories = [f'/{name.strip()}_1.jpg' for name in Path('categories.txt').open()]

placeholder_data = ImageDataBunch.from_name_re(
    Path('/tmp'), categories,
    pat=r'/([^/]+)_\d+.jpg$',
    ds_tfms=get_transforms(),
    device='cpu',
    size=224
)

learn = create_cnn(placeholder_data, resnet18)
state = torch.load(f'models/{MODEL_NAME}.pth', map_location='cpu')
learn.model.load_state_dict(state, state)


@app.route('/')
def home(request):
    template = env.get_template('index.html')
    return HTMLResponse(template.render(static_url='/static'))


@app.route('/send', methods=['POST'])
async def send(request):
    data = await request.json()
    losses = predict_image_from_base64(data['imgBase64'])
    return JSONResponse({'predictions': create_predictions(losses)})


def predict_image_from_base64(base64str):
    _, content = base64str.split(',')
    decoded = base64.b64decode(content)
    image = open_image(BytesIO(decoded))
    return image.predict(learn)


def create_predictions(losses):
    return sorted(
        zip(learn.data.classes, map(float, losses)),
        key=itemgetter(1), reverse=True)


if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app, host='0.0.0.0', port=8080)
