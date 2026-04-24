from transformers import AutoModelForCausalLM, AutoTokenizer
model_path = "D:\\llm\\Nanbeige\\Nanbeige4.1-3B"
tokenizer = AutoTokenizer.from_pretrained(
  model_path,
  use_fast=False,
  trust_remote_code=True
)
model = AutoModelForCausalLM.from_pretrained(
  model_path,
  torch_dtype='auto',
  device_map='auto',
  trust_remote_code=True
)
model.generation_config.max_new_tokens = 2048
while True:
    content = input("请输入: ")
    messages = [
    {'role': 'user', 'content': content}
    ]
    prompt = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=False
    )
    input_ids = tokenizer(prompt, add_special_tokens=False, return_tensors='pt').input_ids
    output_ids = model.generate(input_ids.to('cuda'))
    resp = tokenizer.decode(output_ids[0][len(input_ids[0]):], skip_special_tokens=True)
    print("================")
    print(resp)
