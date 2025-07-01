from art import *
from transcribers.FirstShot import First_Shot
from transcribers.SecondShot import Second_Shot
from cost_analysis import cost_tracker
from txt_to_csv import convert_json_to_csv
import os
from pathlib import Path
import requests
from urllib.parse import urlparse

def select_shots():
    while True:
        choice = input("\nChoose processing mode:\n1. One shot\n2. Two shots\nEnter choice (1-2): ")
        if choice in ['1', '2']:
            return int(choice)
        print("Please enter 1 or 2")

def select_one_shot_type():
    while True:
        choice = input("\nChoose image type for one shot:\n1. Segmented images\n2. Full images\nEnter choice (1-2): ")
        if choice in ['1', '2']:
            return choice
        print("Please enter 1 or 2")

def select_full_image_source():
    while True:
        choice = input("\nChoose full image source:\n1. Local images\n2. URL download\nEnter choice (1-2): ")
        if choice in ['1', '2']:
            return choice == '2'
        print("Please enter 1 or 2")

def get_run_name():
    run_name = input("\nEnter a name for this run (or press Enter for default): ").strip()
    if not run_name:
        from datetime import datetime
        run_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Sanitize filename
    import re
    run_name = re.sub(r'[<>:"/\\|?*]', '_', run_name)
    return run_name

def download_images_from_urls(url_file_path, download_dir):
    """Download images from URLs in a text file"""
    if not os.path.exists(url_file_path):
        print(f"Error: URL file not found at {url_file_path}")
        return False
    
    # Clear existing images
    if os.path.exists(download_dir):
        import shutil
        shutil.rmtree(download_dir)
    
    os.makedirs(download_dir, exist_ok=True)
    
    with open(url_file_path, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"\nDownloading {len(urls)} images...")
    for i, url in enumerate(urls, 1):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Get original filename and add index prefix
            original_filename = os.path.basename(urlparse(url).path) or f"image_{i}.jpg"
            filename = f"{i:04d}_{original_filename}"
            filepath = os.path.join(download_dir, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Downloaded {i}/{len(urls)}: {filename}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")
    
    return True

def get_segmented_folder():
    default_path = os.path.join(os.path.expanduser("~"), "Desktop", "Transcription_Ready_Images")
    base_folder = input(f"Enter path to Transcription_Ready_Images folder or Press enter for default [{default_path}]: ") or default_path 
    
    if not os.path.exists(base_folder):
        print(f"Error: Folder not found at {base_folder}")
        return None, None
    
    date_folders = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]
    if not date_folders:
        print(f"No date folders found in {base_folder}")
        return None, None
    
    print("\nAvailable date folders:")
    for i, folder in enumerate(date_folders, 1):
        print(f"{i}. {folder}")
    
    while True:
        try:
            selection = int(input("\nSelect date folder number: "))
            if 1 <= selection <= len(date_folders):
                date_folder = date_folders[selection-1]
                break
            print(f"Please enter a number between 1 and {len(date_folders)}")
        except ValueError:
            print("Please enter a valid number")
    
    selected_folder = os.path.join(base_folder, date_folder)
    if not os.path.exists(selected_folder):
        print(f"Error: Selected folder not found at {selected_folder}")
        return None, None
        
    return selected_folder, date_folder

def select_prompt():
    prompts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Prompts")
    
    if os.path.exists(prompts_dir):
        prompt_files = [f for f in os.listdir(prompts_dir) if f.endswith('.txt')]
        if prompt_files:
            print("\nAvailable prompts:")
            for i, prompt in enumerate(prompt_files, 1):
                print(f"{i}. {prompt}")
            print(f"{len(prompt_files) + 1}. Custom filepath")
            
            while True:
                try:
                    choice = int(input(f"\nSelect prompt (1-{len(prompt_files) + 1}): "))
                    if 1 <= choice <= len(prompt_files):
                        return os.path.join(prompts_dir, prompt_files[choice-1])
                    elif choice == len(prompt_files) + 1:
                        return input("Enter custom prompt filepath: ")
                    print(f"Please enter a number between 1 and {len(prompt_files) + 1}")
                except ValueError:
                    print("Please enter a valid number")
    
    return input("Enter prompt filepath: ")

