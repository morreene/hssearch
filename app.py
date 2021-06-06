"""
This app creates a responsive sidebar layout with dash-bootstrap-components and
some custom css with media queries.

When the screen is small, the sidebar moved to the top of the page, and the
links get hidden in a collapse element. We use a callback to toggle the
collapse when on a small screen, and the custom CSS to hide the toggle, and
force the collapse to stay open when the screen is large.

dcc.Location is used to track the current location. There are two callbacks,
one uses the current location to render the appropriate page content, the other
uses the current location to toggle the "active" properties of the navigation
links.

For more details on building multi-page Dash applications, check out the Dash
documentation: https://dash.plot.ly/urls
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash_auth
from dash.dependencies import Input, Output, State

import pandas as pd

# for text_preprocessing
from bs4 import BeautifulSoup
import unidecode
from word2number import w2n
import contractions
import spacy
nlp = spacy.load('en_core_web_sm')

# exclude words from spacy stopwords list
deselect_stop_words = ['no', 'not', 'least']
for w in deselect_stop_words:
    nlp.vocab[w].is_stop = False


def strip_html_tags(text):
    """remove html tags from text"""
    soup = BeautifulSoup(text, "html.parser")
    stripped_text = soup.get_text(separator=" ")
    return stripped_text


def remove_whitespace(text):
    """remove extra whitespaces from text"""
    text = text.strip()
    return " ".join(text.split())


def remove_accented_chars(text):
    """remove accented characters from text, e.g. café"""
    text = unidecode.unidecode(text)
    return text


def expand_contractions(text):
    """expand shortened words, e.g. don't to do not"""
    text = contractions.fix(text)
    return text


def text_preprocessing(text, accented_chars=True, contractions=True,
                       convert_num=True, extra_whitespace=True,
                       lemmatization=True, lowercase=True, punctuations=True,
                       remove_html=True, remove_num=True, special_chars=True,
                       stop_words=True):
    """preprocess text with default option set to true for all steps"""
    if remove_html == True: #remove html tags
        text = strip_html_tags(text)
    if extra_whitespace == True: #remove extra whitespaces
        text = remove_whitespace(text)
    if accented_chars == True: #remove accented characters
        text = remove_accented_chars(text)
    if contractions == True: #expand contractions
        text = expand_contractions(text)
    if lowercase == True: #convert all characters to lowercase
        text = text.lower()

    doc = nlp(text) #tokenise text

    clean_text = []

    for token in doc:
        flag = True
        edit = token.text
        # remove stop words
        if stop_words == True and token.is_stop and token.pos_ != 'NUM':
            flag = False
        # remove punctuations
        if punctuations == True and token.pos_ == 'PUNCT' and flag == True:
            flag = False
        # remove special characters
        if special_chars == True and token.pos_ == 'SYM' and flag == True:
            flag = False
        # remove numbers
        if remove_num == True and (token.pos_ == 'NUM' or token.text.isnumeric()) and flag == True:
            flag = False
        # convert number words to numeric numbers
        if convert_num == True and token.pos_ == 'NUM' and flag == True:
            edit = w2n.word_to_num(token.text)
        # convert tokens to base form
        elif lemmatization == True and token.lemma_ != "-PRON-" and flag == True:
            edit = token.lemma_
        # append tokens edited and not removed to list
        if edit != "" and flag == True:
            clean_text.append(edit)
    # return clean_text
    return ' '.join(clean_text)

# ===== Data =====
data = pd.read_pickle('data/data-3-results.pickle')








# ===== App =====
# Username and password for login
VALID_USERNAME_PASSWORD_PAIRS = {'wto': 'wto'}

external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css']
# external_stylesheets = ['https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.7/css/bootstrap.min.css']

# with "__name__" local css under assets is also included
app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
app.title = 'Better HS Search'
app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-62289743-8"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', 'UA-62289743-8');
        </script>

        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

server = app.server
app.config.suppress_callback_exceptions = True

