from dash import Dash, html
from components import map_column

app = Dash()

app.layout = html.Div(
    style={
        'display': 'grid',
        'gridTemplateColumns': '20% 50% 30%',
        'height': '100vh',
        'boxSizing': 'border-box',
    },
    children=[
        html.Div("Filters (20%)"),
        map_column.render(),
        html.Div("Details (30%)"),
    ]
)

if __name__ == '__main__':
    app.run(debug=True)
