from diffusers import StableDiffusionImg2ImgPipeline, AutoPipelineForImage2Image, StableDiffusionLatentUpscalePipeline, StableDiffusionXLImg2ImgPipeline
import requests
import torch
from io import BytesIO
from PIL import Image
import numpy as np
from datetime import datetime
device = "cuda"

# Specify the path to your model directory
model_directory = "stabilityai/stable-diffusion-xl-refiner-1.0"
pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(model_directory, torch_dtype=torch.float16)
pipe.enable_attention_slicing()
pipe.to(device)
# pipe.enable_model_cpu_offload()

# Function to generate a unique filename with timestamp
def generate_unique_filename(base_name):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{base_name}_{timestamp}.png"


img = "test.png"
def load_img(path):
    image = Image.open(path).convert("RGB")
    w, h = image.size
    print(f"loaded input image of size ({w}, {h}) from {path}")
    w, h = map(lambda x: x - x % 64, (w, h))  # resize to integer multiple of 64
    image = image.resize((w, h), resample=Image.LANCZOS)
    image = np.array(image).astype(np.float32) / 255.0
    image = image[None].transpose(0, 3, 1, 2)
    image = torch.from_numpy(image)
    return 2. * image - 1.

# Use the function to generate a unique output filename
output = generate_unique_filename("output")

low_res_img = Image.open(img).convert("RGB")
image = load_img(img)
w, h = low_res_img.size
print(f"loaded input image of size ({w}, {h}) from {img}")
# low_res_img = low_res_img.resize((270, 480))


# How to use a seed to generate an image
# generator = torch.Generator("cuda").manual_seed(1024)
# image = pipe(prompt, guidance_scale=7.5, generator=generator).images[0]

# Another example:
# generator = torch.Generator("cuda").manual_seed(1024)
# image = pipe(prompt, guidance_scale=7.5, num_inference_steps=15, generator=generator).images[0]



prompt = "high resolution"
guidance_rescale = 0.0
image = pipe(prompt, image=image, guidance_rescale=guidance_rescale, num_inference_steps=25).images[0]
image.save(output)