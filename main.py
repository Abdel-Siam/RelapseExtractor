from dash import Dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import dash
import json
import os
import base64
import time
import re

import pandas as pd

from llms.wizard13BGPTQ import wizard13bGPTQ
from llms.wizardvicuna13 import WizardVicuna
from llms.wizardMega import WizardMega
from llms.vicuna13 import Vicuna
from llms.wizardHot import Wizard13BHot
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
              'WizardHot': Wizard13BHot(),
              'KoalaHot13B':Koala(),
              'OrcaMiniv2':OrcaMini(),
              'WizardVicuna13': WizardVicuna(),
              'WizardMega': WizardMega(),
              'Vicuna13': Vicuna(),
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

#################################################### Modals ####################################################
# modal for adding a new note
newNoteModal = dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Add New Note:")),
            dbc.ModalBody([
                dcc.Textarea(id="newClinNote", className="newClinNote", style={"width":"100%",'height':'750px'})
            ]),
            dbc.ModalFooter(
                dbc.Row([
                    dbc.Col(dbc.Button("Submit", id="SubmitNewNote", className="me-auto", n_clicks=0, style = {'width':'100%', 'height':'50px'})),
                    dbc.Col(dbc.Button("Close", id="CloseModal", className="ms-auto", n_clicks=0, style = {'width':'100%', 'height':'50px'}))
                ], style={'width':'100%'})
            ),
        ],
        id="AddNote",
        is_open=False,
        size="xl",
    )

# modal for saiving configuration
saveconfigModal = dbc.Modal([
        dbc.ModalHeader("Save Configuration"),
        dbc.ModalBody([
            dbc.Input(id="fileName", placeholder="Enter file name", type="text"),
        ]),
        dbc.ModalFooter([
            dbc.Col(dbc.Button("Save", id="saveConfigButton", className="ms-auto", n_clicks=0, style={'width':'100%'})),
            dbc.Col(dbc.Button("Cancel", id="cancelConfigButton", className="ms-auto", n_clicks=0,  style={'width':'100%'})),
        ])
    ], id="save-popup", is_open=False)

# modal for loading a new file
loadFile = dbc.Modal([
    dbc.ModalHeader("Load Excel File"),
    dbc.ModalBody([
        dbc.Row(dcc.Upload(
            id='upload-data',
            children=dbc.Button("Upload Excel File", style = {'width':'100%'}),
            multiple=False
            
        ),style = {'margin-bottom':'15px'}),
        dbc.Row(dcc.Dropdown(
            id='column-dropdown',
            placeholder="Select a column",
        ))
    ]),
    dbc.ModalFooter([
        dbc.Col(dbc.Button("Load", id="loadFile", className="ms-auto", n_clicks=0, style={'width':'100%'})),
        dbc.Col(dbc.Button("Cancel", id="cancelFileLoad", className="ms-auto", n_clicks=0,  style={'width':'100%'})),
    ])
], id="loadFile-popup", is_open=False)

# modal for saving to excel file
saveToExcel = dbc.Modal([
    dbc.ModalHeader("Save To Excel"),
    dbc.ModalBody([
        dbc.Row([dbc.Col(html.H5('File Name: ', style = {'color':'#000000'}), width = 3),
                 dbc.Col(dcc.Input(id='ExcelFileName', style={'width':'100%'}), width = 9)],style = {'margin-bottom':'15px'}),
    ]),
    dbc.ModalFooter([
        dbc.Col(dbc.Button("Save", id="saveToExcelFile", className="ms-auto", n_clicks=0, style={'width':'100%'})),
        dbc.Col(dbc.Button("Cancel", id="CancelSavingExcel", className="ms-auto", n_clicks=0,  style={'width':'100%'})),
    ])
], id="SaveToExcel-popup", is_open=False)


# modal for model options
rowStyles = {'margin-top':'20px', 'margin-bottom':'5px'}

