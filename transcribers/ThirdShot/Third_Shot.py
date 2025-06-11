import boto3
from PIL import Image
import io
import os
from pathlib import Path

""""Third Shot, This looks over the Collaged Images produced in the Segmentator. Exact same logic for evetyhing just named
Collaged_Images instead."""



# List of available models
AVAILABLE_MODELS = [
    "us.anthropic.claude-3-sonnet-20240229-v1:0",
    "us.meta.llama3-2-90b-instruct-v1:0",
    "us.meta.llama4-maverick-17b-instruct-v1:0",
    "us.amazon.nova-premier-v1:0",
    "us.amazon.nova-pro-v1:0",
    "us.mistral.pixtral-large-2502-v1:0"
]

# Resize image if too large
def resize_image(image_bytes, max_size=(1120, 1120)):
    img = Image.open(io.BytesIO(image_bytes))
    if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=img.format)
        return img_byte_arr.getvalue()
    return image_bytes

def select_model():
    
    print("Available models:")
    for i, model in enumerate(AVAILABLE_MODELS, 1):
        print(f"{i}. {model}")

    while True:
        try:
            selection = int(input("Select model number: "))
            if 1 <= selection <= len(AVAILABLE_MODELS):
                return AVAILABLE_MODELS[selection-1]
            print(f"Please enter a number between 1 and {len(AVAILABLE_MODELS)}")
        except ValueError:
            print("Please enter a valid number")

def convert_to_png(image_path):
    #Convert to PNG
    img = Image.open(image_path)
    png_bytes = io.BytesIO()
    img.save(png_bytes, format="PNG")
    return png_bytes.getvalue()

def process_image(image_path, prompt_path, model_id=None):
    
    # Initialize Bedrock client
    bedrock_runtime = boto3.client("bedrock-runtime")
    
    # Select model if not provided
    if model_id is None:
        model_id = select_model()
    
    # Convert image to PNG and resize
    image = convert_to_png(image_path)
    image = resize_image(image)
    
    # Read prompt
    with open(prompt_path, "r") as f:
        user_message = f.read().strip()
    
    # Always use PNG format
    # Prepare message for model
    messages = [
        {
            "role": "user",
            "content": [
                {"image": {"format": "png", "source": {"bytes": image}}},
                {"text": user_message},
            ],
        }
    ]
    
    # Call Bedrock
    response = bedrock_runtime.converse(
        modelId=model_id,
        messages=messages,
    )
    
    # Extract and return response
    response_text = response["output"]["message"]["content"][0]["text"]
    print(response_text)
    return response_text

def process_images(base_folder, prompt_path, output_dir, date_folder, model_id=None):
    """Process multiple images from a folder
    
    Args:
        base_folder: Path to the base date folder
        prompt_path: Path to the prompt file
        output_dir: Path to save the transcription results
        date_folder: Name of the date folder for naming the output file
        model_id: Pre-selected model ID (optional)
    """
    # Output directory is already FirstShot specific
    # Construct path to Collaged_Images folder
    images_folder = os.path.join(base_folder, "Collaged_Images")
    if not os.path.exists(images_folder):
        print(f"Error: Collaged_Images folder not found at {images_folder}")
        return
        
    print(f"Third Shot processing images from: {images_folder}")
    
    # Get all image files
    image_extensions = ['.png', '.jpg', '.jpeg']
    image_files = []
    for ext in image_extensions:
        image_files.extend(list(Path(images_folder).glob(f'*{ext}')))
    
    if not image_files:
        print(f"No image files found in {images_folder}")
        return
        
    # Sort images by index
    def extract_index(filename):
        # Extract numeric index from filename
        # This assumes index is a number in the filename
        import re
        match = re.search(r'(\d+)', filename.name)
        if match:
            return int(match.group(1))
        return 0  # Default to 0 if no index found
    
    # Sort image files by their index
    image_files.sort(key=extract_index)
    #print("Images sorted by index for processing")
        
    #print("All images will be converted to PNG format for processing")
    
    # Use pre-selected model or select one if not provided
    if model_id is None:
        model_id = select_model()
    
    # Create output file
    output_file = output_dir / f"{date_folder}_third_shot_transcriptions.txt"
    
    # Write header to the output file
    with open(output_file, "w") as f:
        f.write(f"Third Shot Transcriber transcriptions: {Path(base_folder).name}\n")
        f.write("="*80 + "\n\n")
    
    # Process each image
    print(f"\nFound {len(image_files)} images to process")
    for i, image_path in enumerate(image_files, 1):
        print(50*"=")
        print(f"Processing image {i}/{len(image_files)}: {image_path.name}")
        
        try:
            # Process the image using the selected model
            response_text = process_image(image_path, prompt_path, model_id)
            
            # Append result to the single output file
            with open(output_file, "a") as f:
                f.write(f"Image: {image_path.name}\n")
                #f.write("-"*80 + "\n")
                f.write(response_text)
                f.write("\n\n" + "="*80 + "\n\n")
            
            print(f"Completed to: {output_file}")
            
        except Exception as e:
            print(f"Error processing {image_path.name}: {str(e)}")
            # Log error to the output file
            with open(output_file, "a") as f:
                f.write(f"Error processing {image_path.name}: {str(e)}\n\n")
    
    print(f"Third Shot processing completed successfully! Results saved to {output_file}")

# Allow running this module directly for testing
if __name__ == "__main__":
    process_images()
