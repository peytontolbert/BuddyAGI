from diffusers import StableDiffusionImg2ImgPipeline, AutoPipelineForImage2Image, StableDiffusionLatentUpscalePipeline, StableDiffusionControlNetImg2ImgPipeline, ControlNetModel, UniPCMultistepScheduler
from diffusers.utils import load_image
import requests
import torch
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
device = "cuda"

img = "test.png"
np_image = np.array(img)
model_directory = "stabilityai/sd-x2-latent-upscaler"


# get canny image
np_image = cv2.Canny(np_image, 100, 200)
np_image = np_image[:, :, None]
np_image = np.concatenate([np_image, np_image, np_image], axis=2)
canny_image = Image.fromarray(np_image)

# load control net and stable diffusion v1-5
controlnet = ControlNetModel.from_pretrained("lllyasviel/control_v11f1e_sd15_tile", torch_dtype=torch.float16)
controlnetcanny = ControlNetModel.from_pretrained("lllyasviel/sd-controlnet-canny", torch_dtype=torch.float16)
pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(model_directory, controlnet=controlnet, torch_dtype=torch.float16)
pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
pipe.enable_attention_slicing()
# pipe.to(device)
pipe.enable_model_cpu_offload()


generator = torch.manual_seed(0)
image = pipe(
                "high resolution, clear quality",
                num_inference_steps=20,
                generator=generator,
                image=img,
                control_image=canny_image,
).images[0]