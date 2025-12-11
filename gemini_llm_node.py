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
                "model": (["gemini-3-pro-preview", "gemini-2.0-flash-exp", "gemini-1.5-pro"], {
                    "default": "gemini-3-pro-preview"
                }),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Tell me about this"
                }),
            },
            "optional": {
                "image": ("IMAGE",),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate_text"
    CATEGORY = "text/generation"
    
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
            tensor = tensor[0]  # 取第一张图片
        
        numpy_image = (tensor.cpu().numpy() * 255).astype(np.uint8)
        return Image.fromarray(numpy_image)
    
    def generate_text(self, api_key, host, model, prompt, image=None):
        try:
            self._init_client(api_key, host)

            contents = []

            if image is not None:
                pil_image = self._tensor_to_pil(image)
                contents.append(pil_image)
                print(f"已添加图像到请求，尺寸: {pil_image.size}")
            
            contents.append(prompt)
            
            print(f"使用模型: {model}")
            print(f"提示词: {prompt[:100]}..." if len(prompt) > 100 else f"提示词: {prompt}")
            
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


# ComfyUI节点注册
NODE_CLASS_MAPPINGS = {
    "GeminiLLM": GeminiLLMNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeminiLLM": "Gemini LLM"
}