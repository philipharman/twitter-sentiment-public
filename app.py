# Reference: https://github.com/plotly/dash-sample-apps/tree/master/apps/dash-uber-rides-demo
# A great video/YouTube account for Dash: https://www.youtube.com/watch?v=hSPmj7mK6ng

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import numpy as np

from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt
import plotly.express as px
import plotly.io as pi
import os

external_stylesheets = [dbc.themes.BOOTSTRAP]

# Instantiate app
app = dash.Dash(
   __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}], external_stylesheets=external_stylesheets
)

app.title = "Twitter Sentiment"
server = app.server


# Mapbox token - make a free accout at Mapbox.com to get yours.
mapbox_access_token = open("mapbox_token.txt").read()

# Initialize data frame + important lists
data = pd.read_csv('data/prepped_data.csv')
continents = data.Continent.unique()
countries = data.Country.unique()
brands = data.Brand.unique()

# App layout
app.layout = html.Div(
    style = {'padding' : 20, 'background-color':"black", 'height':750, 'width':1200},
    children = [
        dbc.Row(
            [
                # Control Panel and Histogram
                dbc.Col(
                    html.Div(
                        [
                            # Control Panel
                            #Intro text
                            html.H2("Twitter Sentiment", style = {'color':'white'}),
                            html.P('Filter by Brand and Continent below.', style = {'color':'white'}),
                            
                            # Brand dropdown
                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id = 'brand-dropdown',
                                        options=[
                                            {'label': i, 'value': i}
                                            for i in brands
                                        ],
                                        multi = True,
                                        placeholder = 'Select a brand.',
                                        style = {'width':'100%', 'display':'inline-block'}
                                    )
                                ]
                            ),
                            
                            # Continent dropdown
                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id = 'continent-dropdown',
                                        options=[
                                            {'label': i, 'value': i}
                                            for i in continents
                                        ],
                                        multi = True,
                                        placeholder = 'Select a continent.',
                                        style = {'width':'100%', 'display':'inline-block'}
                                    )
                                ]
                            ),
                            
                            html.Br(), # line break
                            
                            # Histogram
                            html.Div(
                                children = [
                                    html.P('Sentiment Distribution', style = {'color':'white'}),
                                    html.Div(
                                        className = "eight columns div-for-charts bg-grey",
                                        children = [
                                            dcc.Graph(id = 'histogram', style = {'height' : 204})
                                        ]
                                    )
                                ]
                            )
                        ]
                    ), width = 4 
                ),
                
                dbc.Col(
                    
                    # Map objects
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.P('Mapped Sentiment', style = {'color':'white'}),
                                    dcc.Graph(id = "map", style = {'height': 400, 'width':'auto'})
                                ]
                            )
                        ]
                    ), 
                )
            ]
        ),
    
        # Country volumes
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.Div(
                            [
                                html.Br(), # line break
                                html.P('Activity by Country (no. Tweets)', style = {'color':'white'}),
                                dcc.Graph(id = 'country-volume', style = {'height': 200})#,style = {'width':'autp', 'display':'inline-block'})
                            ]
                        )
                    ]
                )
            )
        )
    ]
)

# Define color vals
colorVal = [
        "#80E41D",
        "#66E01F",
        "#4CDC20",
        "#26CC58",
        "#28C86D",
        "#29C481",
        "#2C99B4",
        "#2D7EB0",
        "#2D65AC",
        "#2E4EA4",
        "#2E38A4"
    ]


# Update Figures based on brand and/or continent
@app.callback(
    [Output("histogram", "figure"), Output("map","figure"), 
     Output("country-volume","figure")],
    [Input("brand-dropdown", "value"), Input("continent-dropdown", "value")],
)

