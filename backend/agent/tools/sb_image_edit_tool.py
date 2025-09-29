from typing import Optional
from agentpress.tool import ToolResult, openapi_schema, usage_example
from sandbox.tool_base import SandboxToolsBase
from agentpress.thread_manager import ThreadManager
import httpx
from io import BytesIO
import uuid
from litellm import aimage_generation, aimage_edit
import base64
import json
import mimetypes
import os
from urllib.parse import urlparse
from utils.config import config
import requests


class SandboxImageEditTool(SandboxToolsBase):
    """Tool for generating or editing images using OpenAI GPT Image 1 via OpenAI SDK (no mask support)."""

    def __init__(self, project_id: str, thread_id: str, thread_manager: ThreadManager):
        super().__init__(project_id, thread_manager)
        self.thread_id = thread_id
        self.thread_manager = thread_manager

    @openapi_schema(
        {
            "type": "function",
            "function": {
                "name": "image_edit_or_generate",
                "description": "Generate a new image from a prompt, or edit an existing image (no mask support) using OpenAI GPT Image 1 via OpenAI SDK. Stores the result in the thread context.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mode": {
                            "type": "string",
                            "enum": ["generate", "edit"],
                            "description": "'generate' to create a new image from a prompt, 'edit' to edit an existing image.",
                        },
                        "prompt": {
                            "type": "string",
                            "description": "Text prompt describing the desired image or edit.",
                        },
                        "image_path": {
                            "type": "string",
                            "description": "(edit mode only) Path to the image file to edit, relative to /workspace. Required for 'edit'.",
                        },
                    },
                    "required": ["mode", "prompt"],
                },
            },
        }
    )
    @usage_example("""
        <function_calls>
        <invoke name="image_edit_or_generate">
        <parameter name="mode">generate</parameter>
        <parameter name="prompt">A futuristic cityscape at sunset</parameter>
        </invoke>
        </function_calls>
        """)
    async def image_edit_or_generate(
        self,
        mode: str,
        prompt: str,
        image_path: Optional[str] = None,
    ) -> ToolResult:
        """Generate or edit images using OpenAI GPT Image 1 via OpenAI SDK (no mask support)."""
        try:
            await self._ensure_sandbox()

            if mode == "generate":
                response = await aimage_generation(
                    model="gpt-image-1",
                    prompt=prompt,
                    n=1,
                    size="1024x1024",
                )
            elif mode == "edit":
                if not image_path:
                    return self.fail_response("'image_path' is required for edit mode.")

                image_bytes = await self._get_image_bytes(image_path)
                if isinstance(image_bytes, ToolResult):  # Error occurred
                    return image_bytes

                # Create BytesIO object with proper filename to set MIME type
                image_io = BytesIO(image_bytes)
                image_io.name = (
                    "image.png"  # Set filename to ensure proper MIME type detection
                )

                response = await aimage_edit(
                    image=[image_io],  # Type in the LiteLLM SDK is wrong
                    prompt=prompt,
                    model="gpt-image-1",
                    n=1,
                    size="1024x1024",
                )
            else:
                return self.fail_response("Invalid mode. Use 'generate' or 'edit'.")

            # Download and save the generated image to sandbox
            image_filename = await self._process_image_response(response)
            if isinstance(image_filename, ToolResult):  # Error occurred
                return image_filename

            return self.success_response(
                f"Successfully generated image using mode '{mode}'. Image saved as: {image_filename}. You can use the ask tool to display the image."
            )

        except Exception as e:
            return self.fail_response(
                f"An error occurred during image generation/editing: {str(e)}"
            )

    async def _get_image_bytes(self, image_path: str) -> bytes | ToolResult:
        """Get image bytes from URL or local file path."""
        if image_path.startswith(("http://", "https://")):
            return await self._download_image_from_url(image_path)
        else:
            return await self._read_image_from_sandbox(image_path)

    async def _download_image_from_url(self, url: str) -> bytes | ToolResult:
        """Download image from URL."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
        except Exception:
            return self.fail_response(f"Could not download image from URL: {url}")

    async def _read_image_from_sandbox(self, image_path: str) -> bytes | ToolResult:
        """Read image from sandbox filesystem."""
        try:
            cleaned_path = self.clean_path(image_path)
            full_path = f"{self.workspace_path}/{cleaned_path}"

            # Check if file exists and is not a directory
            file_info = await self.sandbox.fs.get_file_info(full_path)
            if file_info.is_dir:
                return self.fail_response(
                    f"Path '{cleaned_path}' is a directory, not an image file."
                )

            return await self.sandbox.fs.download_file(full_path)

        except Exception as e:
            return self.fail_response(
                f"Could not read image file from sandbox: {image_path} - {str(e)}"
            )

    async def _process_image_response(self, response) -> str | ToolResult:
        """Download generated image and save to sandbox with random name."""
        try:
            original_b64_str = response.data[0].b64_json
            # Decode base64 image data
            image_data = base64.b64decode(original_b64_str)

            # Generate random filename
            random_filename = f"generated_image_{uuid.uuid4().hex[:8]}.png"
            sandbox_path = f"{self.workspace_path}/{random_filename}"

            # Save image to sandbox
            await self.sandbox.fs.upload_file(image_data, sandbox_path)
            return random_filename

        except Exception as e:
            return self.fail_response(f"Failed to download and save image: {str(e)}")


class SandboxImageEditToolAli(SandboxImageEditTool):
    """Tool for generating or editing images using Alibaba Tongyi models."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = config.DASHSCOPE_API_KEY or ""
        self.url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    @openapi_schema(
        {
            "type": "function",
            "function": {
                "name": "image_edit_or_generate",
                "description": "Generate a new image from a prompt, or edit an existing image using Alibaba Tongyi models.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mode": {
                            "type": "string",
                            "enum": ["generate", "edit"],
                            "description": "'generate' to create a new image from a prompt, 'edit' to edit an existing image.",
                        },
                        "prompt": {
                            "type": "string",
                            "description": "Text prompt describing the desired image or edit.",
                        },
                        "model": {
                            "type": "string",
                            "enum": ["qwen-image-plus", "qwen-image-edit"],
                            "description": "The image model to use. 'qwen-image-plus' for generation, 'qwen-image-edit' for editing. Auto-selected based on mode if not specified.",
                            "default": "auto"
                        },
                        "image_path": {
                            "type": "string",
                            "description": "(edit mode only) Path to the image file to edit. Can be: 1) Relative path to /workspace, or 2) Full URL.",
                        },
                        "size": {
                            "type": "string",
                            "enum": ["1328*1328", "1024*1024", "768*768"],
                            "description": "Image size for generation. Defaults to '1328*1328'.",
                            "default": "1328*1328"
                        },
                        "watermark": {
                            "type": "boolean",
                            "description": "Whether to add watermark for generated images. Defaults to True.",
                            "default": True
                        },
                        "prompt_extend": {
                            "type": "boolean",
                            "description": "Whether to extend the prompt for better results. Defaults to True.",
                            "default": True
                        }
                    },
                    "required": ["mode", "prompt"],
                },
            },
        }
    )
    @usage_example("""
        阿里通义生成图片示例:
        <function_calls>
        <invoke name="image_edit_or_generate">
        <parameter name="mode">generate</parameter>
        <parameter name="prompt">一副典雅庄重的对联悬挂于厅堂之中，房间是个安静古典的中式布置</parameter>
        <parameter name="model">qwen-image-plus</parameter>
        <parameter name="size">1328*1328</parameter>
        </invoke>
        </function_calls>
        
        阿里通义编辑图片示例:
        <function_calls>
        <invoke name="image_edit_or_generate">
        <parameter name="mode">edit</parameter>
        <parameter name="prompt">将图中的人物改为站立姿势，弯腰握住狗的前爪</parameter>
        <parameter name="image_path">generated_image_abc123.png</parameter>
        <parameter name="model">qwen-image-edit</parameter>
        </invoke>
        </function_calls>

        Multi-turn workflow (follow-up edits):
        1. User: "Create a logo" → generate mode
        2. User: "Make it more colorful" → edit mode (automatic)
        3. User: "Add text to it" → edit mode (automatic)
        """)
    async def image_edit_or_generate(
        self,
        mode: str,
        prompt: str,
        model: str = "auto",
        image_path: Optional[str] = None,
        size: str = "1328*1328",
        watermark: bool = True,
        prompt_extend: bool = True,
    ) -> ToolResult:
        """Generate or edit images using Alibaba Tongyi models via direct HTTP requests."""
        try:
            await self._ensure_sandbox()
            
            # Auto-select model based on mode
            if model == "auto":
                model = "qwen-image-plus" if mode == "generate" else "qwen-image-edit"
            
            if mode == "generate":
                # 生成图片逻辑，参考gen_img函数
                json_data = {
                    "model": model,
                    "input": {
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"text": prompt}
                                ]
                            }
                        ]
                    },
                    "parameters": {
                        "negative_prompt": "",
                        "prompt_extend": prompt_extend,
                        "watermark": watermark,
                        "size": size
                    }
                }
                
                # 使用requests库发送同步请求
                resp = requests.post(self.url, headers=self.headers, json=json_data)
                response_json = resp.json()
                
            elif mode == "edit":
                # 编辑图片逻辑，参考edit_img函数
                if not image_path:
                    return self.fail_response("'image_path' is required for edit mode.")
                
                # 获取图片字节数据
                image_bytes = await self._get_image_bytes(image_path)
                if isinstance(image_bytes, ToolResult):  # Error occurred
                    return image_bytes
                
                # 将图片转换为Base64编码，格式为 data:{mime_type};base64,{base64_data}
                mime_type = self._get_mime_type(image_path)
                encoded_string = base64.b64encode(image_bytes).decode('utf-8')
                base64_image = f"data:{mime_type};base64,{encoded_string}"
                
                # 构建请求数据
                json_data = {
                    "model": model,
                    "input": {
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"image": base64_image},
                                    {"text": prompt}
                                ]
                            }
                        ]
                    },
                    "parameters": {
                        "negative_prompt": "",
                        "watermark": False
                    }
                }
                
                # 使用requests库发送同步请求
                resp = requests.post(self.url, headers=self.headers, json=json_data)
                response_json = resp.json()
                
            else:
                return self.fail_response("Invalid mode. Use 'generate' or 'edit'.")
            
            # 处理响应
            if resp.status_code == 200:
                try:
                    # 解析响应获取图片URL
                    if 'output' in response_json and 'choices' in response_json['output'] and response_json['output']['choices']:
                        image_url = response_json['output']['choices'][0]['message']['content'][0]['image']
                        
                        # 下载并保存图片到sandbox
                        image_data = await self._download_image_from_url(image_url)
                        if isinstance(image_data, ToolResult):
                            return image_data
                        
                        # 生成随机文件名
                        random_filename = f"generated_image_{uuid.uuid4().hex[:8]}.png"
                        sandbox_path = f"{self.workspace_path}/{random_filename}"
                        
                        # 保存图片到sandbox
                        await self.sandbox.fs.upload_file(image_data, sandbox_path)
                        
                        return self.success_response(
                            f"Successfully processed image using mode '{mode}' with Alibaba Tongyi model '{model}'. Image saved as: {random_filename}. You can use the ask tool to display the image."
                        )
                    else:
                        return self.fail_response(f"Invalid API response format: {response_json}")
                    
                except Exception as e:
                    return self.fail_response(f"Failed to process API response: {str(e)}")
                    
            else:
                # 与参考函数保持一致的错误处理
                error_msg = f"HTTP返回码：{resp.status_code}"
                if 'code' in response_json:
                    error_msg += f", 错误码：{response_json['code']}"
                if 'message' in response_json:
                    error_msg += f", 错误信息：{response_json['message']}"
                return self.fail_response(error_msg)
                
        except Exception as e:
            return self.fail_response(
                f"An error occurred during image processing: {str(e)}"
            )
    
    def _get_mime_type(self, image_path: str) -> str:
        """Get MIME type from image path, similar to encode_file function."""
        try:
            if image_path.startswith(("http://", "https://")):
                # For URLs, extract the path part
                parsed = urlparse(image_path)
                mime_type, _ = mimetypes.guess_type(parsed.path)
            else:
                # For local files
                mime_type, _ = mimetypes.guess_type(image_path)
            
            if mime_type and mime_type.startswith("image/"):
                return mime_type
            else:
                return "image/png"  # Default fallback
        except Exception:
            return "image/png"  # Default fallback
