import asyncio
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import boto3
import pyaudio
import sounddevice
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent, TranscriptResultStream

from api_request_schema import api_request_list, get_model_ids

model_id = os.getenv('MODEL_ID', 'us.anthropic.claude-sonnet-4-20250514-v1:0')
aws_region = os.getenv('AWS_REGION', 'us-east-1')

if model_id not in get_model_ids():
    print(f'Error: Models ID {model_id} in not a valid model ID. Set MODEL_ID env var to one of {get_model_ids()}.')
    sys.exit(0)

api_request = api_request_list[model_id]
config = {
    'log_level': 'none',  # Back to none - no debug info needed
    'last_speech': "If you have any other questions, please don't hesitate to ask. Have a great day!",
    'region': aws_region,
    'polly': {
        'Engine': 'neural',
        'LanguageCode': 'en-US',
        'VoiceId': 'Joanna',
        'OutputFormat': 'pcm',
        'SpeechMarkTypes': [],
        'SampleRate': '16000',
        'SpeechRate': '1.75'  
    },
    'translate': {
        'SourceLanguageCode': 'en',
        'TargetLanguageCode': 'en',
    },
    'bedrock': {
        'response_streaming': True,
        'api_request': api_request
    }
}


p = pyaudio.PyAudio()
bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name=config['region'])
polly = boto3.client('polly', region_name=config['region'])
transcribe_streaming = TranscribeStreamingClient(region=config['region'])


def printer(text, level):
    if config['log_level'] == 'info' and level == 'info':
        print(text)
    elif config['log_level'] == 'debug' and level in ['info', 'debug']:
        print(text)


class UserInputManager:
    shutdown_executor = False
    executor = None

    @staticmethod
    def set_executor(executor):
        UserInputManager.executor = executor

    @staticmethod
    def start_shutdown_executor():
        UserInputManager.shutdown_executor = False
        raise Exception()  # Workaround to shutdown exec, as executor.shutdown() doesn't work as expected.

    @staticmethod
    def start_user_input_loop():
        while True:
            sys.stdin.readline().strip()
            printer(f'[DEBUG] User input to shut down executor...', 'debug')
            UserInputManager.shutdown_executor = True

    @staticmethod
    def is_executor_set():
        return UserInputManager.executor is not None

    @staticmethod
    def is_shutdown_scheduled():
        return UserInputManager.shutdown_executor


