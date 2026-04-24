
# 启动命令
# D:\project\llmapi>D:\program\python310_cuda\Scripts\python Qwen3-4B-Thinking.py


# from modelscope import AutoModelForCausalLM, AutoTokenizer
from modelscope import Qwen3VLForConditionalGeneration, AutoProcessor
model_name = "C:/llm/Qwen/Qwen3-VL-4B-Thinking"
# default: Load the model on the available device(s)
model = Qwen3VLForConditionalGeneration.from_pretrained(
    model_name, dtype="auto", device_map="auto"
)

# We recommend enabling flash_attention_2 for better acceleration and memory saving, especially in multi-image and video scenarios.
# model = Qwen3VLForConditionalGeneration.from_pretrained(
#     model_name,
#     dtype=torch.bfloat16,
#     attn_implementation="flash_attention_2",
#     device_map="auto",
# )

processor = AutoProcessor.from_pretrained(model_name)

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg",
            },
            {"type": "text", "text": "Describe this image."},
        ],
    }
]

# Preparation for inference
inputs = processor.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=True,
    return_dict=True,
    return_tensors="pt"
)
inputs = inputs.to(model.device)

# Inference: Generation of the output
generated_ids = model.generate(**inputs, max_new_tokens=128)
generated_ids_trimmed = [
    out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
]
output_text = processor.batch_decode(
    generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
)
print(output_text)


'''
D:\project\llmapi>D:\program\python310_cuda\Scripts\python Qwen3-4B-Thinking.py
Loading weights: 100%|███████████████████████████████████████████████████████████████| 713/713 [00:24<00:00, 29.41it/s]
["So, let's describe this image. First, the setting is a beach at sunset or sunrise, I think, because the sky is bright with warm light. The ocean is in the background with gentle waves. The main subjects are a woman and a dog sitting on the sandy beach.\n\nThe dog is a light-colored Labrador, maybe yellow or golden, sitting upright. It's wearing a harness with a colorful pattern—like small flowers or designs. The dog is reaching out its paw towards the woman, as if they're playfully interacting. The woman is sitting cross-legged on the sand, wearing a blue and white plaid shirt, dark"]
'''
