from dash import Dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import dash
import json

import re

from llms.wizard13BGPTQ import wizard13bGPTQ
from llms.wizardvicuna13 import WizardVicuna
from llms.wizardMega import WizardMega
from llms.vicuna13 import Vicuna
from llms.wizardHot import WizardHot
from llms.noushermes import NousHermes
from llms.wizardvicunaHot13 import WizardVicunaHot
from llms.chronosHot import ChronosHot
from llms.samanthaHot import SamanthaHot
from llms.guanacoHot import GuanacoHot
from llms.gpt4all import Gpt4All
from llms.wizardvicunaHotReg import WizardVicunaHotReg
from llms.vicuna13Hot import VicunaHot
from llms.openinstruct import OpenInstruct
from llms.koalaHot13b import Koala
from llms.orcaMiniv27B import OrcaMini
from llms.camel13bHot import CAMEL13BHot
from llms.wizard30B import wizard30bGPTQ

class_dict = {'Wizard13B': wizard13bGPTQ(),
              'Wizard30B': wizard30bGPTQ(),
              'KoalaHot13B':Koala(),
              'OrcaMiniv2':OrcaMini(),
              'WizardVicuna13': WizardVicuna(),
              'WizardMega': WizardMega(),
              'Vicuna13': Vicuna(),
              'WizardHot': WizardHot(),
              'CAMEL13BHot': CAMEL13BHot(),
              'NousHermes': NousHermes(),
              'WizardVicunaHot13': WizardVicunaHot(),
              'ChronosHot': ChronosHot(),
              'SamanthaHot': SamanthaHot(),
              'GuanacoHot': GuanacoHot(),
              'Gpt4All': Gpt4All(),
              'WizardVicunaHotReg': WizardVicunaHotReg(),
              'Vicuna13Hot': VicunaHot(),
              'OpenInstruct': OpenInstruct()}

class_names = list(class_dict.keys())
class_names.append('None')

app = Dash(__name__, external_stylesheets=['./assets/custom.css', dbc.themes.BOOTSTRAP])
# Modals
newNoteModal = dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Add New Note:")),
                dbc.ModalBody([
                    dcc.Textarea(id="newClinNote", className="newClinNote", style={"width":"100%",'height':'600px'})
                    ]),
                dbc.ModalFooter([
                    dbc.Button("Submit", id="SubmitNewNote", className="ms-auto", n_clicks=0, style={'align':'start'}),
                    dbc.Button("Close", id="CloseModal", className="ms-auto", n_clicks=0)]
                ),
            ],
            id="AddNote",
            is_open=False,
            size="xl",
        )
