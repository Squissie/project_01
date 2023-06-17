from django.conf import settings
import numpy as np
from io import BytesIO

import matplotlib.pyplot as plt
import skimage
import skimage.io
import torch
import torch.nn.functional as F
import torchvision
import torchvision.transforms
import skimage
import skimage.filters
import torchxrayvision as xrv

from model_splitter import *
from joblib import load
from skimage.transform import resize
from PIL import Image

from skimage import transform
from tensorflow import keras

# CNN is used here, not SVM

### OLD SVM MODEL ###
# if not settings.DEBUG_NOMODEL:
#     with TempSplitFile("./savedModel/svmModel_2.joblib") as modelfile, TempSplitFile("./savedModel/mmscaler.joblib") as scalerfile:
#         ML_MODEL = load(modelfile)
#         ML_SCALER = load(scalerfile)

###


### NEW MODEL ###
# ML_MODEL = load('./savedModel/resnet50_model_v1.joblib')
# ML_MODEL.eval()
###

## function to run ML models on an image and output results + optional Class Activation Map image
def predictXray(image, cam=False):
    result = "error"
    if not settings.DEBUG_NOMODEL:
        CNN_MODEL = keras.models.load_model("./savedModel/CNN_model.h5")
        # ### Joy's CNN model ###
        results = ("Covid-19", "Normal", "Pneumonia")
        with Image.open(f".{image}") as img:
            img = img.resize((150, 150))
            img = np.array(img)
            img = img / 255.0
            img = resize(img, (150, 150, 3))
            img = np.expand_dims(img, axis=0)
            predictions = CNN_MODEL.predict(img)

        predicted = np.argmax(predictions, axis=1)
        result = results[predicted[0]]
        # for probability - doesn't work
        # result = f"{results[predicted[0]]}\nConfidence: {predictions[0][predicted] * 100: .2f}"

        ### OLD SVM MODEL ###
        # results = ("Covid-19", "Normal", "Pneumonia")
        # with Image.open(f".{image}") as img:
        #     img_resized = resize(np.array(img), (100, 100, 3))
        # color_features = img_resized.flatten()
        # feature_matrix = np.hstack(
        #     color_features).reshape(1, -1)  # type:ignore
        # xray_stand = ML_SCALER.transform(feature_matrix)
        # scores = list(ML_MODEL.predict_proba(xray_stand)[0])
        # result = results[scores.index(max(scores))]
        ###

        ### NEW MODEL ###
        # transform = torchvision.transforms.Compose([
        #     torchvision.transforms.Resize((224, 224)),
        #     torchvision.transforms.ToTensor(),
        #     torchvision.transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        # ])

        # with Image.open(f".{image}") as img:
        #     img_tensor = transform(img)
        #     img_tensor = torch.unsqueeze(img_tensor, 0)

        # with torch.no_grad():
        #     outputs = ML_MODEL(img_tensor)
        #     _, predicted = torch.max(outputs.data, 1)

        # if predicted[0] == 0:
        #     result = "Bacterial Pneumonia"
        # elif predicted[0] == 1:
        #     result = "Covid-19"
        # elif predicted[0] == 2:
        #     result = "Normal"
        # elif predicted[0] == 3:
        #     result = "Viral Pneumonia"
        ###

        severity = ""

        if result == "Covid-19":
            #comment this out when putting back predict severity
            #severity = "Not implemented"
            #commenting out severity for now

            model = PneumoniaSeverityNetCIDC()
            outputs = process(model, f".{image}")

            geo = float(outputs["geographic_extent"].cpu().numpy())

            if geo < 3:
                severity = "Severity (mild/moderate/severe): Mild"
            elif geo < 6:
                severity = "Severity (mild/moderate/severe): Moderate"
            else:
                severity = "Severity (mild/moderate/severe): Severe"

            # geo/opa
            opa = float(outputs["opacity"].cpu().numpy())
            severity += f"\nGeographic Extent (0-8): {geo:1.4}\nOpacity (0-8): {opa:1.4}"

            img = outputs["img"]
            img = img.requires_grad_()
            outputs = model(img)
            grads = torch.autograd.grad(
                outputs["geographic_extent"], img)[0][0][0]
            blurred = skimage.filters.gaussian(
                grads.detach().cpu().numpy() ** 2, sigma=5, truncate=3.5
            )

            full_frame()
            my_dpi = 100
            fig = plt.figure(
                frameon=False, figsize=(224 / my_dpi, 224 / my_dpi), dpi=my_dpi
            )
            ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
            ax.set_axis_off()
            fig.add_axes(ax)
            ax.imshow(img[0][0].detach().cpu().numpy(),
                      cmap="gray", aspect="auto")
            ax.imshow(blurred, alpha=0.5)
            cam = BytesIO()
            plt.savefig(cam, format="png")

        return (f"Prediction: {result}\n{severity}", cam)

    else:
        return ("No prediction\n", False)


class PneumoniaSeverityNetCIDC(torch.nn.Module):
    def __init__(self):
        super(PneumoniaSeverityNetCIDC, self).__init__()
        self.model = xrv.models.DenseNet(weights="all")
        self.model.op_threshs = None
        self.theta_bias_geographic_extent = torch.from_numpy(
            np.asarray((0.8705248236656189, 3.4137437))
        )
        self.theta_bias_opacity = torch.from_numpy(
            np.asarray((0.5484423041343689, 2.5535977))
        )

    def forward(self, x):
        ret = {}
        feats = self.model.features(x)
        feats = F.relu(feats, inplace=True)
        ret["feats"] = F.adaptive_avg_pool2d(
            feats, (1, 1)).view(feats.size(0), -1)
        ret["preds"] = self.model.classifier(ret["feats"])

        pred = ret["preds"][0,
                            xrv.datasets.default_pathologies.index("Lung Opacity")]
        geographic_extent = (
            pred * self.theta_bias_geographic_extent[0]
            + self.theta_bias_geographic_extent[1]
        )
        opacity = pred * \
            self.theta_bias_opacity[0] + self.theta_bias_opacity[1]

        ret["geographic_extent"] = torch.clamp(geographic_extent, 0, 8)
        # scaled to match new RALO score
        ret["opacity"] = torch.clamp(opacity / 6 * 8, 0, 8)

        return ret


def process(model, img_path, cuda=False):
    img = skimage.io.imread(img_path)
    img = xrv.datasets.normalize(img, 255)

    # Check that images are 2D arrays
    if len(img.shape) > 2:
        img = img[:, :, 0]
    if len(img.shape) < 2:
        print("error, dimension lower than 2 for image")

    # Add color channel
    img = img[None, :, :]

    transform = torchvision.transforms.Compose(
        [xrv.datasets.XRayCenterCrop(), xrv.datasets.XRayResizer(224)]
    )

    img = transform(img)

    with torch.no_grad():
        img = torch.from_numpy(img).unsqueeze(0)
        if cuda:
            img = img.cuda()
            model = model.cuda()

        outputs = model(img)

    outputs["img"] = img
    return outputs


def full_frame(width=None, height=None):
    import matplotlib as mpl

    mpl.rcParams["savefig.pad_inches"] = 0
    figsize = None if width is None else (width, height)
    fig = plt.figure(figsize=figsize)
    ax = plt.axes([0, 0, 1, 1], frameon=False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.autoscale(tight=True)
