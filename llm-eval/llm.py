from typing import List
import replicate
from schema import Conversation, Message, ModelConfig
from retrieve import retrieve

FRIENDLY_MAPPING = {
    "Snowflake Arctic": "snowflake/snowflake-arctic-instruct",
    "LLaMa 3 8B": "meta/meta-llama-3-8b",
    "Mistral 7B": "mistralai/mistral-7b-instruct-v0.2",
}
AVAILABLE_MODELS = [k for k in FRIENDLY_MAPPING.keys()]


def encode_arctic(messages: List[Message]):
    prompt = []
    for msg in messages:
        prompt.append(f"<|im_start|>{msg.role}\n{msg.content}<|im_end|>")

    prompt.append("<|im_start|>assistant")
    prompt.append("")
    prompt_str = "\n".join(prompt)
    return prompt_str


def encode_llama3(messages: List[Message]):
    prompt = []
    prompt.append("<|begin_of_text|>")
    for msg in messages:
        prompt.append(f"<|start_header_id|>{msg.role}<|end_header_id|>")
        prompt.append(f"{msg.content.strip()}<|eot_id|>")
    prompt.append("<|start_header_id|>assistant<|end_header_id|>")
    prompt.append("")
    prompt_str = "\n\n".join(prompt)
    return prompt_str


def encode_generic(messages: List[Message]):
    prompt = []
    for msg in messages:
        prompt.append(f"{msg.role}:\n" + msg.content)

    prompt.append("assistant:")
    prompt.append("")
    prompt_str = "\n".join(prompt)
    return prompt_str


ENCODING_MAPPING = {
    "snowflake/snowflake-arctic-instruct": encode_arctic,
    "meta/meta-llama-3-8b": encode_llama3,
    "mistralai/mistral-7b-instruct-v0.2": encode_generic,
}


def generate_stream(
    conversation: Conversation,
):
    messages = conversation.messages
    model_config: ModelConfig = conversation.model_config
    full_model_name = FRIENDLY_MAPPING[model_config.model]

    if model_config.system_prompt:
        system_msg = Message(role="system", content=model_config.system_prompt)
        messages = [system_msg]
        messages.extend(conversation.messages)

    prompt_str = ENCODING_MAPPING[full_model_name](messages)

    model_input = {
        "prompt": prompt_str,
        "prompt_template": r"{prompt}",
        "temperature": model_config.temperature,
        "top_p": model_config.top_p,
    }
    stream = replicate.stream(full_model_name, input=model_input)

    for t in stream:
        yield str(t)

def retrieve_and_generate_stream(
    conversation: Conversation,
):
    messages = conversation.messages
    model_config: ModelConfig = conversation.model_config
    full_model_name = FRIENDLY_MAPPING[model_config.model]

    if model_config.system_prompt:
        system_msg = Message(role="system", content=model_config.system_prompt)
        messages = [system_msg]
        messages.extend(conversation.messages)

    prompt_str = ENCODING_MAPPING[full_model_name](messages)

    nodes = retrieve(query = prompt_str)
    [node.get_content() for node in nodes]

    context_message = "\n\n".join([node.get_content() for node in nodes])

    full_prompt = (
    "We have provided context information below. \n"
    "---------------------\n"
    f"{context_message}"
    "\n---------------------\n"
    f"Given this information, please answer the question: {prompt_str}"
    )

    model_input = {
        "prompt": full_prompt,
        "temperature": model_config.temperature,
        "top_p": model_config.top_p,
    }
    stream = replicate.stream(full_model_name, input=model_input)

    for t in stream:
        yield str(t)