def get_full_images_folder(use_urls):
    if use_urls:
        url_file = input("\nEnter path to .txt file containing image URLs: ")
        download_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Downloaded_Images")
        
        if download_images_from_urls(url_file, download_dir):
            return download_dir, "downloaded_images"
        else:
            return None, None
    else:
        folder_path = input("\nEnter path to local images folder: ")
        if not os.path.exists(folder_path):
            print(f"Error: Folder not found at {folder_path}")
            return None, None
        return folder_path, os.path.basename(folder_path)

def main():
    tprint("Transcriber-cli")
    print("Created by: Riley Herbst")
    print(85*"=")
    print("Welcome to the Field Museum transcriber-cli, this is an all-purpose image transcriber.")
    
    # Get run name
    run_name = get_run_name()
    print(f"Run name: {run_name}")
    
    # Select number of shots
    num_shots = select_shots()
    
    # Get prompt file
    prompt_path = select_prompt()
    print(f"Using: {prompt_path}")
    if not os.path.exists(prompt_path):
        print(f"Error: Prompt file not found at {prompt_path}")
        return
    
    try:
        if num_shots == 1:
            # One shot - user chooses type
            image_type = select_one_shot_type()
            
            if image_type == '1':  # Segmented
                print("\nPlease make sure you have run your images through the segmentator.")
                print("Instructions: https://github.com/rherbst123/Segmentator")
                base_folder, date_folder = get_segmented_folder()
                if not base_folder:
                    print("Exiting due to folder selection error.")
                    return
                
                print("\nSelect model for segmented image processing:")
                model = Second_Shot.select_model()
                
                output_dir = Path("SecondShot_results") / run_name
                output_dir.mkdir(exist_ok=True, parents=True)
                Second_Shot.process_images(base_folder, prompt_path, output_dir, run_name, model_id=model)
                
                # Convert JSON files to CSV
                print("\n=== Converting JSON files to CSV ===")
                convert_json_to_csv(str(output_dir))
                
            else:  # Full images
                use_urls = select_full_image_source()
                base_folder, date_folder = get_full_images_folder(use_urls)
                if not base_folder:
                    print("Exiting due to folder selection error.")
                    return
                
                print("\nSelect model for full image processing:")
                model = First_Shot.select_model()
                
                output_dir = Path("FirstShot_results") / run_name
                output_dir.mkdir(exist_ok=True, parents=True)
                First_Shot.process_images(base_folder, prompt_path, output_dir, run_name, model_id=model)
                
                # Convert JSON files to CSV
                print("\n=== Converting JSON files to CSV ===")
                convert_json_to_csv(str(output_dir))
        
        else:  # Two shots - use Transcription_Ready_Images
            print("\nTwo shots mode: Full images + Segmented images from Transcription_Ready_Images")
            print("\nPlease make sure you have run your images through the segmentator.")
            print("Instructions: https://github.com/rherbst123/Segmentator")
            
            base_folder, date_folder = get_segmented_folder()
            if not base_folder:
                print("Exiting due to folder selection error.")
                return
            
            print("\nSelect model for full image processing:")
            model1 = First_Shot.select_model()
            print("\nSelect model for segmented image processing:")
            model2 = Second_Shot.select_model()
            
            # Run First Shot (full images)
            print("\n=== Running First Shot (Full Images) ===")
            output_dir1 = Path("FirstShot_results") / run_name
            output_dir1.mkdir(exist_ok=True, parents=True)
            First_Shot.process_images(base_folder, prompt_path, output_dir1, run_name, model_id=model1)
            
            # Convert First Shot JSON files to CSV
            print("\n=== Converting First Shot JSON files to CSV ===")
            convert_json_to_csv(str(output_dir1))
            
            # Run Second Shot (segmented images)
            print("\n=== Running Second Shot (Segmented Images) ===")
            output_dir2 = Path("SecondShot_results") / run_name
            output_dir2.mkdir(exist_ok=True, parents=True)
            Second_Shot.process_images(base_folder, prompt_path, output_dir2, run_name, model_id=model2)
            
            # Convert Second Shot JSON files to CSV
            print("\n=== Converting Second Shot JSON files to CSV ===")
            convert_json_to_csv(str(output_dir2))
        
        print("\nTranscription and CSV conversion completed, Thank you!")
        
        # Generate and save cost analysis report
        print("\n=== Generating Cost Analysis Report ===")
        cost_tracker.save_report_to_desktop(run_name)
        
    except Exception as e:
        print(f"\nError during transcription process: {str(e)}")
        # Still generate cost report even if there was an error
        print("\n=== Generating Cost Analysis Report ===")
        cost_tracker.save_report_to_desktop(run_name)

if __name__ == "__main__":
    main()
