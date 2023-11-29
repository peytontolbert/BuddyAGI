from flask import Flask, request, render_template, jsonify, send_file
from flask_cors import CORS, cross_origin
from diffusers import StableDiffusionImg2ImgPipeline, AutoPipelineForImage2Image, StableDiffusionLatentUpscalePipeline, StableDiffusionControlNetImg2ImgPipeline, ControlNetModel, UniPCMultistepScheduler
from diffusers.utils import load_image
import requests
import torch
from io import BytesIO
from PIL import Image
import numpy as np
import cv2

# Initialize Flask app
app = Flask(__name__)

CORS(app, origins=['*'])



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_image():
    # Receive the image
    file = request.files['image']
    img = Image.open(file.stream).convert("RGB")
    #img = preprocess_image(img)
    # Run the tile model and upscale model
    processed_image = run_tile_pipeline(img)

    # Save the processed image temporarily
    processed_image.save("temp_processed.png")

    # Return the processed image
    return send_file("temp_processed.png", mimetype='image/png')

def get_low_res_img(url, shape):
    response = requests.get(url)
    shape = (200, 128)
    low_res_img = Image.open(BytesIO(response.content)).convert("RGB")
    low_res_img = low_res_img.resize(shape)
    return low_res_img


def preprocess_image(image):
    # Resize if any dimension is larger than 2000 pixels
    max_size = 2000
    if image.width > max_size or image.height > max_size:
        image.thumbnail((max_size, max_size))

    # Split the image in half (you can choose between horizontal or vertical split)
    # Example for horizontal split:
    width, height = image.size
    image = image.crop((0, 0, width, height // 2))  # Adjust this line for different types of splits

    return image


def run_tile_model(generator, prompt, image):
    np_image = np.array(image)
    np_image = cv2.Canny(np_image, 50, 100)
    np_image = np_image[:, :, None]
    np_image = np.concatenate([np_image, np_image, np_image], axis=2)
    canny_image = Image.fromarray(np_image)
    controlnet = ControlNetModel.from_pretrained("lllyasviel/control_v11f1e_sd15_tile", torch_dtype=torch.float16)
    model_directory = "runwayml/stable-diffusion-v1-5"
    pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(model_directory, controlnet=controlnet, torch_dtype=torch.float16,
    safety_checker = None,
    requires_safety_checker = False)
    pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
    pipe.enable_model_cpu_offload()
    image = pipe(
                prompt=prompt,
                num_inference_steps=35,
                strength=.09,
                generator=generator,
                image=image,
                control_image=canny_image,
).images[0]
    return image

def run_tile_pipeline(image):
    generator = torch.manual_seed(0)
    # Pre-process: Resize if necessary and split
    prompt = "high resolution, realism, clear quality, masterpiece, sharply defined, 32k quality"

    new_image = run_tile_model(generator, prompt, image)
    return new_image


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



def run_upscale_model(generator, image, prompt):
    # Specify the path to your model directory
    upscale_model = "stabilityai/sd-x2-latent-upscaler"
    upscaler = StableDiffusionLatentUpscalePipeline.from_pretrained(upscale_model, torch_dtype=torch.float16,
    safety_checker = None,
    requires_safety_checker = False)
    # pipe.to(device)
    upscaler.enable_model_cpu_offload()
    image = upscaler(
    prompt=prompt,
    image=image,
    guidance_scale=1,
    generator=generator
).images[0]
    return image


def run_tile_and_upscale_pipeline(image):
    generator = torch.manual_seed(0)
    prompt = "high resolution, clear quality, sharply defined"

    new_image = run_tile_model(generator, prompt, image)
    upscaled_image = run_upscale_model(generator, new_image, prompt)
    return upscaled_image


if __name__ == '__main__':
    app.run(debug=True)