class BedrockModelsWrapper:

    @staticmethod
    def define_body(text):
        model_id = config['bedrock']['api_request']['modelId']
        body = config['bedrock']['api_request']['body'].copy()
        
        # Conversational instruction for natural dialogue
        conversation_prompt = "You are having a friendly, natural conversation. Respond as you would in a real-time voice chat - be conversational, engaging, and avoid bullet points or lists. Keep responses concise but natural, as if you're talking to a friend."
        
        # Handle different model providers and API formats
        if model_id.startswith('amazon.titan'):
            body['inputText'] = f"{conversation_prompt}\n\nHuman: {text}"
        elif model_id.startswith('meta.llama'):
            body['prompt'] = f"<|system|>\n{conversation_prompt}\n<|user|>\n{text}\n<|assistant|>\n"
        elif model_id.startswith('cohere.command-r'):
            body['message'] = text
            body['preamble'] = conversation_prompt
        elif model_id.startswith('cohere.'):
            body['prompt'] = f"{conversation_prompt}\n\nUser: {text}\nAssistant:"
        elif 'anthropic' in model_id:
            # Check if this is a modern Claude model using Messages API
            if 'claude-3' in model_id or 'claude-sonnet-4' in model_id or 'claude-4' in model_id:
                # Modern Messages API with system message
                body['system'] = conversation_prompt
                body['messages'] = [{"role": "user", "content": text}]
            else:
                # Legacy Completion API
                body['prompt'] = f'\n\nHuman: {conversation_prompt}\n\nUser: {text}\n\nAssistant:'
        else:
            raise Exception(f'Unknown model: {model_id}')

        return body

    @staticmethod
    def get_stream_chunk(event):
        return event.get('chunk')

    @staticmethod
    def get_stream_text(chunk):
        model_id = config['bedrock']['api_request']['modelId']
        
        chunk_obj = json.loads(chunk.get('bytes').decode())
        text = ''
        
        # Handle different model response formats
        if model_id.startswith('amazon.titan'):
            text = chunk_obj.get('outputText', '')
        elif model_id.startswith('meta.llama'):
            text = chunk_obj.get('generation', '')
        elif model_id.startswith('cohere.command-r'):
            # Modern Cohere Command R models
            if 'text' in chunk_obj:
                text = chunk_obj['text']
            elif 'delta' in chunk_obj:
                text = chunk_obj['delta'].get('message', {}).get('content', {}).get('text', '')
        elif model_id.startswith('cohere.'):
            # Legacy Cohere models
            if 'generations' in chunk_obj:
                text = ' '.join([c.get("text", "") for c in chunk_obj['generations']])
            else:
                text = chunk_obj.get('text', '')
        elif 'anthropic' in model_id:
            # Check if this is a modern Claude model using Messages API
            if 'claude-3' in model_id or 'claude-sonnet-4' in model_id or 'claude-4' in model_id:
                # Modern Messages API streaming format
                if 'delta' in chunk_obj:
                    delta = chunk_obj['delta']
                    if 'text' in delta:
                        text = delta['text']
                    elif 'content_block' in delta and 'text' in delta['content_block']:
                        text = delta['content_block']['text']
                elif 'message' in chunk_obj and 'content' in chunk_obj['message']:
                    # Non-streaming Messages API format
                    content = chunk_obj['message']['content']
                    if isinstance(content, list) and len(content) > 0:
                        text = content[0].get('text', '')
                    elif isinstance(content, str):
                        text = content
            else:
                # Legacy Completion API
                text = chunk_obj.get('completion', '')
        else:
            raise NotImplementedError(f'Unknown model: {model_id}')

        printer(f'[DEBUG] Chunk object: {chunk_obj}', 'debug')
        return text


def to_audio_generator(bedrock_stream):
    prefix = ''

    if bedrock_stream:
        for event in bedrock_stream:
            chunk = BedrockModelsWrapper.get_stream_chunk(event)
            if chunk:
                text = BedrockModelsWrapper.get_stream_text(chunk)

                if '.' in text:
                    a = text.split('.')[:-1]
                    to_polly = ''.join([prefix, '.'.join(a), '. '])
                    prefix = text.split('.')[-1]
                    print(to_polly, flush=True, end='')
                    yield to_polly
                else:
                    prefix = ''.join([prefix, text])

        if prefix != '':
            print(prefix, flush=True, end='')
            yield f'{prefix}.'

        print('\n')


class BedrockWrapper:

    def __init__(self):
        self.speaking = False

    def is_speaking(self):
        return self.speaking

    def invoke_bedrock(self, text):
        printer('[DEBUG] Bedrock generation started', 'debug')
        self.speaking = True

        body = BedrockModelsWrapper.define_body(text)
        printer(f"[DEBUG] Request body: {body}", 'debug')

        try:
            body_json = json.dumps(body)
            response = bedrock_runtime.invoke_model_with_response_stream(
                body=body_json,
                modelId=config['bedrock']['api_request']['modelId'],
                accept=config['bedrock']['api_request']['accept'],
                contentType=config['bedrock']['api_request']['contentType']
            )

            printer('[DEBUG] Capturing Bedrocks response/bedrock_stream', 'debug')
            bedrock_stream = response.get('body')

            audio_gen = to_audio_generator(bedrock_stream)
            printer('[DEBUG] Created bedrock stream to audio generator', 'debug')

            reader = Reader()
            for audio in audio_gen:
                reader.read(audio)

            reader.close()

        except Exception as e:
            print(e)
            time.sleep(2)
            self.speaking = False

        time.sleep(1)
        self.speaking = False
        printer('\n[DEBUG] Bedrock generation completed', 'debug')