def update(brand, continent):
    
    # Filter data by selection
    df = data.copy()
    if brand != None and brand != []:
        boolean = df.Brand.isin(brand)
        df = df[boolean]
    if continent != None and continent != []:
        boolean = df.Continent.isin(continent)
        df = df[boolean]
        
    
    ######################################################################
    # Histogram setup
    ######################################################################
    xVal = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5] 
    yVal = []
    for x in xVal:
        yVal.append(len(df[df.Sentiment == x]))
    
    # Layout
    layout = go.Layout(
    bargap=0.01,
    bargroupgap=0,
    barmode="group",
    margin=go.layout.Margin(l=10, r=0, t=0, b=25),
    showlegend=False,
    plot_bgcolor="#323130",
    paper_bgcolor="#323130",
    dragmode="select",
    font=dict(color="white"),
    xaxis=dict(
        range=[-5.5, 6],
        showgrid=False,
        fixedrange=True,
    ),
    yaxis=dict(
        range=[0, max(yVal) + max(yVal) / 4],
        showticklabels=False,
        showgrid=False,
        fixedrange=True,
        rangemode="nonnegative",
        zeroline=False,
    ),
    annotations=[
        dict(
            x=xi,
            y=yi,
            text=str(yi),
            xanchor="center",
            yanchor="bottom",
            showarrow=False,
            font=dict(color="white"),
        )
        for xi, yi in zip(xVal, yVal)
    ],
)
    # Defining the figure
    hist = go.Figure(
        data=[
            go.Bar(x=xVal, y=yVal, marker=dict(color=colorVal), hoverinfo="x"),
            go.Scatter(
                opacity=0,
                x=xVal,
                y=yVal,
                hoverinfo="none",
                mode="markers",
                marker=dict(color="rgb(66, 134, 244, 0)", symbol="square", size=40),
                visible=True,
            ),
        ],
        layout=layout,
    )
    
    
    ######################################################################
    # Map setup
    ######################################################################
    sentimap = go.Figure(
        data=[
            Scattermapbox(
                lat=df.Latitude,
                lon=df.Longitude,
                mode="markers",
                marker=dict(
                    showscale=True,
                    colorscale = colorVal,
                    opacity=0.5,
                    size=5.0,
                    color = df.Sentiment,
                    colorbar=dict(
                        title="Sentiment",
                        x=0.93,
                        xpad=0,
                        nticks=11,
                        tickfont=dict(color="#d8d8d8"),
                        titlefont=dict(color="#d8d8d8"),
                        thicknessmode="pixels",
                    ),
                ),
            ),
        ],
        layout=Layout(
            autosize=True,
            margin=go.layout.Margin(l=1, r=1, t=1, b=1),
            showlegend=False,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                style="dark",
                zoom = 0.7,
                center=dict(lat=20, lon=0)
            ),
            updatemenus=[
                dict(
                    buttons=(
                        [
                            dict(
                                args=[
                                    {
                                        "mapbox.zoom": 0.7,
                                        "mapbox.style": "dark",
                                    }
                                ],
                                label="Reset Zoom",
                                method="relayout",
                            )
                        ]
                    ),
                    direction="left",
                    pad={"r": 0, "t": 0, "b": 0, "l": 0},
                    showactive=False,
                    type="buttons",
                    x=0.45,
                    y=0.02,
                    xanchor="left",
                    yanchor="bottom",
                    bgcolor="#323130",
                    borderwidth=1,
                    bordercolor="#6d6d6d",
                    font=dict(color="#FFFFFF"),
                )
            ],
        ),
    )

 
    ######################################################################
    # Country histogram setup
    ######################################################################
    
    # Generate ordered dataframe of highest-traffic countries (top 20)
    # And get average sentiment in each
    grouped = df.copy()
    grouped['Count'] = 1
    grouped = grouped[['Country','Count']].groupby('Country').sum()
    grouped['Sentiment'] = df[['Country','Sentiment']].groupby('Country').mean()
    grouped = grouped.sort_values('Count', ascending = False).head(20)
    
    # Country, count, sentiment
    xVal = grouped.index
    yVal = grouped.Count
    senti = grouped.Sentiment
    
    # Layout
    layout = go.Layout(
    bargap=0.1,
    bargroupgap=0,
    barmode="group",
    margin=go.layout.Margin(l=10, r=0, t=0, b=50),
    showlegend=False,
    plot_bgcolor="#323130",
    paper_bgcolor="#323130",
    dragmode="select",
    font=dict(color="white"),
    xaxis=dict(
        showgrid=False,
        fixedrange=True,
    ),
    yaxis=dict(
        range=[0, max(yVal) + max(yVal) / 4],
        showticklabels=False,
        showgrid=False,
        fixedrange=True,
        rangemode="nonnegative",
        zeroline=False,
    ),
    annotations=[
        dict(
            x=xi,
            y=yi,
            text=str(yi),
            xanchor="center",
            yanchor="bottom",
            showarrow=False,
            font=dict(color="white"),
        )
        for xi, yi in zip(xVal, yVal)
    ],
)
    # Defining the figure
    countryhist = go.Figure(
        data=[
            go.Bar(x=xVal, y=yVal, marker=dict(color= "#29C481" )),
            go.Scatter(
                opacity=0,
                x=xVal,
                y=yVal,
                hoverinfo="none",
                mode="markers",
                marker=dict(color="rgb(66, 134, 244, 0)", symbol="square", size=40),
                visible=True,
            ),
        ],
        layout=layout,
    )

    return hist, sentimap, countryhist
    

if __name__ == "__main__":
    app.run_server(debug = True)
   # app.run_server(host="0.0.0.0", port = os.environ['PORT'], debug=False)
