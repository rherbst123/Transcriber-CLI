from art import *
from transcribers.FirstShot import First_Shot
from transcribers.SecondShot import Second_Shot
from transcribers.ThirdShot import Third_Shot
import os
from pathlib import Path

def select_models():
    print("\n=== Model Selection ===")
    
    print("Select model for First Shot transcriber:")
    first_shot_model = First_Shot.select_model()
    
    print("\nSelect model for Second Shot transcriber:")
    second_shot_model = Second_Shot.select_model()

    print("\nSelect model for Third Shot transcriber:")
    third_shot_model = Third_Shot.select_model()
    
    return first_shot_model, second_shot_model, third_shot_model

def select_folder():
    # Default path on desktop for Transcription_Ready_Images
    default_path = os.path.join(os.path.expanduser("~"), "Desktop", "Transcription_Ready_Images")
    base_folder = input(f"Enter path to Transcription_Ready_Images folder or Press enter for default [{default_path}]: ") or default_path 
    
    # Validate base folder
    if not os.path.exists(base_folder):
        print(f"Error: Folder not found at {base_folder}")
        return None, None
    
    # List date folders
    date_folders = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]
    if not date_folders:
        print(f"No date folders found in {base_folder}")
        return None, None
    
    # Display available date folders
    print("\nAvailable date folders:")
    for i, folder in enumerate(date_folders, 1):
        print(f"{i}. {folder}")
    
    # Select date folder
    while True:
        try:
            selection = int(input("\nSelect date folder number: "))
            if 1 <= selection <= len(date_folders):
                date_folder = date_folders[selection-1]
                break
            print(f"Please enter a number between 1 and {len(date_folders)}")
        except ValueError:
            print("Please enter a valid number")
    
    # Return the base path and selected date folder
    selected_folder = os.path.join(base_folder, date_folder)
    if not os.path.exists(selected_folder):
        print(f"Error: Selected folder not found at {selected_folder}")
        return None, None
        
    return selected_folder, date_folder

def main():
    tprint("Transcriber-cli")
    print("Created by: Riley Herbst")
    print(85*"=")
    print("Welcome to the Field Museum transcriber-cli, this is an all-purpose image transcriber.")
    print("Please make sure you have run your images through the segmentator. Instructions can be found here:")
    print("https://github.com/rherbst123/Segmentator")
    
    # Select folder once
    base_folder, date_folder = select_folder()
    if not base_folder:
        print("Exiting due to folder selection error.")
        return
    
    # Get prompt file
    prompt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Prompts", "Prompt_1.5.3.txt")
    prompt_path = input("Enter path to prompt file: ") or prompt_path 
    print(f"Using: {prompt_path}")
    if not os.path.exists(prompt_path):
        print(f"Error: Prompt file not found at {prompt_path}")
        return
    
    # Select models for both transcribers upfront
    first_shot_model, second_shot_model, third_shot_model = select_models()
    
    try:
        #First shot
        print("\n=== Running First Shot Transcriber ===")
        # Each module has its own transcription_results folder
        first_shot_output_dir = Path("FirstShot_results") / date_folder
        first_shot_output_dir.mkdir(exist_ok=True, parents=True)
        First_Shot.process_images(base_folder, prompt_path, first_shot_output_dir, date_folder, model_id=first_shot_model)
        
        # Second Shot
        print("\n=== Running Second Shot Transcriber ===")
        second_shot_output_dir = Path("SecondShot_results") / date_folder
        second_shot_output_dir.mkdir(exist_ok=True, parents=True)
        Second_Shot.process_images(base_folder, prompt_path, second_shot_output_dir, date_folder, model_id=second_shot_model)
        
        # Third Shot
        print("\n=== Running Third Shot Transcriber ===")
        third_shot_output_dir = Path("ThirdShot_results") / date_folder
        third_shot_output_dir.mkdir(exist_ok=True, parents=True)
        Third_Shot.process_images(base_folder, prompt_path, third_shot_output_dir, date_folder, model_id=third_shot_model)
        
        print("\nAll transcription processes completed, Thank you!")
    except Exception as e:
        print(f"\nError during transcription process: {str(e)}")

if __name__ == "__main__":
    main()
