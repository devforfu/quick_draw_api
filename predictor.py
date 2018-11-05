from PIL import Image as PILImage
from torchvision.transforms.functional import to_tensor

from fastai import *
from fastai.vision import *


@dataclass
class Predictor:
    learn: Learner
    mean: FloatTensor
    std: FloatTensor

    def __post_init__(self):
        device = self.learn.data.device
        self.learn.model.eval()
        self.classes = np.array(self.learn.data.classes)
        self.mean, self.std = [torch.tensor(x).to(device) for x in (self.mean, self.std)]

    def predict(self, x):
        out = self.predict_logits(x)
        best_index = out.argmax()
        return self.learn.data.classes[best_index]

    def predict_top(self, x, k=1):
        out = self.predict_logits(x)
        np_out = out.flatten().detach().numpy()
        top_idx = np_out.argsort()[-k:]
        top_losses = np_out[top_idx]
        top_classes = self.classes[top_idx]
        return top_classes[::-1], top_losses[::-1]

    def predict_logits(self, x):
        x = self._to_tensor(x)
        out = self.learn.model(x[None])
        return out

    def _to_tensor(self, x):
        if isinstance(x, str):
            data = open_image(x).data
        elif isinstance(x, PILImage.Image):
            data = to_tensor(x)
        else:
            data = torch.tensor(x)
        x = data.to(self.learn.data.device)
        x = normalize(x, self.mean, self.std)
        return x