# we use the Row and Col components to construct the sidebar header
# it consists of a title, and a toggle, the latter is hidden on large screens
sidebar_header = dbc.Row(
    [
        # dbc.Col(html.H3("Ag Texts", className="display-4000")),
        dbc.Col(html.Img(src=app.get_asset_url("logo.png"), width="130px", style={'margin-left':'15px'})),
        dbc.Col(
            html.Button(
                # use the Bootstrap navbar-toggler classes to style the toggle
                html.Span(className="navbar-toggler-icon"),
                className="navbar-toggler",
                # the navbar-toggler classes don't set color, so we do it here
                style={
                    "color": "rgba(0,0,0,.5)",
                    "bordercolor": "rgba(0,0,0,.1)",
                },
                id="toggle",
            ),
            # the column containing the toggle will be only as wide as the
            # toggle, resulting in the toggle being right aligned
            width="auto",
            # vertically align the toggle in the center
            align="center",
        ),
    ]
)

sidebar = html.Div(
    [
        sidebar_header,
        # we wrap the horizontal rule and short blurb in a div that can be
        # hidden on a small screen
        html.Div(
            [
                html.Br(),
                html.Br(),
                # html.P(
                #     "Follow the trade news with data",
                    # className="lead",
                # ),1
            ],
            id="blurb",
        ),
        # use the Collapse component to animate hiding / revealing links
        dbc.Collapse(
            dbc.Nav(
                [   dbc.NavLink("About", href="/page-1", id="page-1-link"),
                    dbc.NavLink("Data", href="/page-2", id="page-2-link"),
                    dbc.NavLink("Search", href="/page-3", id="page-3-link"),
                    # dbc.NavLink("menu x", href="/page-4", id="page-4-link"),
                    # dbc.NavLink("menu x", href="/page-5", id="page-5-link"),
                    # dbc.NavLink("menu x", href="/page-6", id="page-6-link"),
                    # dbc.NavLink("menu x", href="/page-7", id="page-7-link"),
                    # dbc.NavLink("menu x", href="/page-8", id="page-8-link"),
                ],
                vertical=True,
                pills=False,
            ),
            id="collapse",
            # id="sidebar",
        ),

        html.Div([  html.Hr(),
                    html.P(
                        "Version 20210606",
                        # className="lead",
                    ),
                ],
            id="blurb-bottom",
            ),
    ],
    id="sidebar",
)

content = html.Div(id="page-content")
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 4)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f"/page-{i}" for i in range(1, 4)]






