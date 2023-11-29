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
model_directory = "./runwayml/stable-diffusion-v1-5"

image = load_image(img)
init_image = Image.open(img).convert("RGB")
# get canny image
#np_image = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
# Now you can safely apply Canny edge detection
#edges = cv2.Canny(np_image, 100, 200)
# Convert single channel image to 3-channel image for compatibility
#canny_image_3ch = np.stack([edges]*3, axis=-1)
#canny_image_pil = Image.fromarray(canny_image_3ch)

# load control net and stable diffusion v1-5
# controlnetcanny = ControlNetModel.from_pretrained("lllyasviel/sd-controlnet-canny", torch_dtype=torch.float16)
# pipe.to(device)

image.save("images/output.png")

def run_tile_model(generator, prompt, np_image):
    np_image = np.array(image)

    np_image = cv2.Canny(np_image, 100, 200)
    np_image = np_image[:, :, None]
    np_image = np.concatenate([np_image, np_image, np_image], axis=2)
    canny_image = Image.fromarray(np_image)
    controlnet = ControlNetModel.from_pretrained("lllyasviel/control_v11f1e_sd15_tile", torch_dtype=torch.float16)
    pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(model_directory, controlnet=controlnet, torch_dtype=torch.float16)
    pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
    pipe.enable_model_cpu_offload()
    image = pipe(
                prompt=prompt,
                num_inference_steps=65,
                strength=3,
                generator=generator,
                image=image,
                control_image=canny_image,
).images[0]
    return image

def run_upscale_model(generator, image, prompt):
    # Specify the path to your model directory
    upscale_model = "stabilityai/sd-x2-latent-upscaler"
    upscaler = StableDiffusionLatentUpscalePipeline.from_pretrained(upscale_model, torch_dtype=torch.float16)
    upscaler .enable_attention_slicing()
    # pipe.to(device)
    upscaler.enable_model_cpu_offload()
    upscaled_image = upscaler(
    prompt=prompt,
    image=image,
    num_inference_steps=25,
    guidance_scale=0,
    strength=0.1,
    generator=generator
).images[0]
    return image

def run_tile_and_upscale_pipeline(image):
    generator = torch.manual_seed(0)
    prompt = "high resolution, clear quality, sharply defined"
    
    new_image = run_tile_model(generator, prompt, image)
    upscaled_image = run_upscale_model(generator, new_image, prompt)
    redone_upscaled_image = run_tile_model(generator, prompt, upscaled_image)

if __name__ == '__main__':
    app.run(debug=True)