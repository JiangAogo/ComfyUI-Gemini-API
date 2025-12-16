from google import genai
from PIL import Image
import torch
import numpy as np


class GeminiLLMNode: 
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {
                    "multiline": False,
                    "default": "your api key"
                }),
                "host": ("STRING", {
                    "multiline": False,
                    "default": "enter the host"
                }),
                "model": (["gemini-3-pro-preview"], {
                    "default": "gemini-3-pro-preview"
                }),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Tell me about this"
                }),
            },
            "optional": {
                "system_prompt": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "image": ("IMAGE",),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate_text"
    CATEGORY = "text/generation"
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")
    
    def __init__(self):
        self.client = None
    
    def _init_client(self, api_key, host):
        if self.client is None:
            print(f"正在连接代理: {host} ...")
            self.client = genai.Client(
                api_key=api_key,
                http_options={
                    'base_url': host,
                    'api_version': 'v1beta',
                }
            )
    
    def _tensor_to_pil(self, tensor):
        # tensor shape: [B, H, W, C]
        if len(tensor.shape) == 4:
            tensor = tensor[0]
        
        numpy_image = (tensor.cpu().numpy() * 255).astype(np.uint8)
        return Image.fromarray(numpy_image)
    
    def generate_text(self, api_key, host, model, prompt, system_prompt=None, image=None):
        try:
            self._init_client(api_key, host)

            contents = []

            if image is not None:
                pil_image = self._tensor_to_pil(image)
                contents.append(pil_image)
                print(f"已添加图像到请求，尺寸: {pil_image.size}")
            
            contents.append(prompt)
            
            print(f"使用模型: {model}")
            if system_prompt and system_prompt.strip():
                print(f"系统提示词: {system_prompt[:100]}..." if len(system_prompt) > 100 else f"系统提示词: {system_prompt}")
            print(f"用户提示词: {prompt[:100]}..." if len(prompt) > 100 else f"用户提示词: {prompt}")
            
            config = None
            if system_prompt and system_prompt.strip():
                config = types.GenerateContentConfig(
                    system_instruction=system_prompt
                )
            
            if config:
                response = self.client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config
                )
            else:
                response = self.client.models.generate_content(
                    model=model,
                    contents=contents
                )
            
            result_text = response.text
            print(f"生成的文本长度: {len(result_text)} 字符")
            
            return (result_text,)
            
        except Exception as e:
            error_msg = f"生成文本时出错: {str(e)}"
            print(error_msg)
            return (error_msg,)


NODE_CLASS_MAPPINGS = {
    "GeminiLLM": GeminiLLMNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeminiLLM": "Gemini LLM"
}
