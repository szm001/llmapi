import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import Qwen3VLForConditionalGeneration, AutoProcessor, AutoConfig
from config import config
import logging
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

logger = logging.getLogger(__name__)


class ModelService:
    _instance = None
    _model = None
    _processor = None
    _config = None
    _device = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self._initialize()
    
    def _initialize(self):
        logger.info(f"初始化模型服务...")
        logger.info(f"使用设备: {config.DEVICE}")
        logger.info(f"GPU可用: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            logger.info(f"GPU名称: {torch.cuda.get_device_name(0)}")
        
        try:
            self._config = AutoConfig.from_pretrained(config.MODEL_PATH)
            
            if hasattr(self._config, 'text_config'):
                if not hasattr(self._config.text_config, 'pad_token_id') or self._config.text_config.pad_token_id is None:
                    self._config.text_config.pad_token_id = getattr(self._config.text_config, 'bos_token_id', 151643)
                    logger.info(f"设置pad_token_id为: {self._config.text_config.pad_token_id}")
            
            logger.info("开始加载模型...")
            self._model = Qwen3VLForConditionalGeneration.from_pretrained(
                config.MODEL_PATH,
                config=self._config,
                dtype=torch.bfloat16,
                device_map="auto"
            )
            self._device = next(self._model.parameters()).device
            logger.info(f"模型加载完成，当前设备: {self._device}")
            
            self._processor = AutoProcessor.from_pretrained(config.MODEL_PATH)
            logger.info("处理器加载完成")
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    def generate_response(self, prompt: str, image_url: str = None, 
                         max_new_tokens: int = None, 
                         temperature: float = None, 
                         top_p: float = None) -> str:
        try:
            messages = [{"role": "user", "content": []}]
            
            if prompt is None or prompt.strip() == "":
                prompt = "用中文描述图片。"
            messages[0]["content"].append({"type": "text", "text": prompt})
            
            if image_url is not None and image_url.strip() != "":
                messages[0]["content"].append({"type": "image", "image": image_url})
            
            if len(messages[0]["content"]) == 0:
                return "请输入图片URL或描述。"
            
            inputs = self._processor.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                return_dict=True,
                return_tensors="pt"
            )
            
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            
            generation_config = self._model.generation_config
            
            generation_config.max_new_tokens = max_new_tokens or config.MAX_NEW_TOKENS
            generation_config.temperature = temperature or config.TEMPERATURE
            generation_config.top_p = top_p or config.TOP_P
            generation_config.do_sample = True
            generation_config.pad_token_id = self._config.text_config.pad_token_id
            generation_config.num_beams = 1
            generation_config.use_cache = True
            
            generated_ids = self._model.generate(
                **inputs,
                generation_config=generation_config
            )
            
            generated_ids_trimmed = generated_ids[:, inputs['input_ids'].shape[1]:]
            output_text = self._processor.batch_decode(
                generated_ids_trimmed,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )
            
            return output_text[0] if output_text else "无输出结果"
            
        except Exception as e:
            logger.error(f"生成响应时出错: {e}")
            raise
    
    def is_loaded(self) -> bool:
        return self._model is not None
    
    def get_device(self) -> str:
        return str(self._device) if self._device else "未加载"



class CodeModelService:
    _instance = None
    _model = None
    _processor = None
    _config = None
    _device = None
    _tokenizer = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self._initialize()
    
    def _initialize(self):
        logger.info(f"初始化模型服务...")
        logger.info(f"使用设备: {config.DEVICE}")
        logger.info(f"GPU可用: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            logger.info(f"GPU名称: {torch.cuda.get_device_name(0)}")
        
        try:
            model_name = "Qwen/Qwen2.5-Coder-7B-Instruct"
            model_name = "D:\llm\Qwen\Qwen2.5-Coder-7B-Instruct"

            self._model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype="auto",
                device_map="auto"
            )
            self._tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            logger.info("处理器加载完成")
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    def generate_response(self, prompt: str, image_url: str = None, 
                         max_new_tokens: int = None, 
                         temperature: float = None, 
                         top_p: float = None) -> str:
        try:

            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
            text = self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            model_inputs = self._tokenizer([text], return_tensors="pt").to(self._device)

            generated_ids = self._model.generate(
                **model_inputs,
                max_new_tokens=max_new_tokens or config.MAX_NEW_TOKENS
            )
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]

            response = self._tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            return response
        except Exception as e:
            logger.error(f"生成响应时出错: {e}")
            raise
    
    def is_loaded(self) -> bool:
        return self._model is not None
    
    def get_device(self) -> str:
        return str(self._device) if self._device else "未加载"
