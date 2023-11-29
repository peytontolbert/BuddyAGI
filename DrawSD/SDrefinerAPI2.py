from diffusers import StableDiffusionImg2ImgPipeline, AutoPipelineForImage2Image, StableDiffusionLatentUpscalePipeline, StableDiffusionXLImg2ImgPipeline
import requests
import torch
from io import BytesIO
from PIL import Image, ImageOps
import numpy as np
from datetime import datetime
device = "cuda"

# Specify the path to your model directory
model_directory = "stabilityai/stable-diffusion-xl-refiner-1.0"
pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(model_directory, torch_dtype=torch.float16)
pipe.enable_attention_slicing()
pipe.to(device)
# pipe.enable_model_cpu_offload()




def process_image(image_path, pipeline, prompt, guidance_scale, num_inference_steps):
    original_image = Image.open(image_path).convert("RGB")
    original_width, original_height = original_image.size

    # Resize and pad the image to the closest multiple of 64
    new_width, new_height = map(lambda x: x + (64 - x % 64) if x % 64 != 0 else x, (original_width, original_height))
    resized_image = original_image.resize((new_width, new_height), resample=Image.LANCZOS)
    padded_image = ImageOps.pad(resized_image, (new_width, new_height))

    # Convert to tensor
    padded_image_tensor = preprocess_image(padded_image)

    # Process the image
    processed_tensor = pipeline(prompt, image=padded_image_tensor, guidance_scale=guidance_scale, num_inference_steps=num_inference_steps).images[0]

    processed_tensor.save(output)
    # Convert back to PIL and resize to original dimensions
    processed_image = tensor_to_image(processed_tensor)
    final_image = processed_image.resize((original_width, original_height), Image.LANCZOS)

    # Save the final image
    final_image.save("output2")

# Helper functions to convert between PIL Image and tensor
def preprocess_image(pil_img):
    image = np.array(pil_img).astype(np.float32) / 255.0
    image = image[None].transpose(0, 3, 1, 2)
    image_tensor = torch.from_numpy(image)
    return 2.0 * image_tensor - 1.0


def tensor_to_image(tensor):
    image = (tensor / 2 + 0.5).clamp(0, 1)
    image = image.permute(1, 2, 0).cpu().numpy()
    return Image.fromarray((image * 255).astype(np.uint8))



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
process_image(img, pipe, "high resolution", 0.0, 25)
#image = pipe(prompt, image=image, guidance_rescale=guidance_rescale, num_inference_steps=25).images[0]
image.save(output)