class Reader:

    def __init__(self):
        self.polly = boto3.client('polly', region_name=config['region'])
        self.audio = p.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)
        self.chunk = 1024

    def read(self, data):
        # Wrap text in SSML to control speech rate (1.5x speed)
        ssml_text = f'<speak><prosody rate="150%">{data}</prosody></speak>'
        
        response = self.polly.synthesize_speech(
            Text=ssml_text,
            TextType='ssml',
            Engine=config['polly']['Engine'],
            LanguageCode=config['polly']['LanguageCode'],
            VoiceId=config['polly']['VoiceId'],
            OutputFormat=config['polly']['OutputFormat'],
        )

        stream = response['AudioStream']

        while True:
            # Check if user signaled to shutdown Bedrock speech
            # UserInputManager.start_shutdown_executor() will raise Exception. If not ideas but is functional.
            if UserInputManager.is_executor_set() and UserInputManager.is_shutdown_scheduled():
                UserInputManager.start_shutdown_executor()

            data = stream.read(self.chunk)
            self.audio.write(data)
            if not data:
                break

    def close(self):
        time.sleep(1)
        self.audio.stop_stream()
        self.audio.close()


def stream_data(stream):
    chunk = 1024
    if stream:
        polly_stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            output=True,
        )

        while True:
            data = stream.read(chunk)
            polly_stream.write(data)

            # If there's no more data to read, stop streaming
            if not data:
                time.sleep(0.5)
                stream.close()
                polly_stream.stop_stream()
                polly_stream.close()
                break
    else:
        # The stream passed in is empty
        pass


def aws_polly_tts(polly_text):
    printer(f'[INTO] Character count: {len(polly_text)}', 'debug')
    byte_stream_list = []
    polly_text_len = len(polly_text.split('.'))
    printer(f'LEN polly_text_len: {polly_text_len}', 'debug')
    for i in range(0, polly_text_len, 20):
        printer(f'{i}:{i + 20}', 'debug')
        polly_text_chunk = '. '.join(polly_text.split('. ')[i:i + 20])
        printer(f'polly_text_chunk LEN: {len(polly_text_chunk)}', 'debug')

        response = polly.synthesize_speech(
            Text=polly_text_chunk,
            Engine=config['polly']['Engine'],
            LanguageCode=config['polly']['LanguageCode'],
            VoiceId=config['polly']['VoiceId'],
            OutputFormat=config['polly']['OutputFormat'],
        )
        byte_stream = response['AudioStream']
        byte_stream_list.append(byte_stream)

    byte_chunks = []
    chunk = 1024
    for bs in byte_stream_list:
        while True:
            data = bs.read(chunk)
            byte_chunks.append(data)

            if not data:
                bs.close()
                break

    read_byte_chunks(b''.join(byte_chunks))


def read_byte_chunks(data):
    polly_stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)
    polly_stream.write(data)

    time.sleep(1)
    polly_stream.stop_stream()
    polly_stream.close()
    time.sleep(1)


