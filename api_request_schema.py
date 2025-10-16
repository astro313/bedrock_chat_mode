api_request_list = {
    # Amazon Titan Models
    'amazon.titan-text-express-v1': {
        "modelId": "amazon.titan-text-express-v1",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "inputText": "",
            "textGenerationConfig": {
                "maxTokenCount": 4096,
                "stopSequences": [],
                "temperature": 0.7,
                "topP": 0.9
            }
        }
    },
    'amazon.titan-text-lite-v1': {
        "modelId": "amazon.titan-text-lite-v1",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "inputText": "",
            "textGenerationConfig": {
                "maxTokenCount": 4096,
                "stopSequences": [],
                "temperature": 0.7,
                "topP": 0.9
            }
        }
    },
    'amazon.titan-text-premier-v1:0': {
        "modelId": "amazon.titan-text-premier-v1:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "inputText": "",
            "textGenerationConfig": {
                "maxTokenCount": 4096,
                "stopSequences": [],
                "temperature": 0.7,
                "topP": 0.9
            }
        }
    },
    
    # Anthropic Claude 4 Models (Messages API)
    'us.anthropic.claude-sonnet-4-20250514-v1:0': {
        "modelId": "us.anthropic.claude-sonnet-4-20250514-v1:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "messages": [],
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
            "anthropic_version": "bedrock-2023-05-31"
        }
    },
    
    # Anthropic Claude 3.5 Models (Messages API)
    'us.anthropic.claude-3-5-sonnet-20241022-v2:0': {
        "modelId": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "messages": [],
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
            "anthropic_version": "bedrock-2023-05-31"
        }
    },
    'us.anthropic.claude-3-5-sonnet-20240620-v1:0': {
        "modelId": "us.anthropic.claude-3-5-sonnet-20240620-v1:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "messages": [],
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
            "anthropic_version": "bedrock-2023-05-31"
        }
    },
    'us.anthropic.claude-3-5-haiku-20241022-v1:0': {
        "modelId": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "messages": [],
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
            "anthropic_version": "bedrock-2023-05-31"
        }
    },
    
    # Anthropic Claude 3 Models (Messages API)
    'anthropic.claude-3-opus-20240229-v1:0': {
        "modelId": "anthropic.claude-3-opus-20240229-v1:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "messages": [],
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
            "anthropic_version": "bedrock-2023-05-31"
        }
    },
    'anthropic.claude-3-sonnet-20240229-v1:0': {
        "modelId": "anthropic.claude-3-sonnet-20240229-v1:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "messages": [],
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
            "anthropic_version": "bedrock-2023-05-31"
        }
    },
    'anthropic.claude-3-haiku-20240307-v1:0': {
        "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "messages": [],
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
            "anthropic_version": "bedrock-2023-05-31"
        }
    },
    
    # Legacy Anthropic Claude Models (Completion API)
    'anthropic.claude-v2:1': {
        "modelId": "anthropic.claude-v2:1",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_tokens_to_sample": 4096,
            "temperature": 0.7,
            "top_k": 250,
            "top_p": 0.9,
            "stop_sequences": ["\n\nHuman:"],
            "anthropic_version": "bedrock-2023-05-31"
        }
    },
    'anthropic.claude-v2': {
        "modelId": "anthropic.claude-v2",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_tokens_to_sample": 4096,
            "temperature": 0.7,
            "top_k": 250,
            "top_p": 0.9,
            "stop_sequences": ["\n\nHuman:"],
            "anthropic_version": "bedrock-2023-05-31"
        }
    },
    'anthropic.claude-instant-v1': {
        "modelId": "anthropic.claude-instant-v1",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_tokens_to_sample": 4096,
            "temperature": 0.7,
            "top_k": 250,
            "top_p": 0.9,
            "stop_sequences": ["\n\nHuman:"],
            "anthropic_version": "bedrock-2023-05-31"
        }
    },
    
    # Meta Llama Models
    'meta.llama3-2-90b-instruct-v1:0': {
        "modelId": "meta.llama3-2-90b-instruct-v1:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_gen_len": 4096,
            "temperature": 0.7,
            "top_p": 0.9
        }
    },
    'meta.llama3-2-11b-instruct-v1:0': {
        "modelId": "meta.llama3-2-11b-instruct-v1:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_gen_len": 4096,
            "temperature": 0.7,
            "top_p": 0.9
        }
    },
    'meta.llama3-2-3b-instruct-v1:0': {
        "modelId": "meta.llama3-2-3b-instruct-v1:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_gen_len": 4096,
            "temperature": 0.7,
            "top_p": 0.9
        }
    },
    'meta.llama3-1-70b-instruct-v1:0': {
        "modelId": "meta.llama3-1-70b-instruct-v1:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_gen_len": 4096,
            "temperature": 0.7,
            "top_p": 0.9
        }
    },
    'meta.llama3-1-8b-instruct-v1:0': {
        "modelId": "meta.llama3-1-8b-instruct-v1:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_gen_len": 4096,
            "temperature": 0.7,
            "top_p": 0.9
        }
    },
    
    # Legacy Meta Llama Models
    'meta.llama2-70b-chat-v1': {
        "modelId": "meta.llama2-70b-chat-v1",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_gen_len": 4096,
            "temperature": 0.7,
            "top_p": 0.9
        }
    },
    'meta.llama2-13b-chat-v1': {
        "modelId": "meta.llama2-13b-chat-v1",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_gen_len": 4096,
            "temperature": 0.7,
            "top_p": 0.9
        }
    },
    
    # Cohere Models
    'cohere.command-r-plus-v1:0': {
        "modelId": "cohere.command-r-plus-v1:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "message": "",
            "max_tokens": 4096,
            "temperature": 0.7,
            "p": 0.9
        }
    },
    'cohere.command-r-v1:0': {
        "modelId": "cohere.command-r-v1:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "message": "",
            "max_tokens": 4096,
            "temperature": 0.7,
            "p": 0.9
        }
    },
    
    # Legacy Cohere Models
    'cohere.command-text-v14': {
        "modelId": "cohere.command-text-v14",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_tokens": 4096,
            "temperature": 0.7,
        }
    },
    'cohere.command-light-text-v14': {
        "modelId": "cohere.command-light-text-v14",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_tokens": 4096,
            "temperature": 0.7,
        }
    },
}


def get_model_ids():
    return list(api_request_list.keys())