@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1"]:
        return html.Div([
                dbc.Jumbotron([
                            html.H4("About the Data and the App", className="display-about"),
                            html.P(
                                "Getting insights from the docs",
                                className="lead",
                            ),
                            html.Hr(className="my-2"),
                            dcc.Markdown(
                                '''
                                Pellentesque posuere pellentesque imperde laoreet’s Velit leading pulvinar velit a hendrerit Donec non pellentesque jus businesses tincidunt. Suspendisse at maximus turpis, non loborsrt.

                                    Dolor sit amet consectetur elit sed do eiusmod tempor incididunt labore et dolore
                                    magna aliqua enim ad minim veniam quis nostrud exercitation ulac laboris aliquip
                                    ex ea commodo consequat duis aute irure.dolor in repre henderit in voluptate velit
                                    esse cillum dolore eu fugiat nulla pariatur excep teur sint cupidatat non proident.

                                Pellentesque posuere pellentesque imperde laoreet’s Velit leading pulvinar velit a hendrerit Donec non pellentesque jus businesses tincidunt. Suspendisse at maximus turpis, non loborsrt.

                                * consectetur elit sed do eius
                                * consectetur elit sed
                                * consectetur elit sed do
                                '''
                                ),
                        ])
        ])
    elif pathname == "/page-2":
        # if 'data' in globals():
        #     del data
        # data = load_data()
        return html.Div([
                html.H3('Data', style={'font-weight': 'bold'}),
                dcc.Markdown(
                    '''
                        Work-in-progress: more data will be added
                    This is the data table behind the search.

                    * HSDesc = the description of code as it is in the latest version of HS
                    * HSDescCleaned = HSDesc with certain predefined texts removed.
                        * excl.
                        * excluding
                    * Alpha = Alphabetical Index
                    * Text =  HSDescCleaned + Alpha
                    * Text_Proc1 = Text with in prcocessed form: remove stopwords (of, with ...), generic form (used >> use, books >> book)
                        * Search will be done on this column
                    '''
                    ),

                dash_table.DataTable(
                    id='table',
                    # columns=[{"name": i, "id": i} for i in textdata.columns],
                    # data=textdata.to_dict('records'),

                    columns=[{"name": i, "id": i} for i in data[['HSVersions', 'HSCode', 'HSDesc', 'HSDescCleaned', 'Alpha', 'Text', 'Text_Proc1']].columns],
                    data=data.to_dict('records'),

                    editable=False,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    column_selectable=False,
                    row_selectable=False,
                    row_deletable=False,
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current= 0,
                    page_size= 20,
                    # style_cell_conditional=[
                    #     {'if': {'column_id': 'Member'},
                    #      'width': '100px'},
                    # ]
                    style_data={
                        'whiteSpace': 'normal',
                        'height': 'auto'
                    },
                    style_cell={
                        # 'height': 'auto',
                        'minWidth': '20px', 'maxWidth': '300px',
                        # 'whiteSpace': 'normal',
                        'textAlign': 'left',
                        'verticalAlign': 'top',
                        'fontSize':12,
                    },
                )
            ])

    elif pathname in ["/page-3"]:
        return html.Div([
            dbc.Row(
                [dbc.Col(
                            [html.P('Search by keywords ...'),
                             dbc.Input(id="input-search", placeholder="Type something...", type="text", value='computer'),
                             dbc.Button('Search', id="button-search", className="mr-2", color="info",),
                            ], width=6
                        ),
                ],
            ),
            html.Br(),
            html.Div(id='results-container')
        ])












    # elif pathname in ["/page-3"]:
    #
    #     return html.Div([
    #                     # Chart 1
    #                     dbc.Row([
    #                         dbc.Col([
    #                             html.H3('Summary Stats', style={'font-weight': 'bold'}),
    #                             html.P(
    #                                 id="description",
    #                                 children=dcc.Markdown(
    #                                   children=(
    #                                     '''
    #                                     Members' submissiong, Chair and Secretariat summaries/notes are not included.
    #                                     ''')
    #                                 )
    #                             ),
    #                             html.Br(),
    #                             html.H6('Number of Proposals by year', style={'font-weight': 'bold'}),
    #                         ], lg=10),
    #                     ]),
    #                     dbc.Row([
    #                         dbc.Col([
    #                             html.Label('Select Pillar:'),
    #                             dcc.Dropdown(
    #                                 id='stat-year-dropdown-pillar',
    #                                 options=[{'label': v, 'value': k}
    #                                             for k, v in dict_pillar.items()],
    #                                 multi=False,
    #                                 value= 'All',
    #                             ),
    #                         ], lg=4),
    #                         dbc.Col([
    #                             html.Label('Select Proponent:'),
    #                             dcc.Dropdown(
    #                                 id='stat-year-dropdown-proponent',
    #                                 options=[{'label': v, 'value': k}
    #                                             for k, v in dict_proponent.items()],
    #                                 multi=False,
    #                                 value= 'All',
    #                             ),
    #                         ], lg=4)
    #                     ]),
    #                     dbc.Row([
    #                         dbc.Col([
    #                             dcc.Graph(
    #                                 id='stat-plot-year-pillar-proponent'
    #                             ),
    #                         ], lg=10),
    #                     ]),
    #
    #                     # Chart 2
    #                     dbc.Row([
    #                         dbc.Col([
    #                             html.Label('Select topic:'),
    #                             dcc.Dropdown(
    #                                 id='stat-year-dropdown-topic',
    #                                 options=[{'label': v, 'value': k}
    #                                             for k, v in dict_topic.items()],
    #                                 multi=False,
    #                                 value= 'All',
    #                             ),
    #                         ], lg=4),
    #                         dbc.Col([
    #                             html.Label('Select Proponent:'),
    #                             dcc.Dropdown(
    #                                 id='stat-year-dropdown-proponent2',
    #                                 options=[{'label': v, 'value': k}
    #                                             for k, v in dict_proponent.items()],
    #                                 multi=False,
    #                                 value= 'All',
    #                             ),
    #                         ], lg=4)
    #                     ]),
    #                     dbc.Row([
    #                         dbc.Col([
    #                             dcc.Graph(
    #                                 id='stat-plot-year-topic-proponent'
    #                             ),
    #                         ], lg=10),
    #                     ]),
    #
    #
    #                 ])
    #
    # elif pathname in ["/page-4"]:
    #     # if 'data' in globals():
    #     #     del data
    #     # data = load_data()
    #     return html.Div([
    #                     dbc.Row([
    #                         # dbc.Col(lg=1),
    #                         dbc.Col([
    #                             html.H3('Similarity within topics', style={'font-weight': 'bold'}),
    #                             # html.H5('Updata on 14 June 2020'),
    #                             html.P(
    #                                 id="description",
    #                                 children=dcc.Markdown(
    #                                   children=(
    #                                     '''
    #                                     Similarity between two docs in a topic.
    #                                     ''')
    #                                 )
    #                             ),
    #                             html.Br(),
    #                             # html.H6('Number of Proposals by year', style={'font-weight': 'bold'}),
    #                             # dcc.Dropdown(
    #                             #     id='my-dropdown',
    #                             #     options=[{'label': v, 'value': k}
    #                             #                 for k, v in dict_pillar.items()],
    #                             #     multi=False,
    #                             #     value= [0,1,2,3,4,5,6,7,8,9],
    #                             # ),
    #                         ], lg=10),
    #                     ]),
    #                     dbc.Row([
    #                         dbc.Col([
    #                             html.Label('Select Topic:'),
    #                             dcc.Dropdown(
    #                                 id='plot-year-dropdown-pillar1',
    #                                 options=[{'label': v, 'value': k}
    #                                             for k, v in dict_topic.items()],
    #                                 multi=False,
    #                                 value= 'COT',
    #                             ),
    #                         ], lg=4),
    #                         # dbc.Col([
    #                         #     html.Label('Select Proponent:'),
    #                         #     dcc.Dropdown(
    #                         #         id='plot-year-dropdown-proponent1',
    #                         #         options=[{'label': v, 'value': k}
    #                         #                     for k, v in dict_proponent.items()],
    #                         #         multi=False,
    #                         #         value= 'All',
    #                         #     ),
    #                         # ], lg=4)
    #                     ]),
    #                     dbc.Row([
    #                         # dbc.Col(lg=1),
    #                         # dbc.Col([
    #                         #     dcc.Graph(
    #                         #         id='top_topics'
    #                         #     ),
    #                         # ], lg=3),
    #                         dbc.Col([
    #                             dcc.Graph(
    #                                 id='plot_year1'
    #                             ),
    #                         ], lg=10),
    #                     ]),
    #                 ])
    #
    #
    # elif pathname in ["/page-5"]:
    #     # return html.H5("Content to be added page 2.")
    #     return html.Div([
    #                     dbc.Row([
    #                         # dbc.Col(lg=1),
    #                         dbc.Col([
    #                             html.H3('WordCloud by topic', style={'font-weight': 'bold'}),
    #                             # html.H5('Updata on 14 June 2020'),
    #                             html.P(
    #                                 id="description",
    #                                 children=dcc.Markdown(
    #                                   children=(
    #                                     '''
    #                                     Word frequency in a topic.
    #                                     ''')
    #                                 )
    #                             ),
    #                             html.Br(),
    #                         ], lg=10),
    #                     ]),
    #                     dbc.Row([
    #                         dbc.Col([
    #                             html.Label('Select Topic:'),
    #                             dcc.Dropdown(
    #                                 id='plot-year-dropdown-pillar2',
    #                                 options=[{'label': v, 'value': k}
    #                                             for k, v in dict_topic.items()],
    #                                 multi=False,
    #                                 value= 'COT',
    #                             ),
    #                         ], lg=4),
    #                     ]),
    #                     dbc.Row([
    #                         dbc.Col([
    #                             dcc.Graph(
    #                                 id='plot_year2'
    #                             ),
    #                         ], lg=10),
    #                     ]),
    #                 ])
    #
    #
    # elif pathname in ["/page-6"]:
    #     return html.Div([
    #                     # html.H1('Title'),
    #                     html.H3('Networks: proposal proponents & document cross reference', style={'font-weight': 'bold'}),
    #                     html.Embed(src = "assets/network_proponent.html", width=850, height=850),
    #                     html.Embed(src = "assets/network_crossreference.html", width=850, height=850)
    #                     ])
    #
    #
    # elif pathname in ["/page-7"]:
    #     return html.Div([
    #                     dbc.Row([
    #                         dbc.Col([
    #                                 html.H3('Term Frequency', style={'font-weight': 'bold'}),
    #                                 html.P(
    #                                     id="description",
    #                                     children=dcc.Markdown(
    #                                       children=(
    #                                         '''
    #                                         Term frequency across time
    #                                         ''')
    #                                     )
    #                                 ),
    #
    #                         ]),
    #
    #                         ]),
    #                     dbc.Row([
    #                             dbc.Col([
    #                                     dbc.Input(id='term-freq-input', value='tariff ams', type='text'),
    #                                     dbc.Button(id='term-freq-button', type='submit', children='Submit', className="mr-2"),
    #                                     html.P(id='term-freq-invalid'),
    #                                     ], lg=6),
    #                             ]),
    #                     dbc.Row([
    #                             dbc.Col([
    #                                     dcc.Graph(
    #                                         id='term-freq-plot'
    #                                         ),
    #                                     # dbc.Button(id='term-freq-button', type='submit', children='Submit', className="mr-2"),
    #                                     ], lg=10),
    #                             ])
    #                     ])
    # elif pathname in ["/page-8"]:
    #     return html.Div([
    #                     dbc.Row([
    #                         dbc.Col([
    #                                 html.H3('TF-IDF keywords', style={'font-weight': 'bold'}),
    #                                 html.P(
    #                                     id="description2",
    #                                     children=dcc.Markdown(
    #                                       children=(
    #                                         '''
    #                                         Keywords based on TF-IDF. Select documents
    #                                         ''')
    #                                     )
    #                                 ),
    #                         ]),
    #
    #                         ]),
    #                     dbc.Row([
    #                             dbc.Col([
    #                                     html.P(id='tfidf-invalid'),
    #                                     dcc.Dropdown(id='tfidf-dropdown',
    #                                                  multi=True,
    #                                                  value=['AIE-1', 'AIE-2','AIE-3','AIE-4','AIE-5'],
    #                                                  placeholder='Select members',
    #                                                  options=[{'label': country, 'value': country}
    #                                                           for country in allfileid]),
    #                                     ],lg=10),
    #                             ]),
    #                     dbc.Row([
    #                             dbc.Col([
    #                                     dcc.Graph(
    #                                         id='tfidf-plot'
    #                                         ),
    #                                     ], lg=10),
    #                             ])
    #                     ])


    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

