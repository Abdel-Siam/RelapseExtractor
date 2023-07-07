from abc import ABC, abstractmethod
from .exceptions import (
    MethodNotImplementedError,
)

class LLM:
    name: str = ''
    pipe = None
    hugPipeline = None
    
    @abstractmethod
    def setupModelAndTokenizer():
        
        raise MethodNotImplementedError("Call method has not been implemented")
    
    @abstractmethod
    def getprompt(instruction:str, question:str)-> str:
        
        raise MethodNotImplementedError("Call method has not been implemented")
    
    @abstractmethod
    def getResponseOnly(response:str)->str:
        
        raise MethodNotImplementedError("Call method has not been implemented")
    
    @abstractmethod
    def generateText(promptInput:str):
        
        raise MethodNotImplementedError("Call method has not been implemeneted")
    
    @abstractmethod
    def createPipe(max_length, temperature, top_p, top_k, repetition_penalty):
        raise MethodNotImplementedError("Call method has not been implemeneted")
    
    def getPipe(self):
        return self.pipe
    
    def getHugPipe(self):
        return self.hugPipeline
    
    def name(self):
        return self.name