optionsModal = dbc.Modal([
                dbc.ModalHeader(dbc.Row([
                                dbc.Col(dbc.ModalTitle("Options Modal"), width = 3),
                                dbc.Col(dbc.Row([
                                    dbc.Col(dcc.Dropdown(
                                        id='configdropdown',
                                        options=[],
                                        placeholder='Select a configuration',
                                        style = {'width':'100%'}
                                        )),
                                    dbc.Col(dbc.Button("Load Config", id="LoadConfig", className="ms-auto", n_clicks=0, style = {'width':'100%'})),
                                    dbc.Col(dbc.Button("Save Config", id="SaveConfig", className="ms-auto", n_clicks=0, style = {'width':'100%'})),
                                    dbc.Col(dbc.Button("Refresh", id="refresh", className="ms-auto", n_clicks=0, style = {'width':'100%'}))]))
                                    ], style = {'width':'100%'})),
                
                dbc.ModalBody([
                    dbc.Row([
                        dbc.Col(html.H3("LLM Model 1", style={'color':'#000000'})),
                        dbc.Col(html.H3("LLM Model 2", style={'color':'#000000'})),
                        dbc.Col(html.H3("Parser Model", style={'color':'#000000'})),
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Dropdown(
                            id='model1-dropdown',
                            options=[{'label': name, 'value': name} for name in class_names],
                            placeholder='Wizard13B',
                            value='Wizard13B'
                            )),
                        dbc.Col(dcc.Dropdown(
                            id='model2-dropdown',
                            options=[{'label': name, 'value': name} for name in class_names],
                            placeholder='Select a Model...'
                            )),
                        dbc.Col(dcc.Dropdown(
                            id='model3-dropdown',
                            options=[{'label': name, 'value': name} for name in class_names],
                            placeholder='Wizard13B',
                            value='Wizard13B'
                            )),
                    ], style = rowStyles),
                    dbc.Row(html.H5('Generation Length: ', style={'color':'#000000'})),
                    dbc.Row(html.Div('This parameter determines the quantity or volume of the generated output produced by the models.')),
                    dbc.Row([
                        dbc.Col(dcc.Slider(
                            id='Generation-slider1',
                            min=256,
                            max=2048,
                            step=256,
                            value=512,
                            marks={i: '{:,}'.format(i) for i in range(256, 2049, 256)},
                            tooltip={"placement": "top", "always_visible": True},
                            updatemode="drag"
                        )),
                        dbc.Col(dcc.Slider(
                            id='Generation-slider2',
                            min=256,
                            max=2048,
                            step=256,
                            value=512,
                            marks={i: '{:,}'.format(i) for i in range(256, 2049, 256)},
                            tooltip={"placement": "top", "always_visible": True},
                            updatemode="drag"
                        )),
                        dbc.Col(dcc.Slider(
                            id='Generation-slider3',
                            min=256,
                            max=2048,
                            step=256,
                            value=512,
                            marks={i: '{:,}'.format(i) for i in range(256, 2049, 256)},
                            tooltip={"placement": "top", "always_visible": True},
                            updatemode="drag"
                        ))
                    ], style = rowStyles),
                    dbc.Row(html.H5('Temperature:', style={'color':'#000000'})),
                    dbc.Row(html.Div('Controls the randomness of the generated text. Higher values (e.g., 1.0) make the output more diverse, while lower values (e.g., 0.2) make it more focused and deterministic.')),
                    dbc.Row([
                        dbc.Col(dcc.Slider(
                                id='temperature-slider1',
                                min=0,
                                max=1,
                                step=0.05,
                                value=0.7,
                                marks={i: str(i) for i in range(0, 11)},
                                tooltip={"placement": "top", "always_visible": True}
                            )),
                        dbc.Col(dcc.Slider(
                                id='temperature-slider2',
                                min=0,
                                max=1,
                                step=0.05,
                                value=0.7,
                                marks={i: str(i) for i in range(0, 11)},
                                tooltip={"placement": "top", "always_visible": True}
                            )),
                        dbc.Col(dcc.Slider(
                                id='temperature-slider3',
                                min=0,
                                max=1,
                                step=0.05,
                                value=0.7,
                                marks={i: str(i) for i in range(0, 11)},
                                tooltip={"placement": "top", "always_visible": True}
                            )),
                    ], style = rowStyles),
                    
                    dbc.Row(html.H5('Top_p:', style={'color':'#000000'}),),
                    dbc.Row(html.Div('Determines the cumulative probability threshold for generating the next word. Higher values (e.g., 0.8) result in more diverse outputs, while lower values (e.g., 0.2) make the output more focused and deterministic.')),
                    dbc.Row([
                        dbc.Col(dcc.Slider(
                                id='top-p-slider1',
                                min=0,
                                max=1,
                                step=0.01,
                                value=0.9,
                                marks={i: str(i) for i in range(0, 11)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),),
                        dbc.Col(dcc.Slider(
                                id='top-p-slider2',
                                min=0,
                                max=1,
                                step=0.01,
                                value=0.9,
                                marks={i: str(i) for i in range(0, 11)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),),
                        dbc.Col(dcc.Slider(
                                id='top-p-slider3',
                                min=0,
                                max=1,
                                step=0.01,
                                value=0.9,
                                marks={i: str(i) for i in range(0, 11)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),),
                    ], style = rowStyles),
                    dbc.Row(html.H5('Top_k:', style={'color':'#000000'})),
                    dbc.Row(html.Div('Limits the number of choices considered for each token during text generation. Higher values (e.g., 50) allow for more diversity, while lower values (e.g., 10) make the output more focused and deterministic.')),
                    dbc.Row([
                        dbc.Col(dcc.Slider(
                                id='top-k-slider1',
                                min=0,
                                max=50,
                                step=5,
                                value=20,
                                marks={i: str(i) for i in range(0, 51, 10)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),),
                        dbc.Col(dcc.Slider(
                                id='top-k-slider2',
                                min=0,
                                max=50,
                                step=5,
                                value=20,
                                marks={i: str(i) for i in range(0, 51, 10)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),),
                        dbc.Col(dcc.Slider(
                                id='top-k-slider3',
                                min=0,
                                max=50,
                                step=5,
                                value=20,
                                marks={i: str(i) for i in range(0, 51, 10)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),),
                    ], style = rowStyles),
                    
                    dbc.Row(html.H5('Repetition Penalty:', style={'color':'#000000'})),
                    dbc.Row(html.Div('Controls the penalty applied to repeated words in the generated text. Higher values (e.g., 1.5) reduce the likelihood of repetitive phrases, while lower values (e.g., 1.0) allow more repetitions.')),
                    dbc.Row([
                        dbc.Col(dcc.Slider(
                                id='repetition-penalty-slider1',
                                min=1,
                                max=2,
                                step=0.01,
                                value=1.15,
                                marks={i: str(i) for i in range(1, 21, 2)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),),
                        dbc.Col(dcc.Slider(
                                id='repetition-penalty-slider2',
                                min=1,
                                max=2,
                                step=0.01,
                                value=1.15,
                                marks={i: str(i) for i in range(1, 21, 2)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),),
                        dbc.Col(dcc.Slider(
                                id='repetition-penalty-slider3',
                                min=1,
                                max=2,
                                step=0.01,
                                value=1.15,
                                marks={i: str(i) for i in range(1, 21, 2)},
                                tooltip={"placement": "top", "always_visible": True}
                            ),),
                    ], style = rowStyles),
                    
                        
                    dbc.Row(dbc.Col([
                        html.H3("Prompting:", style={'color':'#000000'}),
                        html.H5('Model 1 Prompt: ', style={'color':'#000000'}),
                        dbc.Textarea(id="promptModel1", value="You are doctor that is attempting to read the clinical note to extract all types of Relapses that the patient was diagnosed with and the year that each diagnosis was given. You know that a patient may or may not have a relapse in their multiple sclerosis and that a relapse in multiple sclerosis could be one of the following types: Transverse myelitis (myelitis) or optic neuritis (ON) or brain stem. If they are mentioned then the patient experienced a relapse. Use this information to concisely extract that information from the clinical note that the user provides into bullet points that start with `-` of the relapse type with the date that it was diagnosed in. Remember that a clinical note may or may not state that there was a relapse. You are not diagnosing the patient just extracting the information present.", style={'height':'15vh'}),
                        html.H5('Model 2 Prompt: ', style={'color':'#000000'}),
                        dbc.Textarea(id="promptModel2", value="You are doctor that is attempting to read the clinical note to extract all types of Relapses that the patient was diagnosed with and the year that each diagnosis was given. You know that a patient may or may not have a relapse in their multiple sclerosis and that a relapse in multiple sclerosis could be one of the following types: Transverse myelitis (myelitis) or optic neuritis (ON) or brain stem. If they are mentioned then the patient experienced a relapse. Use this information to concisely extract that information from the clinical note that the user provides into bullet points that start with `-` of the relapse type with the date that it was diagnosed in. Remember that a clinical note may or may not state that there was a relapse. You are not diagnosing the patient just extracting the information present.", style={'height':'15vh'}),
                        html.H5('Outer Parser Prompting: ', style={'color':'#000000'}),
                        dbc.Textarea(id="promptModel3", value="From the provided Patient Information, only extract all instances of relapses and the date of onset of each instance into a json format with each relapse and its onset date grouped together. Do not extract extra information.", style={'height':'15vh'}),
                        ], width=12)),
                    
                ], style={'overflow':'auto', 'max-height':'80vh'}),

                    dbc.ModalFooter([
                            dbc.Button("Close", id="CloseModal2", className="ms-auto", n_clicks=0)
                        ])
                ],
                id="OptionsModal",
                is_open=False,
                size="xl"
            )

#################################################### Main Dashboard ####################################################
# main Dashboard
OutputWidths = 4
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
                    dbc.Row(html.Button("Import from Excel", id="Import-button", n_clicks=0), style={'margin-bottom': '10px', 'height':'5vh'}),
                    dbc.Row(html.Button("Export to Excel", id="Export-button", n_clicks=0), style={'margin-bottom': '10px', 'height':'5vh'}),
                    dbc.Row(html.Button("Start", id="start-button", n_clicks=0), style={'margin-bottom': '10px', 'height':'5vh'})
                ], width=1, className='ButtonsCol'),
                dbc.Col([
                    html.Div(id = 'viewDiv', className="viewDiv")
                ])
            ], style={'height':'45vh'}),
        dbc.Row(html.H2("Output:")),
        dbc.Row(html.Div(id='timeOutput')),
        dbc.Row([
            dbc.Col(html.H4("model 1 Output: "), width=OutputWidths),
            dbc.Col(html.H4("model 2 Output: "), width=OutputWidths),
            dbc.Col(html.H4("Parser Output:"), width=OutputWidths),
            #dbc.Col(html.H4(""), width=OutputWidths),
        ], style={'height':'5vh'}),
        dbc.Row(dcc.Loading(dbc.Row([
            dbc.Col(html.Div(id = 'Model1', className="Model1"), width=OutputWidths),
            dbc.Col(html.Div(id = 'Model2', className="Model2"), width=OutputWidths),
            dbc.Col(html.Div(id = 'CombinedOutput', className="CombinedOutput"), width=OutputWidths),
            #dbc.Col(html.Div(id = 'CompleteOuput', className="CompleteOuput"), width=OutputWidths),
        ], style={'width':'100%', 'height':'100%'})), style={'height':'30vh'}),
        newNoteModal,
        optionsModal,
        saveconfigModal,
        loadFile,
        saveToExcel,
    ],
    style={"width": "90%", "margin": "auto"},
)
#################################################### CALLBACKS ####################################################
### show clicked on notes
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

### Updating the Configurations dropdown on clicking refresh
def get_config_files():
    config_folder = './configs'
    if os.path.exists(config_folder):
        files = os.listdir(config_folder)
        json_files = [f for f in files if f.endswith('.json')]
        return json_files
    return []

@app.callback(
    Output('configdropdown', 'options'),
    [Input('refresh', 'n_clicks')]
)
def update_config_dropdown(n_clicks):
    config_files = get_config_files()
    dropdown_options = [{'label': file, 'value': file} for file in config_files]
    return dropdown_options


### adding a new note to the list of notes
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

### toggling add note modal on and off 
@app.callback(
    Output("AddNote", "is_open"),
    [Input("add-button", "n_clicks"), Input("CloseModal", "n_clicks"), Input('SubmitNewNote', 'n_clicks')],
    [State("AddNote", "is_open")],
)
def toggle_Notemodal(n1, n2, n_click, is_open):
    if n1 or n2:
        return not is_open
    return is_open

### toggling options modal on and off
@app.callback(
    Output("OptionsModal", "is_open"),
    [Input("options-button", "n_clicks"), Input("CloseModal2", "n_clicks")],
    [State("OptionsModal", "is_open")],
)
def toggle_OptionsModal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

################ Functions for importing excel file 

@app.callback(
    Output('column-dropdown', 'options'),
    Output('column-dropdown', 'value'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_column_dropdown(contents, filename):
    global df
    
    if contents is not None:
        # Decode contents and save the file locally
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        temp_filename = 'temp.xlsx'  # Temporary filename to save the uploaded file
        with open(temp_filename, 'wb') as f:
            f.write(decoded)

        # Read the Excel file
        df = pd.read_excel(temp_filename)
        columns = [{'label': col, 'value': col} for col in df.columns]

        # Clean up the temporary file
        os.remove(temp_filename)

        return columns, columns[0]['value']
    else:
        return [], None


### toggling add note modal on and off 
@app.callback(
    Output("loadFile-popup", "is_open"),
    [Input("Import-button", "n_clicks"), Input("cancelFileLoad", "n_clicks")],
    [State("loadFile-popup", "is_open")],
)
def toggle_LoadExcel(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    [Output("NotesDiv", "children", allow_duplicate=True),
     Output("newClinNote", "value", allow_duplicate=True),
     Output("loadFile-popup", "is_open", allow_duplicate=True),],
    [Input('loadFile', 'n_clicks'),
     State('column-dropdown', 'value')],
    prevent_initial_call=True
)
def toggle_LoadExcel(n1, columnName):
    global df
    loadedNotes = []
    NoteNumber = 0
    if 'df' in globals():
        print("Loading File ....")
        for i, value in enumerate(df[columnName]):
            if not pd.isna(value):  # Skip empty rows
                newCard = html.Div([
                    html.H5('Note Number: ' + str(NoteNumber)),
                    html.H5(str(value), id={'type': 'individualnotes', 'index': NoteNumber})
                ], className='notes', id={'type': 'note', 'index': NoteNumber})
                # iterate note number
                NoteNumber += 1
                loadedNotes.append(newCard)

    return loadedNotes, "", False

################ Functions for removing the last note
### removing the last note from the list of notes
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


### Callbacks for showing/hiding the save popup modal
@app.callback(
    Output("save-popup", "is_open"),
    [Input("SaveConfig", "n_clicks"), Input("cancelConfigButton", "n_clicks"), Input("saveConfigButton", "n_clicks")],
    [State("save-popup", "is_open")]
)
def toggle_save_popup(save_clicks, cancel_clicks, save_button_clicks, is_open):
    if save_clicks or cancel_clicks or save_button_clicks:
        return not is_open
    return is_open

def save_configuration(values, filename):
    folder_path = "./configs"
    file_name = filename+'.json'
    file_path = os.path.join(folder_path, file_name)

    # Create the configs folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Save the values to a JSON file
    with open(file_path, "w") as file:
        json.dump(values, file)

### Callback function for the "Save Config" button click event
@app.callback(
    Output("OptionsModal", "is_open", allow_duplicate=True),
    Output("configdropdown", "options", allow_duplicate=True),
    Input("saveConfigButton", "n_clicks"),
    State("fileName", "value"),
    State("model1-dropdown", "value"),
    State("model2-dropdown", "value"),
    State("model3-dropdown", "value"),
    State("Generation-slider1", "value"),
    State("Generation-slider2", "value"),
    State("Generation-slider3", "value"),
    State("temperature-slider1", "value"),
    State("temperature-slider2", "value"),
    State("temperature-slider3", "value"),
    State("top-p-slider1", "value"),
    State("top-p-slider2", "value"),
    State("top-p-slider3", "value"),
    State("top-k-slider1", "value"),
    State("top-k-slider2", "value"),
    State("top-k-slider3", "value"),
    State("repetition-penalty-slider1", "value"),
    State("repetition-penalty-slider2", "value"),
    State("repetition-penalty-slider3", "value"),
    State("promptModel1", "value"),
    State("promptModel2", "value"),
    State("promptModel3", "value"),
    prevent_initial_call=True
)
def save_config(n_clicks, filename, model1, model2, model3, gen1, gen2, gen3, temp1, temp2, temp3, top_p1, top_p2, top_p3,
                top_k1, top_k2, top_k3, rep_penalty1, rep_penalty2, rep_penalty3, prompt1, prompt2, prompt3):
    if n_clicks > 0:
        values = {
            "model1": model1,
            "model2": model2,
            "model3": model3,
            "generation_length": [gen1, gen2, gen3],
            "temperature": [temp1, temp2, temp3],
            "top_p": [top_p1, top_p2, top_p3],
            "top_k": [top_k1, top_k2, top_k3],
            "repetition_penalty": [rep_penalty1, rep_penalty2, rep_penalty3],
            "prompt_model1": prompt1,
            "prompt_model2": prompt2,
            "prompt_model3": prompt3
        }
        save_configuration(values, filename)
    return False, []

################ Functions for Saving the output as excel file
### toggling saving to excel file
@app.callback(
    Output("SaveToExcel-popup", "is_open"),
    [Input("Export-button", "n_clicks"), Input("CancelSavingExcel", "n_clicks")],
    [State("SaveToExcel-popup", "is_open")],
)
def toggle_SavingToExcel(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


import openpyxl

### function for saving on clicking save
@app.callback(
    Output("SaveToExcel-popup", "is_open", allow_duplicate=True),
    Input("saveToExcelFile", "n_clicks"),
    [
    State('ExcelFileName', 'value'),
    State({'type': 'note', 'index': ALL}, 'children'),
    State({'type': 'output', 'index': ALL}, 'children'),
    State({'type': 'output2', 'index': ALL}, 'children'),
    State({'type': 'output3', 'index': ALL}, 'children'),
    
    State("model1-dropdown", "value"),
    State("model2-dropdown", "value"),
    State("model3-dropdown", "value"),
    State("Generation-slider1", "value"),
    State("Generation-slider2", "value"),
    State("Generation-slider3", "value"),
    State("temperature-slider1", "value"),
    State("temperature-slider2", "value"),
    State("temperature-slider3", "value"),
    State("top-p-slider1", "value"),
    State("top-p-slider2", "value"),
    State("top-p-slider3", "value"),
    State("top-k-slider1", "value"),
    State("top-k-slider2", "value"),
    State("top-k-slider3", "value"),
    State("repetition-penalty-slider1", "value"),
    State("repetition-penalty-slider2", "value"),
    State("repetition-penalty-slider3", "value"),
    State("promptModel1", "value"),
    State("promptModel2", "value"),
    State("promptModel3", "value"),    
    ],
    prevent_initial_call=True
)
def saveToExcel(nclick, filename, Notes, model1Output, model2Output, model3Output, model1, model2, model3, gen1, gen2, gen3,
                temp1, temp2, temp3, top_p1, top_p2, top_p3, top_k1, top_k2, top_k3,
                rep_penalty1, rep_penalty2, rep_penalty3, prompt1, prompt2, prompt3):
    
    # Create a new workbook
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    
    # Write column headers
    headers = ["Notes", "Model 1 Output", "Model 2 Output", "Model 3 Output"]
    sheet.append(headers)

    # Iterate over the data and write to the sheet
    for i in range(len(Notes)):
        
        # COULD CHANGE THE CODING OF THIS SO THAT IT DOESNT CAUSE FUTURE ERROR
        if model1Output == []:
            model1Output = ""
        else:
            model1Output = model1Output[i][1]['props']['children']       
        
        if model2Output == []:
            model2Output = ""
        else:
            model2Output = model2Output[i][1]['props']['children']        
            
        if model3Output == []:
            model3Output = ""
        else:
            model3Output = model3Output[i][1]['props']['children']
            
            
        row = [Notes[i][1]['props']['children'], model1Output, model2Output, model3Output]
        sheet.append(row)
    
    sheet.append(['Settings'])
    
    sheet.append(["Model 1", "Model 2", "Model 3", "Generation 1", "Generation 2", "Generation 3", "Temperature 1", "Temperature 2", "Temperature 3",
               "Top-p 1", "Top-p 2", "Top-p 3", "Top-k 1", "Top-k 2", "Top-k 3", "Repetition Penalty 1",
               "Repetition Penalty 2", "Repetition Penalty 3", "Prompt Model 1", "Prompt Model 2", "Prompt Model 3"])
    sheet.append([model1, model2, model3, gen1, gen2, gen3,temp1, temp2, temp3, top_p1, top_p2, top_p3, 
               top_k1, top_k2, top_k3, rep_penalty1, rep_penalty2, rep_penalty3, prompt1, prompt2, prompt3])
    # Save the workbook with the given filename
    workbook.save(filename + ".xlsx")
    
    # Return False to close the modal
    return False

from parser import outparser

# def format_string(input_string):
#     output_string = ""
#     for word in input_string.split():
#         if word.isdigit() and len(word) == 3 and '0' in word:
#             output_string += word.replace('0', '00') + ' '
#         else:
#             output_string += word + ' '
#     return output_string.strip()


def load_configuration(file_name):
    folder_path = "configs"
    file_path = os.path.join(folder_path, file_name)

    # Check if the configuration file exists
    if not os.path.exists(file_path):
        return None

    # Load the values from the JSON file
    with open(file_path, "r") as file:
        values = json.load(file)

    return values

### Callback function for the "Load Config" button click event
@app.callback(
    Output("model1-dropdown", "value"),
    Output("model2-dropdown", "value"),
    Output("model3-dropdown", "value"),
    Output("Generation-slider1", "value"),
    Output("Generation-slider2", "value"),
    Output("Generation-slider3", "value"),
    Output("temperature-slider1", "value"),
    Output("temperature-slider2", "value"),
    Output("temperature-slider3", "value"),
    Output("top-p-slider1", "value"),
    Output("top-p-slider2", "value"),
    Output("top-p-slider3", "value"),
    Output("top-k-slider1", "value"),
    Output("top-k-slider2", "value"),
    Output("top-k-slider3", "value"),
    Output("repetition-penalty-slider1", "value"),
    Output("repetition-penalty-slider2", "value"),
    Output("repetition-penalty-slider3", "value"),
    Output("promptModel1", "value"),
    Output("promptModel2", "value"),
    Output("promptModel3", "value"),
    
    Input("LoadConfig", "n_clicks"),
    State("configdropdown", "value"),
    prevent_initial_call=True
)
def load_config(n_clicks, file_name):
    if n_clicks > 0 and file_name:
        values = load_configuration(file_name)
        if values:
            return values["model1"], values["model2"],values["model3"],values["generation_length"][0],values["generation_length"][1],values["generation_length"][2],values["temperature"][0],values["temperature"][1],values["temperature"][2],values["top_p"][0],values["top_p"][1],values["top_p"][2],values["top_k"][0],values["top_k"][1],values["top_k"][2],values["repetition_penalty"][0],values["repetition_penalty"][1],values["repetition_penalty"][2],values["prompt_model1"], values["prompt_model2"],values["prompt_model3"]
            # Assign other values to output components here
    return None, None, None, None, None, None,None, None, None,None, None, None,None, None, None,None, None, None, None, None, None
    # Return None for other output components

### Function for running the main notes
@app.callback(
    [Output("Model1", "children"),
     Output("Model2", "children"),
     Output("CombinedOutput", "children"),
     Output("timeOutput", "children"),
     #Output("CompleteOuput", "children")
     ],
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
    #completeoutput = ''
    llm1TextOnly = []    
    llm2TextOnly = []
    
    timeTaken = f""
    
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
        
        parserStarTime = time.time()
        
        #change everything to an html.p
        for i in range(len(outerparserOutput)):
            FinalouterparserOutput.append(html.Div([html.H5(f"Note - {i} output"), dcc.Markdown(outerparserOutput[i], className='Outputs')], id={'type': 'output', 'index': i}))
            
        parserEndTime = time.time()
        #print(outerparserOutput)
        # stating if there were any models used
        model2Output = model1Output = [dcc.Markdown("No Models were used", className='Outputs')]
        
        parserExecTime = parserEndTime-parserStarTime
        
        timeTaken = html.P(f'Model 1 and Model 2 were not run only the Parser. Parser took: {parserExecTime:.2f} sec to run all Notes', id = 'execTime')
        
        return model1Output, model2Output, FinalouterparserOutput, timeTaken #, completeoutput
    
    # instruction2 = """You are doctor that is attempting to read the clinical note to extract all types of Relapses that the patient was diagnosed with and the year that each diagnosis was given. You know that a patient may or may not have a relapse in their multiple sclerosis and that a relapse in multiple sclerosis could be one of the following types: Transverse myelitis (myelitis) or optic neuritis (ON) or brain stem. If they are mentioned then the patient experienced a relapse. Use this information to concisely extract that information from the clinical note that the user provides into bullet points that start with `-` of the relapse type with the date that it was diagnosed in. Remember that a clinical note may or may not state that there was a relapse. You are not diagnosing the patient just extracting the information present."""

    if model1Name != 'None' and model1Name != None:
        print('runing model 1...')
        llm1 = class_dict[model1Name]

        model1StartTime = time.time()
        
        llm1.setupModelAndTokenizer()
        llm1.createPipe(temperature= model1Temp, max_length=model1Generation, top_p=model1topP, top_k=model1topK, repetition_penalty=mode1RepetitionPen)
        
        for i in range(len(notes)):
            note = notes[i]
            question = f"clinical note:{note}"
            prompt = llm1.getprompt(model1prompt, question)
            response = llm1.generateText(promptInput=prompt)
            response = f"{response[0]['generated_text']}"
            onlyResponse = llm1.getResponseOnly(response)
            #onlyResponse = format_string(onlyResponse)
            llm1TextOnly.append(onlyResponse)
            # printing out
            print(f"model 1 resonse: {onlyResponse}")
            model1Output.append(html.Div([html.H5(f"Note - {i} output"), dcc.Markdown(onlyResponse)], className='Outputs', id={'type': 'output', 'index': i}))
        llm1.deleteInstance()

        model1EndTime = time.time()
        
    else:
        model1StartTime = model1EndTime = 0
        
        
    if model2Name != 'None' and model2Name != None:
        print('running model 2.....')
        llm2 = class_dict[model2Name]
        
        model2StartTime = time.time()
        
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
            #onlyResponse = format_string(onlyResponse)
            llm2TextOnly.append(onlyResponse)
            # printing out
            print(f"model 2 resonse: {onlyResponse}")
            model2Output.append(html.Div([html.H5(f"Note - {i} output"), dcc.Markdown(onlyResponse)], className='Outputs', id={'type': 'output2', 'index': i}))
        llm2.deleteInstance()
        
        model2EndTime = time.time()
    
    else:
        model2StartTime = model2EndTime = 0
    
    if len(llm1TextOnly) == 0:
        llm1TextOnly = llm2TextOnly
    elif len(llm2TextOnly) == 0:
        llm1TextOnly = llm1TextOnly
    else:
        for i in range(len(llm2TextOnly)):
            llm1TextOnly[i] = llm1TextOnly[i] + " "+llm2TextOnly[i]

    model3StartTime = time.time()
    
    llm3 = class_dict[model3Name]
    llm3.setupModelAndTokenizer()
    llm3.createPipe(temperature= model3Temp, max_length=model3Generation, top_p=model3topP, top_k=model3topK, repetition_penalty=mode3RepetitionPen)
    outerparserOutput = []
    for i in range(len(llm1TextOnly)):
        parsed = str(outparser(note=llm1TextOnly[i], question=model3prompt, llm=llm3))
        outerparserOutput.append(html.Div([html.H5(f"Note - {i} output"), dcc.Markdown(parsed)], className='Outputs', id={'type': 'output3', 'index': i}))
    
    llm3.deleteInstance()
    del llm3

    model3EndTime = time.time()
    
    model1ExecTime = model1EndTime - model1StartTime    
    model2ExecTime = model2EndTime - model2StartTime    
    model3ExecTime = model3EndTime - model3StartTime
    
    totalTime = model3EndTime - model1StartTime
    timeTaken = html.P(f'Execuation Times: Model 1 took: {model1ExecTime:.2f} sec. Model 2 Took: {model2ExecTime:.2f} sec. Parser took: {model3ExecTime:.2f} sec to run all Notes. Total Time: {totalTime:.2f} sec. *Note: if time = 0.00 then the model was not run.', id = 'execTime')


    return model1Output, model2Output, outerparserOutput, timeTaken #, completeoutput 

#################################################### StartMain function ####################################################
### starting the main function
if __name__ == "__main__":
    app.run_server(debug=True, port=8040, use_reloader=False)
