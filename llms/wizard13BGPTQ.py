from .baseLLM import LLM

from transformers import AutoTokenizer,pipeline, logging
from auto_gptq import AutoGPTQForCausalLM
from langchain.llms import HuggingFacePipeline

class wizard13bGPTQ(LLM):
    
    name = "wizardLM-13B-1.0-GPTQ"
    model_name_or_path = "TheBloke/wizardLM-13B-1.0-GPTQ"
    model_basename = "WizardLM-13B-1.0-GPTQ-4bit-128g.no-act-order"
    # global model tokenizaer
    model = None
    tokenizer = None
    # pipe line and huggingfacepipeline
    pipeline = None
    hugPipeline = None
    # creating the model and tokenizer elements
    def setupModelAndTokenizer(self):
        print(f'Setting Up {self.name}......')
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path, use_fast=True)

        self.model = AutoGPTQForCausalLM.from_quantized(self.model_name_or_path,
                model_basename=self.model_basename,
                use_safetensors=True,
                trust_remote_code=True,
                device="cuda:0",
                use_triton=False,
                quantize_config=None)
    
    # create a pipeline 
    def createPipe(self,max_length, temperature, top_p, top_k, repetition_penalty):
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=max_length,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,   
        ) 
        
        self.hugPipeline = HuggingFacePipeline(pipeline=self.pipe)
        
    def __init__(self):
        # Prevent printing spurious transformers error when using pipeline with AutoGPTQ
        logging.set_verbosity(logging.CRITICAL)

    # Get the prompt
    def getprompt(self, instruction:str, question:str)-> str:
        return f"{instruction} USER: {question} ASSISTANT:"
    
    # only get the response 
    def getResponseOnly(self,response:str):
        delimiter = "ASSISTANT:"
        response = response.split(delimiter)
        return response[1]


    def generateText(self, promptInput:str):
        return self.pipe(promptInput)
    
    def deleteInstance(self):
        del self.model
        del self.tokenizer
        del self.pipe
        del self.hugPipeline
    