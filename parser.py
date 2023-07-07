from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, validator
#prompt_template = "You are a doctor who is attempting to extract information from the given clinical note.{instruction} USER:  ASSISTANT:"

from llms.wizard13BGPTQ import wizard13bGPTQ
from llms.vicuna13 import Vicuna
from llms.wizardHot import WizardHot
from llms.wizardvicunaHotReg import WizardVicunaHotReg
from llms.openinstruct import OpenInstruct
# pipe = pipeline(
#     "text-generation",
#     model=model,
#     tokenizer=tokenizer,
#     max_new_tokens=1024,
#     temperature=0.4,
#     top_p=0.95,
#     repetition_penalty=1.15
# )
# Define your desired data structure.
class Relapse(BaseModel):
    RelapseDiagnosis: str = Field(description="Describes the Relapse Diagnosis for the patient which can be myelitis, Optical Neuritis (ON), brainstem or none")
    RelapseDate: str = Field(description="Describes what year the patient first diagnosised with the Relapse in multiple schlerosis or none")
    
# You can add custom validation logic easily with Pydantic.
@validator('setup')
def question_ends_with_question_mark(cls, field):
    if field[-1] != '?':
        raise ValueError("Badly formed question!")
    return field

# "From the provided clinical note, extract all instances of relapses, the date of diagnosis of each instance and the context where that can be found"
import re
def outparser(note, question, llm,):
    inst = 'You are a doctor who is attempting to extract information from the given Patient Information.{instruction}'
    prompt_template = llm.getprompt(inst, question)
    # cleaning up the note
    note = note.replace('\n', '').replace('\xa0', '')
    
    # Set up a parser + inject instructions into the prompt template.
    parser = PydanticOutputParser(pydantic_object=Relapse)
    prompt = PromptTemplate(
        template=prompt_template.format(instruction = "{format_instructions} Patient Information: "+str(note)+" {query}"),
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    # And a query intended to prompt a language model to populate the data structure.
    #print(prompt)
    _input = prompt.format_prompt(query=question)
    #print(_input)
    output = llm.generateText(_input.to_string())
    
    #output = re.sub(r"0", "00", output[0]['generated_text'].split('ASSISTANT:')[1])
    output = llm.getResponseOnly(output[0]['generated_text'])
    print(f"outter parser output: {output}")
    return output