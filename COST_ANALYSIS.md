# Cost Analysis Feature

The Transcriber CLI now includes comprehensive cost tracking for AWS Bedrock usage.

## Features

- **Real-time Cost Tracking**: Monitors token usage and calculates costs during processing
- **Model-specific Pricing**: Accurate pricing for all supported Bedrock models
- **Detailed Reports**: Comprehensive cost breakdown saved to desktop
- **Session Tracking**: Tracks total processing time and image counts

## Supported Models & Pricing

| Model | Provider | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------|----------------------|------------------------|
| Claude 3 Sonnet | Anthropic | $3.00 | $15.00 |
| Claude 3.5 Sonnet | Anthropic | $3.00 | $15.00 |
| Claude 3 Haiku | Anthropic | $0.25 | $1.25 |
| Claude 3 Opus | Anthropic | $15.00 | $75.00 |
| Llama 3.2 90B | Meta | $2.00 | $2.00 |
| Llama 3.2 11B | Meta | $0.35 | $0.35 |
| Llama 3.2 1B | Meta | $0.10 | $0.10 |
| Nova Premier | Amazon | $2.50 | $12.50 |
| Nova Pro | Amazon | $0.80 | $3.20 |
| Nova Lite | Amazon | $0.06 | $0.24 |
| Nova Micro | Amazon | $0.035 | $0.14 |
| Pixtral Large | Mistral | $3.00 | $9.00 |
| Mistral Large | Mistral | $3.00 | $9.00 |

## Usage

The cost analysis runs automatically when you use the Transcriber CLI:

1. **During Processing**: Costs are tracked in real-time for each API call
2. **After Completion**: A detailed report is automatically saved to your desktop
3. **Report Location**: `~/Desktop/bedrock_cost_analysis_YYYYMMDD_HHMMSS.txt`

## Report Contents

Each cost analysis report includes:

- **Session Summary**: Total time, images processed, and estimated cost
- **Model Breakdown**: Per-model usage statistics and costs
- **Token Counts**: Input and output token usage for each model
- **Pricing Reference**: Current pricing information for all models

## View Current Pricing

To see current model pricing without running a transcription:

```bash
python show_pricing.py
```

## Cost Estimation

- Token counts are estimated using a 4:1 character-to-token ratio
- Actual AWS billing may vary slightly from estimates
- Reports provide conservative estimates for budgeting purposes

## Notes

- Cost tracking has minimal performance impact
- Reports are generated even if processing encounters errors
- All pricing is based on AWS Bedrock rates as of 2025
- Image processing may include additional base costs not reflected in token pricing