# Callbacks for interactive pages

# # Page 2 dropdown control
@app.callback(
        [dash.dependencies.Output('results-container', 'children')],
        [dash.dependencies.Input('button-search', 'n_clicks')],
        [dash.dependencies.State('input-search', 'value')]
    )
def display_table(n_clicks, search_str):
    search = text_preprocessing(search_str)
    # print(search_str)
    # search = search_str
    dff = data[data['Text_Proc1'].str.contains(' '+search+' ')][['HSVersions','HSCode', 'HSDesc', 'Alpha', 'Text_Proc1']]

    return html.Div([
            # dbc.Alert(str(len(dff)) + ' papragraphs found for selection criteria: member = "' + dropdown_value_gov_1 + '", search = "' + search_str + '"', color="info"),
            html.Blockquote(' Results for searching: "' + search_str + '"; Total ' + str(len(dff)) + ' found'),
            dash_table.DataTable(
                    id='tab',
                    columns=[
                                {"name": i, "id": i, "deletable": False, "selectable": False} for i in dff.columns if i != 'ID'
                            ],
                    data = dff.to_dict('records'),
                    editable=False,
                    # filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    column_selectable=False,
                    row_selectable=False,
                    row_deletable=False,
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current= 0,
                    page_size= 20,
                    style_cell={
                                'height': 'auto',
                                'minWidth': '20px', 'maxWidth': '500px',
                                'whiteSpace': 'normal',
                                'textAlign': 'left',
                                'verticalAlign': 'top',
                                'fontSize':12,
                                },
                    style_cell_conditional=[
                                {'if': {'column_id': 'Symbol'},
                                 'width': '100px'},
                                {'if': {'column_id': 'Member'},
                                 'width': '70px'},
                                {'if': {'column_id': 'ReportDate'},
                                 'width': '90px'},
                                {'if': {'column_id': 'Topic'},
                                 'width': '200px'},
                                {'if': {'column_id': 'ParaID'},
                                 'width': '40px'},
                                 ]
                )
            ]), #csv_string

















# General modules
@app.callback(
    Output("collapse", "is_open"),
    [Input("toggle", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run_server(debug=True)
