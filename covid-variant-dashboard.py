"""
Author: Josh Stine
Date Created: 10/28/2021

resources used:
https://github.com/Coding-with-Adam/Dash-by-Plotly/tree/master/Dash%20Components/Dropdown
https://www.youtube.com/watch?v=UYH_dNSX1DM
"""

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas
import plotly.graph_objects as go

# import and transform the data for the way we need it in order to create the dashboard
colors = ["001219","005f73","0a9396","94d2bd","e9d8a6","ee9b00","ca6702","bb3e03","ae2012","E2797D"]

variants = ['Beta','Alpha','Gamma','Delta','Kappa','Epsilon','Eta','Iota','Lambda','others']
covid_variant_data = pandas.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/variants/covid-variants.csv')
covid_variant_data = covid_variant_data[covid_variant_data['variant'].isin(variants)]
countries = covid_variant_data['location'].unique()

covid_case_data = pandas.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/jhu/full_data.csv')
covid_case_data = covid_case_data[covid_case_data['location'].isin(countries)]

vaccination_data = pandas.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv')
vaccination_data = vaccination_data[vaccination_data['location'].isin(countries)]

# dictionary for dropdown list
country_dict = []
for country in countries:
    country_dict.append({'label': country, 'value': country})

# create the dashboard as an app and initialize server
app = dash.Dash(__name__)
server = app.server

"""HTML Layout of the app"""
app.layout = html.Div([
    # div for dropdown
    html.Div([
        html.Br(),
        html.Div(id='country_data'),
        html.Br(),
        html.Label(['Choose Country:'], style={'font-weight': 'bold','text-align': 'center'}),
        dcc.Dropdown(id='country_dropdown',
                     options=country_dict,
                     optionHeight=35,
                     value='United States',
                     disabled=False,
                     multi=False,
                     searchable=True,
                     search_value='United States',
                     placeholder='Please select a Country',
                     clearable=True,
                     style={'width':'50%', 'align':'right', 'padding-left':'5px'})
    ]),
    # div for graphs
    html.Div([
        html.Div(dcc.Graph(id='covid_variant_graph')),
        html.Div(
            children=dcc.Graph(id='covid_case_graph'),
            className='variant_graph',
            style={
                'width':'50%', 'display':'inline-block'
            }
        ),
        html.Div(
            children=dcc.Graph(id='covid_vaccination_graph'),
            className='vaccination_graph',
            style={
                'width':'50%', 'display':'inline-block'
            }

        )
    ]),
    # div for data source
    html.Div([
        html.Span(['Data Source: '], style={'font-size': '16px', 'font-weight':'bold'}),
        html.A('https://github.com/owid/covid-19-data/blob/master/public/data/',
               href='https://github.com/owid/covid-19-data/blob/master/public/data/'
               , target='_blank'),
        html.Br(),
        html.P('*** These charts are sourced directly from the repository so they will update when new data is uploaded ***'
               , style={'font-size':'12px', 'font-weight':'bold'})
    ])
])

"""Interactive functionality of the app"""
# connect the dropdown to the variant graph
@app.callback(
    Output(component_id='covid_variant_graph', component_property='figure'),
    [Input(component_id='country_dropdown', component_property='value')]
)
def build_variant_chart(country):
    # select subset of data based on country and add trace lines for each variant
    country_variant_data = covid_variant_data[covid_variant_data['location']==country]
    trace_lines = []
    for index, variant in enumerate(variants):
        # create a subset of data by variant
        variant_data = country_variant_data[country_variant_data['variant']==variant]
        # sum the data by date in case there are any duplicates
        variant_data_sum = variant_data.groupby(country_variant_data['date']).sum()
        # add date back in as a column since it moves to index with .groupby()
        variant_data_sum.reset_index(level=0, inplace=True)
        # add back in the country and variant columns since .sum() drops all non numerics
        variant_data_sum['location'] = country
        variant_data_sum['variant'] = variant
        trace = go.Scatter(
                x=variant_data_sum['date'],
                y=variant_data_sum['num_sequences'],
                name=variant,
                fill='tonexty',
                stackgroup=index,
                line=dict(color="#"+colors[index])
        )
        trace_lines.append(trace)
    layout = dict(
            title=country + ' COVID Variant Trends',
            annotations=[
                go.layout.Annotation(
                    text='Double-click on legend item to isolate<br>Single-click to remove from plot',
                    align='left',
                    bordercolor='black',
                    borderwidth=1.5,
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=1,
                    y=1.15
                ),
                go.layout.Annotation(
                    text='Slide dates on x-axis to update chart zoom',
                    align='left',
                    bordercolor='black',
                    borderwidth=1.5,
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=1,
                    y=-0.25
                )
            ]
    )
    fig = go.Figure(data=trace_lines, layout=layout)
    fig.update_layout(title_font_size=24, title_x=0.5)
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Number of Sequences')
    return fig


# connect the dropdown to the case graph
@app.callback(
    Output(component_id='covid_case_graph', component_property='figure'),
    [Input(component_id='country_dropdown', component_property='value')]
)
def build_case_chart(country):
    country_case_data = covid_case_data[covid_case_data['location']==country]
    country_case_data_sum = country_case_data.groupby(country_case_data['date']).sum()
    country_case_data_sum.reset_index(level=0, inplace=True)
    country_case_data_sum['location'] = country
    new_cases = go.Scatter(
            x=country_case_data_sum['date'],
            y=country_case_data_sum['new_cases'],
            name=country,
            fill='tonexty',
            stackgroup=0,
            line=dict(color="#"+colors[1])
    )
    layout = dict(
            title=country + ' COVID New Case Trends'
        )
    fig = go.Figure(data=new_cases, layout=layout)
    fig.update_layout(title_font_size=24, title_x=0.5)
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Number of New Cases')
    return fig


# connect the dropdown to the vaxx graph
@app.callback(
    Output(component_id='covid_vaccination_graph', component_property='figure'),
    [Input(component_id='country_dropdown', component_property='value')]
)
def build_vaccination_chart(country):
    country_vax_data = vaccination_data[vaccination_data['location']==country]
    country_vax_data_sum = country_vax_data.groupby(country_vax_data['date']).sum()
    country_vax_data_sum.reset_index(level=0, inplace=True)
    country_vax_data_sum['location'] = country
    people_vaccinated = go.Scatter(
            x=country_vax_data_sum['date'],
            y=country_vax_data_sum['people_vaccinated_per_hundred'],
            name='People<br>Vaccinated<br>per 100',
            fill='tonexty',
            stackgroup=0,
            line=dict(color="#"+colors[4])
    )
    people_fully_vaccinated = go.Scatter(
        x=country_vax_data_sum['date'],
        y=country_vax_data_sum['people_fully_vaccinated_per_hundred'],
        name='People Fully<br>Vaccinated<br>per 100<br>',
        fill='tonexty',
        stackgroup=1,
        line=dict(color="#" + colors[3])
    )
    layout = dict(
            title=country + ' COVID Vaccination Trends'
        )
    fig = go.Figure(data=[people_vaccinated, people_fully_vaccinated], layout=layout)
    fig.update_layout(title_font_size=24, title_x=0.5)
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Number of Vaccinations per 100 People')
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
