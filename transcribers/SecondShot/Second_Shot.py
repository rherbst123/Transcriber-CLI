import boto3
from PIL import Image
import io
import os
from pathlib import Path
from datetime import datetime
from cost_analysis import cost_tracker
from json_output import save_json_transcription, create_batch_json_file

""""Second Shot, This looks over the Collaged Images produced in the Segmentator. Exact same logic for evetyhing just named
Collaged_Images instead."""



# List of available models
AVAILABLE_MODELS = [
    "us.anthropic.claude-3-sonnet-20240229-v1:0",
    "us.anthropic.claude-opus-4-20250514-v1:0",
    "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "us.meta.llama3-2-90b-instruct-v1:0",
    "us.meta.llama4-maverick-17b-instruct-v1:0",
    "us.amazon.nova-premier-v1:0",
    "us.amazon.nova-pro-v1:0",
    "us.mistral.pixtral-large-2502-v1:0"
]

def standardize_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))
    width, height = img.size
    
    # Determine if landscape or portrait and set target size
    if width > height:  # Landscape
        target_size = (1120, 1120)
    else:  # Portrait
        target_size = (1120, 1120)
    
    # Resize to standard dimensions
    if img.size != target_size:
        img = img.resize(target_size, Image.Resampling.LANCZOS)
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()

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
    
    # Convert image to PNG and standardize
    image = convert_to_png(image_path)
    image = standardize_image(image)
    
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
    
    # Call Bedrock with temperature 0.0
    response = bedrock_runtime.converse(
        modelId=model_id,
        messages=messages,
        inferenceConfig={"temperature": 0.0}
    )
    
    # Extract and return response
    response_text = response["output"]["message"]["content"][0]["text"]
    
    # Track cost
    input_tokens = cost_tracker.estimate_tokens(user_message)
    output_tokens = cost_tracker.estimate_tokens(response_text, is_output=True)
    cost_tracker.track_request(model_id, input_tokens, output_tokens)
    
    # Check if the response contains the prompt itself instead of the structured data
    if "## 🌿 Herbarium Label Transcription" in response_text or "**Herbarium Label Transcription**" in response_text:
        print("Warning: Response contains the prompt instead of structured data. Extracting only the field list...")
        
        # Try to find the actual field list in the response
        field_list_start = response_text.find("verbatimCollectors:")
        if field_list_start != -1:
            response_text = response_text[field_list_start:]
        else:
            print("Could not find field list in response. Please check the model output.")
    
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
    # Construct path to Collaged_Images folder
    images_folder = os.path.join(base_folder, "Collaged_Images")
    if not os.path.exists(images_folder):
        print(f"Error: Collaged_Images folder not found at {images_folder}")
        return
        
    print(f"Second Shot processing images from: {images_folder}")
    
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
    
    # Use pre-selected model or select one if not provided
    if model_id is None:
        model_id = select_model()
    
    # Store all transcriptions for batch file
    all_transcriptions = []
    
    # Process each image
    print(f"\nFound {len(image_files)} images to process")
    for i, image_path in enumerate(image_files, 1):
        print(50*"=")
        print(f"Processing image {i}/{len(image_files)}: {image_path.name}")
        
        try:
            # Process the image using the selected model
            response_text = process_image(image_path, prompt_path, model_id)
            
            # Get token counts for this request
            with open(prompt_path, "r") as f:
                user_message = f.read().strip()
            input_tokens = cost_tracker.estimate_tokens(user_message)
            output_tokens = cost_tracker.estimate_tokens(response_text, is_output=True)
            
            # Save individual JSON file
            json_filepath = save_json_transcription(
                output_dir, date_folder, "second_shot", 
                image_path.name, response_text, model_id, 
                input_tokens, output_tokens
            )
            
            # Add to batch collection
            from json_output import create_json_response
            json_response = create_json_response(
                image_path.name, response_text, model_id, 
                input_tokens, output_tokens
            )
            all_transcriptions.append(json_response)
            
            print(f"JSON saved to: {json_filepath}")
            
        except Exception as e:
            print(f"Error processing {image_path.name}: {str(e)}")
            # Create error JSON response
            error_response = {
                "error": str(e),
                "image_name": image_path.name,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            all_transcriptions.append(error_response)
    
    # Create batch JSON file
    if all_transcriptions:
        batch_filepath = create_batch_json_file(output_dir, date_folder, "second_shot", all_transcriptions)
        print(f"Batch JSON file created: {batch_filepath}")
    
    print(f"Second Shot processing completed successfully! JSON files saved to {output_dir}")

# Allow running this module directly for testing
if __name__ == "__main__":
    process_images()
