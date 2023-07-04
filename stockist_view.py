import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc
from dash import html

df = pd.read_csv('https://raw.githubusercontent.com/priyam-g/AgrEco_Stockist/main/Stockists_data.csv')
df=df.sort_values('Product')
total_sales = df.groupby('Product')["Net Profit"].sum()

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H1("Stockist's View"),
    html.Label("Select a Product:"),
    dcc.Dropdown(
        id='product-dropdown',
        options=[{'label': 'Total', 'value': 'Total'}] + [{'label': p, 'value': p} for p in df['Product'].unique()],
        value=df['Product'].unique()[0],
        style={'width': '40%'}
    ),
    html.Label("Select a Metric:"),
    dcc.Dropdown(
        id='metric-dropdown',
        options=[
            {'label': 'Net Revenue', 'value': 'Net Revenue'},
            {'label': 'Net Profit', 'value': 'Net Profit'}
        ],
        value='Net Revenue',
        style={'width': '40%'}
    ),
    dcc.Graph(id='circle-plot'),

    dcc.Graph(
        id='pie-chart1',
        figure={
            'data': [go.Pie(labels=total_sales.index, values=total_sales.values, textinfo='label+percent')],
            'layout': go.Layout(
                title="Total Profit by Product",
                showlegend=False,
                font=dict(
                    size=12  # Adjust the font size as per your preference
                )
            )
        }
    ),
    html.Div(id='pie-charts-container')
])

# # Adjust the figure size to accommodate the text
# app.config['displayModeBar'] = False
# app.run_server(debug=True)




@app.callback(
    dash.dependencies.Output('circle-plot', 'figure'),
    [dash.dependencies.Input('product-dropdown', 'value'),
     dash.dependencies.Input('metric-dropdown', 'value')]
)
def update_circle_plot(selected_product, selected_metric):
    if selected_product == 'Total':
        total_sales = df.groupby('Pincode')[selected_metric].sum()
        filtered_df = df.merge(total_sales, on='Pincode', suffixes=('', '_Total'))
        fig = px.scatter_mapbox(
            filtered_df,
            lat="Lat",
            lon="Long",
            hover_name="Pincode",
            hover_data=None,
            zoom=5,
            center=dict(lat=df['Lat'].mean(), lon=df['Long'].mean()),
            mapbox_style="open-street-map",
            color=f"{selected_metric}_Total",
            color_continuous_scale="RdYlGn",
            size_max=50
        )

        fig.update_traces(
            customdata=filtered_df[['Pincode', 'Product', f"{selected_metric}_Total"]].values,
            hovertemplate="<b>%{customdata[0]}</b><br>" +
                         "Pincode: %{customdata[0]}<br>" +
                          "Product: %{customdata[1]}<br>" +
                          f"{selected_metric} (Total): %{{customdata[2]:.2f}}<br>",
            marker=dict(
            size=15  # Increase the size of the markers
            )
        )
    else:
        filtered_df = df[df['Product'] == selected_product]
        fig = px.scatter_mapbox(
        filtered_df,
        lat="Lat",
        lon="Long",
        hover_name="Pincode",
        hover_data=None,
        zoom=5,
        center=dict(lat=filtered_df['Lat'].mean(), lon=filtered_df['Long'].mean()),
        mapbox_style="open-street-map",
        color=selected_metric,
        color_continuous_scale="RdYlGn",
        size_max=50
        )

        fig.update_traces(
        customdata=filtered_df[['Pincode', 'Product', selected_metric]].values,
        hovertemplate="<b>%{customdata[0]}</b><br>" +
                      "Pincode: %{customdata[0]}<br>" +
                      "Product: %{customdata[1]}<br>" +
                      f"{selected_metric}: %{{customdata[2]:.2f}}<br>",
        marker=dict(
        size=15  # Increase the size of the markers
        )
        )

    return fig

@app.callback(
    dash.dependencies.Output('pie-charts-container', 'children'),
    [dash.dependencies.Input('pie-chart1', 'clickData'),
    dash.dependencies.State('pie-charts-container', 'children')]
)
def generate_pie_charts(click_data, children):
    if click_data is not None:
        clicked_label = click_data['points'][0]['label']
        filtered_data = df[df['Product'] == clicked_label]
        filtered_data['Pincode'] = pd.to_numeric(filtered_data['Pincode'])
        column_names = ['Number of Units', 'Net Revenue', 'Net Profit']  # Replace with your actual column names
        pie_charts = []
        for column_name in column_names:
            pie_data = filtered_data.groupby('Pincode')[column_name].sum()
            pie_data = pie_data.astype(str).sort_index()
            pie_chart = dcc.Graph(
                id=f'pie-chart-{column_name}',
                figure={
                    'data': [go.Pie(
                        labels=pie_data.index,
                        values=pie_data.values,
                        textinfo='none',
                        hoverinfo='label+percent',
                        sort=False,
                        marker=dict(line=dict(color='#000000', width=1))
                    )],
                    'layout': go.Layout(
                        title=f"{clicked_label}- {column_name}",
                        showlegend=False,
                        font=dict(
                            size=9  # Adjust the font size as per your preference
                        ),
                        autosize=False,
                        width=300,  # Adjust the width of each pie chart as per your preference
                        height=300,  # Adjust the height of each pie chart as per your preference
                        margin=dict(l=10, r=10, t=30, b=10),  # Adjust the margins as per your preference
                    )
                }
            )
            pie_charts.append(pie_chart)
        return html.Div(
            children=pie_charts,
            style={'display': 'flex', 'justify-content': 'space-between', 'width': '100%'}
        )
    return children

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
