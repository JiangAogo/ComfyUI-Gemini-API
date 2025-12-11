# ComfyUI-Gemini

ComfyUI custom nodes for Google Gemini API integration, supporting both text generation (LLM) and image generation.

## Features

- 🖼️ **Gemini Image Generator**: Generate images using Gemini 3 Pro Image Preview model
- 💬 **Gemini LLM**: Generate text responses with optional image input using Gemini models
- 🔄 Support for reference images in both nodes
- 🎨 Customizable aspect ratios and resolutions for image generation
- 🌐 Proxy support for API access

## Nodes

### 1. Gemini Image Generator

Generate images using Google's Gemini 3 Pro Image Preview model.

**Inputs:**
- `api_key` (required): Your Google Gemini API key
- `host` (required): API endpoint URL
- `prompt` (required): Text description for image generation
- `aspect_ratio` (required): Choose from 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
- `resolution` (required): 1K, 2K, or 4K
- `reference_image` (optional): Reference image for style/content guidance

**Outputs:**
- `image`: Generated image tensor (ComfyUI format)

**Features:**
- Detailed debug logging for troubleshooting
- Support for reference images
- Multiple aspect ratios and resolutions
- Automatic image format conversion

### 2. Gemini LLM

Generate text using Google's Gemini language models with optional image input.

**Inputs:**
- `api_key` (required): Your Google Gemini API key
- `host` (required): API endpoint URL
- `model` (required): Choose from:
  - `gemini-3-pro-preview`
  - `gemini-2.0-flash-exp`
  - `gemini-1.5-pro`
- `prompt` (required): Your text prompt
- `image` (optional): Image for multimodal prompts

**Outputs:**
- `text`: Generated text response

**Features:**
- Multiple Gemini model support
- Vision capabilities (when image is provided)
- Error handling with informative messages
- Debug logging for monitoring

## Usage Example

### Image Generation Workflow

```
[Gemini Image Generator]
├─ api_key: "your-api-key"
├─ host: "https://your-proxy-url"
├─ prompt: "A beautiful sunset over mountains"
├─ aspect_ratio: "16:9"
├─ resolution: "2K"
└─ reference_image: (optional) -> [Your Image]
    └─ image -> [Preview Image] or [Save Image]
```

### Text Generation Workflow

```
[Load Image] (optional)
    └─ image
        └─ [Gemini LLM]
           ├─ api_key: "your-api-key"
           ├─ host: "https://your-proxy-url"
           ├─ model: "gemini-3-pro-preview"
           ├─ prompt: "Describe this image in detail"
           └─ text -> [Display Text] or [Save Text]
```

## Debug Information

Both nodes provide detailed console logging:

**Gemini Image Generator logs:**
- `[Gemini] 参考图片已添加` - Reference image info
- `[Gemini] 发送请求参数` - Request parameters
- `[Gemini] 响应统计` - Response statistics
- `[Gemini] 输出图像张量形状` - Output tensor shape

**Gemini LLM logs:**
- Image dimensions when provided
- Model selection
- Prompt preview
- Generated text length

## Configuration

### API Key Setup

1. Get your Google Gemini API key from [Google AI Studio]
2. If using a proxy, configure the `host` parameter accordingly

### Default Values

You can modify default values in the node code:
- `api_key`: Update in `INPUT_TYPES` default value
- `host`: Update your proxy URL in default value
- `aspect_ratio`: Default is "9:16"
- `resolution`: Default is "2K"
- `model`: Default is "gemini-3-pro-preview"

## Troubleshooting

### No Image Generated
- Check console for `[Gemini] Contents数量` - should be 2 if reference image is provided
- Verify `[Gemini] 响应统计` shows image parts > 0
- Ensure API key and host are correct

### Text Generation Errors
- Verify model name is correct
- Check if image format is compatible (RGB mode)
- Review console error messages

### Connection Issues
- Verify host URL is accessible
- Check API key validity
- Ensure proxy (if used) is properly configured

## Requirements

- ComfyUI
- Python 3.8+
- google-genai
- Pillow
- torch
- numpy

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Note**: This project uses Google's Gemini API. Make sure to comply with Google's terms of service and usage policies.