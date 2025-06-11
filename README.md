# Transcriber CLI

A command-line interface tool for transcribing herbarium label details from images using AWS Bedrock AI models.

## Overview

Transcriber CLI is designed to process and transcribe text from herbarium specimen images:

- **First Shot**: Processes full images to extract label information
- **Second Shot**: Processes collaged images (created by the Segmentator tool)
- **Third Shot**: Additional processing for enhanced accuracy

## Prerequisites

- Python 3.x
- AWS account with Bedrock access
- Properly configured AWS credentials: [AWS CLI](https://aws.amazon.com/cli/)
- Images processed through the [Segmentator](https://github.com/rherbst123/Segmentator) tool

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd Transcriber_CLI
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the main script:

```
python TranscribeCLI.py
```

The tool will:
1. Prompt you to select a folder containing processed images
2. Ask you to select AI models for each transcription phase
3. Process images and save transcription results to date-specific folders

### Expected Folder Structure

The tool expects images to be organized in the following structure:
```
Transcription_Ready_Images/
└── YYYY-MM-DD/
    ├── Full_Images/
    │   └── [image files]
    └── Collaged_Images/
        └── [image files]
```

## Supported AI Models

The tool supports multiple AWS Bedrock models:
- Claude 3 Sonnet
- Llama 3 (90B)
- Llama 4 Maverick
- Amazon Nova Premier
- Amazon Nova Pro
- Mistral Pixtral Large

##### More models will be added as they come out. 

## Output

Transcription results are saved in:
- `FirstShot_results/[date]/[date]_first_shot_transcriptions.txt`
- `SecondShot_results/[date]/[date]_first_shot_transcriptions.txt`

## Prompts

The tool uses specialized prompts for herbarium label transcription, located in the `Prompts/` directory. The default prompt (Prompt_1.5.3.txt) is designed to extract detailed information from herbarium labels following specific formatting rules.

## Customization

- Modify prompts in the `Prompts/` directory to adjust transcription behavior
- Add or remove models in the `AVAILABLE_MODELS` list in each transcriber module



Created by Riley Herbst, for the Field Museum

