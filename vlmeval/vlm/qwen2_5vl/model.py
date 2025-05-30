from __future__ import annotations

import os
import warnings

import torch

from ..base import BaseModel
from .prompt import Qwen2VLPromptMixin
from ...smp import get_rank_and_world_size
import math

def ensure_image_url(image: str) -> str:
    prefixes = ['http://', 'https://', 'file://', 'data:image;']
    if any(image.startswith(prefix) for prefix in prefixes):
        return image
    if os.path.exists(image):
        return 'file://' + image
    raise ValueError(f'Invalid image: {image}')

def split_model(layers):
    device_map = {}

    total_gpus = torch.cuda.device_count()
    rank, world_size = get_rank_and_world_size()
    num_gpus = total_gpus // world_size
    # + 8 is virtual layers for the memory of visual
    # num_layers = 80 + 8 #64
    num_layers = layers #64
    num_layers_per_gpu = math.ceil(num_layers / num_gpus)
    num_layers_per_gpu = [num_layers_per_gpu] * num_gpus
    num_layers_per_gpu[0] -= 6
    num_layers_per_gpu[-1] -= 2
    layer_cnt = 0

    for i, num_layer in enumerate(num_layers_per_gpu):
        for j in range(num_layer):
            device_map[f'model.layers.{layer_cnt}'] = rank + i * world_size
            layer_cnt += 1

    last_gpu = rank + (num_gpus - 1) * world_size
    device_map['visual'] = rank
    device_map['model.embed_tokens'] = rank
    device_map['model.norm'] = last_gpu
    device_map['model.rotary_emb'] = last_gpu
    device_map['lm_head'] = last_gpu
    return device_map

class Qwen2_5VLChat(Qwen2VLPromptMixin, BaseModel):
    INSTALL_REQ = False
    INTERLEAVE = True

    def __init__(
        self,
        model_path: str,
        min_pixels: int | None = None,
        max_pixels: int | None = None,
        # max_new_tokens=12800,
        max_new_tokens=2000,
        top_p=0.001,
        top_k=1,
        temperature=0.01,
        repetition_penalty=1.0,
        use_custom_prompt: bool = True,
        system_prompt: str | None = None,
        verbose: bool = True,
    ):
        super().__init__(use_custom_prompt=use_custom_prompt)
        self.min_pixels = min_pixels
        self.max_pixels = max_pixels
        self.generate_kwargs = dict(
            max_new_tokens=max_new_tokens,
            top_p=top_p,
            top_k=top_k,
            temperature=temperature,
            repetition_penalty=repetition_penalty,
        )
        self.system_prompt = system_prompt
        self.verbose = verbose

        from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor

        assert model_path is not None
        self.model_path = model_path
        self.processor = AutoProcessor.from_pretrained(model_path)
        # self.model = Qwen2VLForConditionalGeneration.from_pretrained(
        #     model_path, torch_dtype='auto', device_map='auto', attn_implementation='flash_attention_2'
        # ).eval()
        # if '72b' not in self.model_path.lower() :
            # self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            #     model_path, trust_remote_code=True, torch_dtype='auto', device_map='cpu', attn_implementation='flash_attention_2'
            # )
            # self.model.cuda().eval()
        # else:
        #     self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        #         model_path, torch_dtype='auto', device_map=split_model(), attn_implementation='flash_attention_2'
        #     )
        #     self.model.eval()
        if '72b' in self.model_path.lower():
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                model_path, torch_dtype='auto', device_map="auto", attn_implementation='flash_attention_2'
                # model_path, torch_dtype='auto', device_map=split_model(80), attn_implementation='flash_attention_2'
            )
            self.model.eval()
        elif '32b' in self.model_path.lower():
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                model_path, torch_dtype='auto', device_map="auto", attn_implementation='flash_attention_2'
            )
            self.model.eval()
        else:
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                model_path, trust_remote_code=True, torch_dtype='auto', device_map='cpu', attn_implementation='flash_attention_2'
            )
            self.model.cuda().eval()
        torch.cuda.empty_cache()

    def _prepare_content(self, inputs: list[dict[str, str]], dataset: str | None = None) -> list[dict[str, str]]:
        """
        inputs list[dict[str, str]], each dict has keys: ['type', 'value']
        """
        content = []
        for s in inputs:
            if s['type'] == 'image':
                item = {'type': 'image', 'image': ensure_image_url(s['value'])}
                if dataset == 'OCRBench':
                    item['min_pixels'] = 10 * 10 * 28 * 28
                    warnings.warn(f"OCRBench dataset uses custom min_pixels={item['min_pixels']}")
                    if self.max_pixels is not None:
                        item['max_pixels'] = self.max_pixels
                else:
                    if self.min_pixels is not None:
                        item['min_pixels'] = self.min_pixels
                    if self.max_pixels is not None:
                        item['max_pixels'] = self.max_pixels
            elif s['type'] == 'text':
                item = {'type': 'text', 'text': s['value']}
            else:
                raise ValueError(f"Invalid message type: {s['type']}, {s}")
            content.append(item)
        return content

    def generate_inner(self, message, dataset=None):
        try:
            from qwen_vl_utils import process_vision_info
        except ImportError:
            warnings.warn("qwen_vl_utils not found, please install it via 'pip install qwen-vl-utils'")
            raise

        messages = []
        if self.system_prompt is not None:
            messages.append({'role': 'system', 'content': self.system_prompt})
        messages.append({'role': 'user', 'content': self._prepare_content(message, dataset=dataset)})
        if self.verbose:
            print(f'\033[31m{messages}\033[0m')

        text = self.processor.apply_chat_template([messages], tokenize=False, add_generation_prompt=True)
        images, videos = process_vision_info([messages])
        inputs = self.processor(text=text, images=images, videos=videos, padding=True, return_tensors='pt')
        inputs = inputs.to('cuda')

        generated_ids = self.model.generate(
            **inputs,
            **self.generate_kwargs,
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
        ]
        out = self.processor.tokenizer.batch_decode(
            generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
        response = out[0]
        if self.verbose:
            print(f'\033[32m{response}\033[0m')
        return response
    
    def chat_inner(self, messages, dataset=None):
        try:
            from qwen_vl_utils import process_vision_info
        except ImportError:
            warnings.warn("qwen_vl_utils not found, please install it via 'pip install qwen-vl-utils'")
            raise
        
        new_dict = []
        for item in messages:
            new_content = []
            for sub_item in item['content']:
                if sub_item['type'] == 'image':
                    new_sub_item = {'type': 'image', 'image': sub_item['value']}
                elif sub_item['type'] == 'text':
                    new_sub_item = {'type': 'text', 'text': sub_item['value']}
                elif sub_item['type'] == 'video':
                    new_sub_item = {'type': 'video', 'video': sub_item['value']}
                else:
                    new_sub_item = sub_item
                new_content.append(new_sub_item)
            new_dict.append({'role': item['role'], 'content': new_content})
        messages = new_dict
        if self.verbose:
            print(f'\033[31m{messages}\033[0m')

        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, add_vision_id=True)
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to("cuda")
        
        # generated_ids = self.model.generate(
        #     **inputs,
        #     **self.generate_kwargs,
        # )
        try:
            generated_ids = self.model.generate(
                **inputs,
                **self.generate_kwargs,
            )
        except Exception as e:
            print(f"Error during model.generate: {e}")
            raise

        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
        ]
        out = self.processor.tokenizer.batch_decode(
            generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
        response = out[0]
        

        if self.verbose:
            print(f'\033[32m{response}\033[0m')

        return response