class EventHandler(TranscriptResultStreamHandler):
    text = []
    last_time = 0
    sample_count = 0
    max_sample_counter = 4

    def __init__(self, transcript_result_stream: TranscriptResultStream, bedrock_wrapper):
        super().__init__(transcript_result_stream)
        self.bedrock_wrapper = bedrock_wrapper

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        printer(f'[INFO] Received transcript event. Results: {len(results) if results else 0}', 'info')
        
        if not self.bedrock_wrapper.is_speaking():

            if results:
                for result in results:
                    EventHandler.sample_count = 0
                    if not result.is_partial:
                        for alt in result.alternatives:
                            printer(f'[INFO] Transcribed: {alt.transcript}', 'info')
                            print(alt.transcript, flush=True, end=' ')
                            EventHandler.text.append(alt.transcript)

            else:
                EventHandler.sample_count += 1
                printer(f'[INFO] Empty transcript result #{EventHandler.sample_count}', 'info')
                if EventHandler.sample_count == EventHandler.max_sample_counter:

                    if len(EventHandler.text) == 0:
                        printer('[INFO] No speech detected after timeout, exiting...', 'info')
                        last_speech = config['last_speech']
                        print(last_speech, flush=True)
                        aws_polly_tts(last_speech)
                        os._exit(0)  # exit from a child process
                    else:
                        input_text = ' '.join(EventHandler.text)
                        printer(f'\n[INFO] User input: {input_text}', 'info')

                        executor = ThreadPoolExecutor(max_workers=1)
                        # Add executor so Bedrock execution can be shut down, if user input signals so.
                        UserInputManager.set_executor(executor)
                        # Use asyncio.get_running_loop() instead of loop variable
                        asyncio.get_running_loop().run_in_executor(
                            executor,
                            self.bedrock_wrapper.invoke_bedrock,
                            input_text
                        )

                    EventHandler.text.clear()
                    EventHandler.sample_count = 0


class MicStream:

    async def mic_stream(self):
        loop = asyncio.get_running_loop()
        input_queue = asyncio.Queue()

        def callback(indata, frame_count, time_info, status):
            printer(f'[INFO] Audio callback received {len(indata)} bytes, status: {status}', 'info')
            loop.call_soon_threadsafe(input_queue.put_nowait, (bytes(indata), status))

        printer('[INFO] Starting microphone stream...', 'info')
        stream = sounddevice.RawInputStream(
            channels=1, samplerate=16000, callback=callback, blocksize=2048 * 2, dtype="int16")
        with stream:
            while True:
                indata, status = await input_queue.get()
                yield indata, status

    async def write_chunks(self, stream):
        printer('[INFO] Starting to write audio chunks to Transcribe...', 'info')
        async for chunk, status in self.mic_stream():
            try:
                await stream.input_stream.send_audio_event(audio_chunk=chunk)
            except Exception as e:
                printer(f'[INFO] Error sending audio chunk: {e}', 'info')
                raise

        await stream.input_stream.end_stream()

    async def basic_transcribe(self):
        loop = asyncio.get_running_loop()
        loop.run_in_executor(ThreadPoolExecutor(max_workers=1), UserInputManager.start_user_input_loop)

        printer('[INFO] Connecting to Amazon Transcribe...', 'info')
        try:
            stream = await transcribe_streaming.start_stream_transcription(
                language_code="en-US",
                media_sample_rate_hz=16000,
                media_encoding="pcm",
            )
            printer('[INFO] Successfully connected to Amazon Transcribe', 'info')
        except Exception as e:
            printer(f'[INFO] Failed to connect to Transcribe: {e}', 'info')
            raise

        handler = EventHandler(stream.output_stream, BedrockWrapper())
        await asyncio.gather(self.write_chunks(stream), handler.handle_events())


info_text = f'''
*************************************************************
[INFO] Supported FM models: {get_model_ids()}.
[INFO] Change FM model by setting <MODEL_ID> environment variable. Example: export MODEL_ID=meta.llama2-70b-chat-v1

[INFO] AWS Region: {config['region']}
[INFO] Amazon Bedrock model: {config['bedrock']['api_request']['modelId']}
[INFO] Polly config: engine {config['polly']['Engine']}, voice {config['polly']['VoiceId']}
[INFO] Log level: {config['log_level']}

[INFO] Hit ENTER to interrupt Amazon Bedrock. After you can continue speaking!
[INFO] Go ahead with the voice chat with Amazon Bedrock!
*************************************************************
'''
print(info_text)

# Fixed asyncio deprecation warning by using asyncio.run()
try:
    asyncio.run(MicStream().basic_transcribe())
except (KeyboardInterrupt, Exception) as e:
    print()
