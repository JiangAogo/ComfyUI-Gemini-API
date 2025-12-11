from google import genai
from google.genai import types
from PIL import Image
import torch
import numpy as np
import io
import tempfile
import os


class GeminiImageGeneratorNode:
    """
    ComfyUI节点：使用Google Gemini生成图像，暂时未处理多图参考
    """
    
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
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "Generate an image"
                }),
                "aspect_ratio": ([
                    "1:1", "2:3", "3:2", "3:4", "4:3", 
                    "4:5", "5:4", "9:16", "16:9", "21:9"
                ], {
                    "default": "9:16"
                }),
                "resolution": (["1K", "2K", "4K"], {
                    "default": "2K"
                }),
            },
            "optional": {
                "reference_image": ("IMAGE",),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_image"
    CATEGORY = "image/generation"
    
    def __init__(self):
        self.client = None
    
    def _init_client(self, api_key, host):
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
    
    def _gemini_image_to_pil(self, gemini_image):
        if hasattr(gemini_image, '_pil_image'):
            try:
                pil_image = gemini_image._pil_image
                if isinstance(pil_image, Image.Image):
                    print(f"成功通过 _pil_image 属性获取图像")
                    return pil_image
            except Exception as e:
                print(f"_pil_image 属性访问失败: {e}")
        
        for attr in ['data', '_data', 'image_data', '_image_bytes', 'bytes', '_bytes']:
            if hasattr(gemini_image, attr):
                try:
                    image_data = getattr(gemini_image, attr)
                    if isinstance(image_data, bytes):
                        pil_image = Image.open(io.BytesIO(image_data))
                        print(f"成功通过 {attr} 属性获取图像")
                        return pil_image
                except Exception as e:
                    print(f"{attr} 属性转换失败: {e}")
        
        for method in ['to_pil', 'as_pil', 'get_pil_image', 'to_pillow']:
            if hasattr(gemini_image, method):
                try:
                    result = getattr(gemini_image, method)()
                    if isinstance(result, Image.Image):
                        print(f"成功通过 {method}() 方法获取图像")
                        return result
                except Exception as e:
                    print(f"{method}() 方法调用失败: {e}")
        
        if hasattr(gemini_image, 'save'):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    temp_path = temp_file.name
                
                gemini_image.save(temp_path)
                pil_image = Image.open(temp_path)
                pil_image.load()
                
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    print(f"清理临时文件失败: {e}")
                
                print(f"成功通过 save() 方法获取图像")
                return pil_image
            except Exception as e:
                print(f"save() 方法失败: {e}")
        
        attrs = [attr for attr in dir(gemini_image) if not attr.startswith('__')]
        print(f"可用的属性和方法: {attrs}")
        raise TypeError(f"无法从 google.genai.types.Image 提取图像数据")
    
    def _pil_to_tensor(self, pil_image):
        # 如果是 google.genai.types.Image，先转换
        if hasattr(pil_image, '__class__') and 'google.genai' in str(type(pil_image)):
            pil_image = self._gemini_image_to_pil(pil_image)
        
        if not isinstance(pil_image, Image.Image):
            raise TypeError(f"无法处理的图像类型: {type(pil_image)}")
        
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        numpy_image = np.array(pil_image).astype(np.float32) / 255.0
        
        tensor = torch.from_numpy(numpy_image)
        
        return tensor.unsqueeze(0)
    
    def generate_image(self, api_key, host, prompt, aspect_ratio, resolution, reference_image=None):
        try:
            self._init_client(api_key, host)
            
            contents = [prompt]
            
            if reference_image is not None:
                pil_image = self._tensor_to_pil(reference_image)
                contents.append(pil_image)
                print(f"[Gemini] 参考图片已添加 - 尺寸: {pil_image.size}, 模式: {pil_image.mode}")
            else:
                print(f"[Gemini] 未提供参考图片")
            
            print(f"[Gemini] 发送请求参数:")
            print(f"  - Prompt长度: {len(prompt)} 字符")
            print(f"  - Contents数量: {len(contents)} (1=仅文本, 2=文本+图片)")
            print(f"  - 宽高比: {aspect_ratio}")
            print(f"  - 分辨率: {resolution}")
            
            response = self.client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image'],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                        image_size=resolution,
                    ),
                )
            )
            
            print(f"[Gemini] API响应已收到")
            
            generated_image = None
            text_parts = []
            image_parts = 0
            
            for i, part in enumerate(response.parts):
                if part.text is not None:
                    text_parts.append(part.text)
                    print(f"[Gemini] 响应部分 {i}: 文本 ({len(part.text)} 字符)")
                else:
                    try:
                        image = part.as_image()
                        if image is not None:
                            image_parts += 1
                            generated_image = image
                            print(f"[Gemini] 响应部分 {i}: 图像 (类型: {type(image).__name__})")
                    except Exception as e:
                        print(f"[Gemini] 响应部分 {i}: 处理图像时出错 - {str(e)}")
                        continue
            
            print(f"[Gemini] 响应统计: {len(text_parts)} 个文本部分, {image_parts} 个图像部分")
            if text_parts:
                for i, text in enumerate(text_parts):
                    print(f"  文本 {i+1}: {text[:100]}..." if len(text) > 100 else f"  文本 {i+1}: {text}")
            
            if generated_image is None:
                raise ValueError("未能从API响应中获取图像")
            

            output_tensor = self._pil_to_tensor(generated_image)
            print(f"[Gemini] 输出图像张量形状: {output_tensor.shape}")
            
            return (output_tensor,)
            
        except Exception as e:
            print(f"[Gemini] ❌ 生成图像时出错: {str(e)}")
            raise



NODE_CLASS_MAPPINGS = {
    "GeminiImageGenerator": GeminiImageGeneratorNode
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "GeminiImageGenerator": "Gemini Image Generator"
}