import torch
from transformers import Qwen3VLForConditionalGeneration, AutoProcessor, AutoConfig

# 设置使用GPU:0
device = "cuda:0"
print(f"使用设备: {device}")
print(f"GPU可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU名称: {torch.cuda.get_device_name(0)}")

# 模型路径
model_path = "D:/llm/Qwen/Qwen3-VL-4B-Instruct"

# 加载配置
config = AutoConfig.from_pretrained(model_path)

# 确保pad_token_id存在
if hasattr(config, 'text_config'):
    if not hasattr(config.text_config, 'pad_token_id') or config.text_config.pad_token_id is None:
        config.text_config.pad_token_id = getattr(config.text_config, 'bos_token_id', 151643)
        print(f"设置pad_token_id为: {config.text_config.pad_token_id}")

# 加载模型，指定使用GPU:0
print("开始加载模型...")
model = Qwen3VLForConditionalGeneration.from_pretrained(
    model_path,
    config=config,
    dtype=torch.bfloat16,  # 使用bfloat16加速计算
    device_map="auto"     # 自动分配设备
)
print(f"模型加载完成，当前设备: {next(model.parameters()).device}")

# 加载处理器
processor = AutoProcessor.from_pretrained(model_path)

def getMessage(prompt,img_url):
    messages = [
        {
            "role": "user",
            "content": [],
        }
    ]
    if prompt is None or prompt.strip() == "":
        prompt = "用中文描述图片。"
    messages[0]["content"].append({"type": "text", "text": prompt})
    
    if img_url is not None and img_url.strip() != "":
        # img_url = "https://pics5.baidu.com/feed/962bd40735fae6cdc3a098830069193543a70f22.jpeg"
        messages[0]["content"].append({"type": "image", "image": img_url})  
    
    if len(messages[0]["content"]) == 0:
        return "请输入图片URL或描述。"
    # 处理输入
    inputs = processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt"
    )

    # 将输入移动到GPU:0
    inputs = {k: v.to(device) for k, v in inputs.items()}
    # print(f"输入数据处理完成，输入设备: {inputs['input_ids'].device}")

    # 生成文本
    try:
        # 获取并使用模型的generation_config
        generation_config = model.generation_config
        
        # 更新generation_config中的参数
        generation_config.max_new_tokens = 128
        generation_config.temperature = 0.7
        generation_config.top_p = 0.95
        generation_config.do_sample = True
        generation_config.pad_token_id = config.text_config.pad_token_id
        generation_config.num_beams = 1
        generation_config.use_cache = True
        
        # 使用更新后的generation_config生成文本
        generated_ids = model.generate(
            **inputs,
            generation_config=generation_config
        )
        # print("文本生成完成")

        # 解码结果
        # print("开始解码结果...")
        generated_ids_trimmed = generated_ids[:, inputs['input_ids'].shape[1]:]
        # print(f"生成的token数量: {generated_ids_trimmed.shape[1]}")
        output_text = processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )
        # print("结果解码完成")
        # print(f"解码后的文本长度: {len(output_text[0]) if output_text else 0}")

        # 打印结果
        # print("\n推理结果:")
        # print(output_text[0] if output_text else "无输出结果")
        return output_text[0] if output_text else "无输出结果"
    except Exception as e:
        # print(f"生成文本时出错: {e}")
        # import traceback
        # traceback.print_exc() 
        return f"生成文本时出错: {e}"
img_url = ""
prompt = ""
for i in range(10):
    img_url = input("请输入图片地址：")
    prompt = input("请输入描述：")
    if prompt == "exit":
        break
    prompt = prompt.strip()+"\n请简单回答。"
    content = getMessage(prompt,img_url)
    print("回答:", content)