optionsModal = dbc.Modal(
            [
                dbc.ModalHeader([dbc.ModalTitle("Options Modal"),
                                 dcc.Dropdown(
                                    id='configdropdown',
                                    options=[],
                                    placeholder='Select a prompt...'
                                    ),]),
                dbc.ModalBody(dbc.Row([
                    dbc.Col([
                        html.H3("Model 1", style={'color':'#000000'}),
                        dcc.Dropdown(
                            id='model1-dropdown',
                            options=[{'label': name, 'value': name} for name in class_names],
                            placeholder='Select a class...'
                            ),
                        html.Div([
                            html.H5('Generation Length: ', style={'color':'#000000'}),
                            dcc.Slider(
                                id='Generation-slider1',
                                min=256,
                                max=2048,
                                step=256,
                                value=512,
                                marks={i: str(i) for i in range(0, 11)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),
                            html.Div('Controls the generation amount for the models output.')
                        ]),
                        html.Div([
                            html.H5('Temperature', style={'color':'#000000'}),
                            dcc.Slider(
                                id='temperature-slider1',
                                min=0,
                                max=1,
                                step=0.05,
                                value=0.7,
                                marks={i: str(i) for i in range(0, 11)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),
                            html.Div('Controls the randomness of the generated text. Higher values (e.g., 1.0) make the output more diverse, while lower values (e.g., 0.2) make it more focused and deterministic.')
                        ]),
                        html.Div([
                            html.H5('Top_p', style={'color':'#000000'}),
                            dcc.Slider(
                                id='top-p-slider1',
                                min=0,
                                max=1,
                                step=0.01,
                                value=0.9,
                                marks={i: str(i) for i in range(0, 11)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),
                            html.Div('Determines the cumulative probability threshold for generating the next word. Higher values (e.g., 0.8) result in more diverse outputs, while lower values (e.g., 0.2) make the output more focused and deterministic.')
                        ]),
                        html.Div([
                            html.H5('Top_k', style={'color':'#000000'}),
                            dcc.Slider(
                                id='top-k-slider1',
                                min=0,
                                max=50,
                                step=5,
                                value=20,
                                marks={i: str(i) for i in range(0, 51, 10)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),
                            html.Div('Limits the number of choices considered for each token during text generation. Higher values (e.g., 50) allow for more diversity, while lower values (e.g., 10) make the output more focused and deterministic.')
                        ]),
                        html.Div([
                            html.H5('Repetition Penalty', style={'color':'#000000'}),
                            dcc.Slider(
                                id='repetition-penalty-slider1',
                                min=1,
                                max=2,
                                step=0.01,
                                value=1.15,
                                marks={i: str(i) for i in range(1, 21, 2)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),
                            html.Div('Controls the penalty applied to repeated words in the generated text. Higher values (e.g., 1.5) reduce the likelihood of repetitive phrases, while lower values (e.g., 1.0) allow more repetitions.')
                        ]),
                    ], width=4),
                    dbc.Col([
                        html.H3("Model 2", style={'color':'#000000'}),
                        dcc.Dropdown(
                            id='model2-dropdown',
                            options=[{'label': name, 'value': name} for name in class_names],
                            placeholder='Select a class...'
                            ),
                        html.Div([
                            html.H5('Generation Length: ', style={'color':'#000000'}),
                            dcc.Slider(
                                id='Generation-slider2',
                                min=256,
                                max=2048,
                                step=256,
                                value=512,
                                marks={i: str(i) for i in range(0, 11)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),
                            html.Div('Controls the generation amount for the models output.')
                        ]),
                        html.Div([
                            html.H5('Temperature', style={'color':'#000000'}),
                            dcc.Slider(
                                id='temperature-slider2',
                                min=0,
                                max=1,
                                step=0.05,
                                value=0.7,
                                marks={i: str(i) for i in range(0, 11)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),
                            html.Div('Controls the randomness of the generated text. Higher values (e.g., 1.0) make the output more diverse, while lower values (e.g., 0.2) make it more focused and deterministic.')
                        ]),
                        html.Div([
                            html.H5('Top_p', style={'color':'#000000'}),
                            dcc.Slider(
                                id='top-p-slider2',
                                min=0,
                                max=1,
                                step=0.01,
                                value=0.9,
                                marks={i: str(i) for i in range(0, 11)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),
                            html.Div('Determines the cumulative probability threshold for generating the next word. Higher values (e.g., 0.8) result in more diverse outputs, while lower values (e.g., 0.2) make the output more focused and deterministic.')
                        ]),
                        html.Div([
                            html.H5('Top_k', style={'color':'#000000'}),
                            dcc.Slider(
                                id='top-k-slider2',
                                min=0,
                                max=50,
                                step=5,
                                value=20,
                                marks={i: str(i) for i in range(0, 51, 10)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),
                            html.Div('Limits the number of choices considered for each token during text generation. Higher values (e.g., 50) allow for more diversity, while lower values (e.g., 10) make the output more focused and deterministic.')
                        ]),
                        html.Div([
                            html.H5('Repetition Penalty'),
                            dcc.Slider(
                                id='repetition-penalty-slider2',
                                min=1,
                                max=2,
                                step=0.01,
                                value=1.15,
                                marks={i: str(i) for i in range(1, 21, 2)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),
                            html.Div('Controls the penalty applied to repeated words in the generated text. Higher values (e.g., 1.5) reduce the likelihood of repetitive phrases, while lower values (e.g., 1.0) allow more repetitions.')
                            ]),
                        ], width=4),
                    dbc.Col([
                        html.H3("Parser", style={'color':'#000000'}),
                        dcc.Dropdown(
                            id='model3-dropdown',
                            options=[{'label': name, 'value': name} for name in class_names],
                            placeholder='OrcaMiniv2',
                            value='OrcaMiniv2'
                            ),
                        html.Div([
                            html.H5('Generation Length: ', style={'color':'#000000'}),
                            dcc.Slider(
                                id='Generation-slider3',
                                min=256,
                                max=2048,
                                step=256,
                                value=1024,
                                marks={i: str(i) for i in range(0, 11)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),
                            html.Div('Controls the generation amount for the models output.')
                        ]),
                        html.Div([
                            html.H5('Temperature', style={'color':'#000000'}),
                            dcc.Slider(
                                id='temperature-slider3',
                                min=0,
                                max=1,
                                step=0.05,
                                value=0.7,
                                marks={i: str(i) for i in range(0, 11)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),
                            html.Div('Controls the randomness of the generated text. Higher values (e.g., 1.0) make the output more diverse, while lower values (e.g., 0.2) make it more focused and deterministic.')
                        ]),
                        html.Div([
                            html.H5('Top_p', style={'color':'#000000'}),
                            dcc.Slider(
                                id='top-p-slider3',
                                min=0,
                                max=1,
                                step=0.01,
                                value=0.9,
                                marks={i: str(i) for i in range(0, 11)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),
                            html.Div('Determines the cumulative probability threshold for generating the next word. Higher values (e.g., 0.8) result in more diverse outputs, while lower values (e.g., 0.2) make the output more focused and deterministic.')
                        ]),
                        html.Div([
                            html.H5('Top_k', style={'color':'#000000'}),
                            dcc.Slider(
                                id='top-k-slider3',
                                min=0,
                                max=50,
                                step=5,
                                value=20,
                                marks={i: str(i) for i in range(0, 51, 10)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),
                            html.Div('Limits the number of choices considered for each token during text generation. Higher values (e.g., 50) allow for more diversity, while lower values (e.g., 10) make the output more focused and deterministic.')
                        ]),
                        html.Div([
                            html.H5('Repetition Penalty', style={'color':'#000000'}),
                            dcc.Slider(
                                id='repetition-penalty-slider3',
                                min=1,
                                max=2,
                                step=0.01,
                                value=1.15,
                                marks={i: str(i) for i in range(1, 21, 2)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),
                            html.Div('Controls the penalty applied to repeated words in the generated text. Higher values (e.g., 1.5) reduce the likelihood of repetitive phrases, while lower values (e.g., 1.0) allow more repetitions.')
                            ]),
                        ], width=4),
                    dbc.Col([
                        html.H3("Prompting", style={'color':'#000000'}),
                        html.H5('Model 1 Prompt: ', style={'color':'#000000'}),
                        dbc.Textarea(id="promptModel1", value="You are doctor that is attempting to read the clinical note to extract all types of Relapses that the patient was diagnosed with and the year that each diagnosis was given. You know that a patient may or may not have a relapse in their multiple sclerosis and that a relapse in multiple sclerosis could be one of the following types: Transverse myelitis (myelitis) or optic neuritis (ON) or brain stem. If they are mentioned then the patient experienced a relapse. Use this information to concisely extract that information from the clinical note that the user provides into bullet points that start with `-` of the relapse type with the date that it was diagnosed in. Remember that a clinical note may or may not state that there was a relapse. You are not diagnosing the patient just extracting the information present.", style={'height':'10vh'}),
                        html.H5('Model 2 Prompt: ', style={'color':'#000000'}),
                        dbc.Textarea(id="promptModel2", value="You are doctor that is attempting to read the clinical note to extract all types of Relapses that the patient was diagnosed with and the year that each diagnosis was given. You know that a patient may or may not have a relapse in their multiple sclerosis and that a relapse in multiple sclerosis could be one of the following types: Transverse myelitis (myelitis) or optic neuritis (ON) or brain stem. If they are mentioned then the patient experienced a relapse. Use this information to concisely extract that information from the clinical note that the user provides into bullet points that start with `-` of the relapse type with the date that it was diagnosed in. Remember that a clinical note may or may not state that there was a relapse. You are not diagnosing the patient just extracting the information present.", style={'height':'10vh'}),
                        html.H5('Outer Parser Prompting: ', style={'color':'#000000'}),
                        dbc.Textarea(id="promptModel3", value="From the provided clinical note, extract all episodes of relapses and the date of diagnosis of each instance", style={'height':'10vh'}),
                        ], width=12),
                    ]), style={'overflow':'auto', 'max-height':'80vh'}),
                dbc.ModalFooter([
                    dbc.Button("Close", id="CloseModal2", className="ms-auto", n_clicks=0)]),
            ],
            id="OptionsModal",
            is_open=False,
            size="xl",
        )
# main Dashboard
app.layout = dbc.Container([
        dbc.Row(html.H1("Relapse Extractor"), style={"margin-bottom":"25px"}),
        dbc.Row([
                dbc.Col([
                    html.Div(id = 'NotesDiv', className="NotesDiv")
                ], width=4),
                dbc.Col([
                    dbc.Row(html.Button("+", id="add-button", n_clicks=0), style={'margin-bottom': '10px', 'height':'5vh'}),
                    dbc.Row(html.Button("-", id="remove-button", n_clicks=0), style={'margin-bottom': '10px', 'height':'5vh'}),
                    dbc.Row(html.Button("Options", id="options-button", n_clicks=0), style={'margin-bottom': '10px', 'height':'5vh'}),
                    dbc.Row(html.Button("Start", id="start-button", n_clicks=0), style={'margin-bottom': '10px', 'height':'5vh'})
                ], width=1, className='ButtonsCol'),
                dbc.Col([
                    html.Div(id = 'viewDiv', className="viewDiv")
                ])
            ], style={'height':'45vh'}),
        dbc.Row(html.H2("Output:")),
        dbc.Row([
            dbc.Col(html.H4("model 1 Output: "), width=3),
            dbc.Col(html.H4("model 2 Output: "), width=3),
            dbc.Col(html.H4("Parser Output:"), width=3),
            dbc.Col(html.H4(""), width=3),
        ], style={'height':'5vh'}),
        dcc.Loading(dbc.Row([
            dbc.Col(html.Div(id = 'Model1', className="Model1"), width=3),
            dbc.Col(html.Div(id = 'Model2', className="Model2"), width=3),
            dbc.Col(html.Div(id = 'CombinedOutput', className="CombinedOutput"), width=3),
            dbc.Col(html.Div(id = 'CompleteOuput', className="CompleteOuput"), width=3),
        ], style={'max-height':'30vh', 'min-height':'30vh'})),
        newNoteModal,
        optionsModal,
    ],
    style={"width": "90%", "margin": "auto"},
)
# show clicked on notes
@app.callback(
    Output("viewDiv", "children"),
    [Input({'type': 'note', 'index': ALL}, 'n_clicks'),
     Input({'type': 'output', 'index': ALL}, 'n_clicks'),
     Input({'type': 'output2', 'index': ALL}, 'n_clicks'),
     Input({'type': 'output3', 'index': ALL}, 'n_clicks')],
    [State({'type': 'note', 'index': ALL}, 'children'),
     State({'type': 'output', 'index': ALL}, 'children'),
     State({'type': 'output2', 'index': ALL}, 'children'),
     State({'type': 'output3', 'index': ALL}, 'children')]
)
def show_full_note_on_click(n, n2, n3, n4, children, children2, children3, children4):
    ctx = dash.callback_context
    #print(ctx.triggered[0]['prop_id'])
    #print(children)
    #print(children2)
    #print(f"trigger: {ctx.triggered}")
    
    if not ctx.triggered:
        return dash.no_update
    else:
        trigger = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])

        if trigger['type'] == 'note':
            index = trigger['index']
            note_children = children[index][1]
            if isinstance(note_children, dict):
                return note_children['props']['children']
            else:
                return note_children.children
        elif trigger['type'] == 'output':
            index = trigger['index']
            
            note_children = children2[index][1]
            #print(f"note children: {note_children}")
            return dcc.Markdown(note_children['props']['children'])
        elif trigger['type'] == 'output2':
            index = trigger['index']
            
            note_children = children3[index][1]
            #print(f"note children: {note_children}")
            return dcc.Markdown(note_children['props']['children'])
        elif trigger['type'] == 'output3':
            index = trigger['index']
            
            note_children = children4[index][1]
            #print(f"note children: {note_children}")
            return dcc.Markdown(note_children['props']['children'])
        else:
            return dash.no_update
            
# adding a new note to the list of notes
@app.callback(
    [Output("NotesDiv", "children"),
     Output("newClinNote", "value"),],
    [Input("SubmitNewNote", "n_clicks")],
    [State('newClinNote', 'value'),
     State("NotesDiv", "children")],
    prevent_initial_call=True
)
def addNewNote(n_clicks, newNote, oldNotes):
    if oldNotes == None:
        newCard = html.Div([
            html.H5('Note Number: 0'),
            html.H5(str(newNote), id={'type': 'individualnotes', 'index': 0})], className='notes', id={'type': 'note', 'index': 0})
        return [newCard], ""
    
    newCard = html.Div([
        html.H5('Note Number: '+str(len(oldNotes))),
        html.H5(str(newNote),id={'type': 'individualnotes', 'index': len(oldNotes)})], className='notes', id={'type': 'note', 'index': len(oldNotes)})
    return oldNotes + [newCard], ""

# toggling add note modal on and off 
@app.callback(
    Output("AddNote", "is_open"),
    [Input("add-button", "n_clicks"), Input("CloseModal", "n_clicks"), Input('SubmitNewNote', 'n_clicks')],
    [State("AddNote", "is_open")],
)
def toggle_modal(n1, n2, n_click, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# toggling options modal on and off
@app.callback(
    Output("OptionsModal", "is_open"),
    [Input("options-button", "n_clicks"), Input("CloseModal2", "n_clicks")],
    [State("OptionsModal", "is_open")],
)
def toggle_OptionsModal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# removing the last note from the list of notes
@app.callback(
    Output("NotesDiv", "children", allow_duplicate=True),
    [Input("remove-button", "n_clicks")],
    [State("NotesDiv", "children")],
    prevent_initial_call=True
)
def removeLastNote(n_clicks, oldNotes):
    if oldNotes is None or len(oldNotes) == 0:
        return dash.no_update

    if n_clicks is None or n_clicks <= 0:
        return dash.no_update

    # Remove the last note from the list of notes
    updatedNotes = oldNotes[:-1]
    return updatedNotes


from parser import outparser

def format_string(input_string):
    output_string = ""
    for word in input_string.split():
        if word.isdigit() and len(word) == 3 and '0' in word:
            output_string += word.replace('0', '00') + ' '
        else:
            output_string += word + ' '
    return output_string.strip()


#Function for running the main notes
@app.callback(
    [Output("Model1", "children"),
     Output("Model2", "children"),
     Output("CombinedOutput", "children"),
     Output("CompleteOuput", "children")],
    [Input("start-button", "n_clicks")],
    [State("model1-dropdown", "value"),
     State("model2-dropdown", "value"),
     State("model3-dropdown", "value"),
     State({'type': 'individualnotes', 'index': ALL}, 'children'),
     
     State('Generation-slider1', 'value'),     
     State('temperature-slider1', 'value'),
     State('top-p-slider1', 'value'),
     State('top-k-slider1', 'value'),
     State('repetition-penalty-slider1', 'value'),   
       
     State('Generation-slider2', 'value'),    
     State('temperature-slider2', 'value'),
     State('top-p-slider2', 'value'),
     State('top-k-slider2', 'value'),
     State('repetition-penalty-slider2', 'value'),     
     
     State('Generation-slider3', 'value'),    
     State('temperature-slider3', 'value'),
     State('top-p-slider3', 'value'),
     State('top-k-slider3', 'value'),
     State('repetition-penalty-slider3', 'value'),
     
     State('promptModel1', 'value'),
     State('promptModel2', 'value'),
     State('promptModel3', 'value'),],
    prevent_initial_call=True
)
def aiExtractor(n_clicks, model1Name, model2Name, model3Name, notes, model1Generation, model1Temp, model1topP, model1topK, mode1RepetitionPen, model2Generation, model2Temp, model2topP, model2topK, mode2RepetitionPen, model3Generation, model3Temp, model3topP, model3topK, mode3RepetitionPen, model1prompt, model2prompt, model3prompt):
    model1Output = []
    model2Output = []
    outerparserOutput = []
    completeoutput = ''
    
    llm1TextOnly = []    
    llm2TextOnly = []
    # due to the structure notes are found in [i][1]['props']['children']
    print(notes)
    for i in range(len(notes)):
        notes[i] = notes[i].replace("\n", "").replace('\xa0', ' ').strip()
    # if both models are picked as non then we will only update the parser
    if (model1Name == 'None' and model2Name == 'None') or (model1Name == None and model2Name == None):
        print('Parsing Only..... ')
        # parse the notes with the question
        llm3 = class_dict[model3Name]
        llm3.setupModelAndTokenizer()
        llm3.createPipe(temperature= model3Temp, max_length=model3Generation, top_p=model3topP, top_k=model3topK, repetition_penalty=mode3RepetitionPen)
        outerparserOutput = outparser(notes=notes, question=model3prompt, llm=llm3)
        llm3.deleteInstance()
        del llm3
        
        FinalouterparserOutput = []
        #change everything to an html.p
        for i in range(len(outerparserOutput)):
            FinalouterparserOutput.append(html.Div([html.H5(f"Note - {i} output"), dcc.Markdown(outerparserOutput[i], className='Outputs')], id={'type': 'output', 'index': i}))
            
        #print(outerparserOutput)
        # stating if there were any models used
        model2Output = model1Output = dcc.Markdown("No Models were used", className='Outputs')
        
        return model1Output, model2Output, FinalouterparserOutput, completeoutput
    
    # instruction2 = """You are doctor that is attempting to read the clinical note to extract all types of Relapses that the patient was diagnosed with and the year that each diagnosis was given. You know that a patient may or may not have a relapse in their multiple sclerosis and that a relapse in multiple sclerosis could be one of the following types: Transverse myelitis (myelitis) or optic neuritis (ON) or brain stem. If they are mentioned then the patient experienced a relapse. Use this information to concisely extract that information from the clinical note that the user provides into bullet points that start with `-` of the relapse type with the date that it was diagnosed in. Remember that a clinical note may or may not state that there was a relapse. You are not diagnosing the patient just extracting the information present."""

    if model1Name != 'None' and model1Name != None:
        print('runing model 1...')
        llm1 = class_dict[model1Name]
        #Chronos best pipe
        llm1.setupModelAndTokenizer()
        llm1.createPipe(temperature= model1Temp, max_length=model1Generation, top_p=model1topP, top_k=model1topK, repetition_penalty=mode1RepetitionPen)
        
        for i in range(len(notes)):
            note = notes[i]
            question = f"clinical note:{note}"
            prompt = llm1.getprompt(model1prompt, question)
            response = llm1.generateText(promptInput=prompt)
            response = f"{response[0]['generated_text']}"
            onlyResponse = llm1.getResponseOnly(response)
            onlyResponse = format_string(onlyResponse)
            llm1TextOnly.append(onlyResponse)
            # printing out
            print(f"model 1 resonse: {onlyResponse}")
            model1Output.append(html.Div([html.H5(f"Note - {i} output"), dcc.Markdown(onlyResponse)], className='Outputs', id={'type': 'output', 'index': i}))
        llm1.deleteInstance()
    
    if model2Name != 'None' and model2Name != None:
        print('running model 2.....')
        llm2 = class_dict[model2Name]
        llm2.setupModelAndTokenizer()
        #vicuna hot reg or wizard
        llm2.createPipe(temperature= model2Temp, max_length=model2Generation, top_p=model2topP, top_k=model2topK, repetition_penalty=mode2RepetitionPen)
        for i in range(len(notes)):
            note = notes[i]
            question = f"clinical note:{note}"
            prompt = llm2.getprompt(model2prompt, question)
            response = llm2.generateText(promptInput=prompt)
            response = f"{response[0]['generated_text']}"
            onlyResponse = llm2.getResponseOnly(response)
            onlyResponse = format_string(onlyResponse)
            llm2TextOnly.append(onlyResponse)
            # printing out
            print(f"model 2 resonse: {onlyResponse}")
            model2Output.append(html.Div([html.H5(f"Note - {i} output"), dcc.Markdown(onlyResponse)], className='Outputs', id={'type': 'output2', 'index': i}))
        llm2.deleteInstance()
    
    if len(llm1TextOnly) == 0:
        llm1TextOnly = llm2TextOnly
    elif len(llm2TextOnly) == 0:
        llm1TextOnly = llm1TextOnly
    else:
        for i in range(len(llm2TextOnly)):
            llm1TextOnly[i] = llm1TextOnly[i] + " "+llm2TextOnly[i]

    llm3 = class_dict[model3Name]
    llm3.setupModelAndTokenizer()
    llm3.createPipe(temperature= model3Temp, max_length=model3Generation, top_p=model3topP, top_k=model3topK, repetition_penalty=mode3RepetitionPen)
    outerparserOutput = []
    for i in range(len(llm1TextOnly)):
        parsed = str(outparser(note=llm1TextOnly[i], question=model3prompt, llm=llm3))
        outerparserOutput.append(html.Div([html.H5(f"Note - {i} output"), dcc.Markdown(parsed)], className='Outputs', id={'type': 'output3', 'index': i}))
    
    llm3.deleteInstance()
    del llm3

    return model1Output, model2Output, outerparserOutput, completeoutput 

# starting the main function
if __name__ == "__main__":
    app.run_server(debug=True, port=8040, use_reloader=False)
