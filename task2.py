import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import serial
import time

app = dash.Dash(__name__)

data = {'time': [], 'altitude': []}

app.layout = html.Div(
    [
        html.H2("Real-Time Altitude Measurement"),
        dcc.Graph(id="live-graph", animate=True),
        html.Div(id="real-time-value"),
        dcc.Interval(id="graph-update", interval=1000, n_intervals=0),
    ]
)

def read_altitude_data():
    try:
        with serial.Serial('COM6', 9600, timeout=1) as ser:
            while True:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    timestamp, altitude = line.split(',')
                    data['time'].append(time.strftime("%H:%M:%S"))
                    data['altitude'].append(float(altitude))
                    with open(r"Ultrasonic.csv", 'a') as file:
                        print(time.strftime("%H:%M:%S,"), altitude, file=file)

@app.callback(
    [Output("live-graph", "figure"), Output("real-time-value", "children")],
    [Input("graph-update", "n_intervals")]
)
def update_graph(n):
    read_altitude_data()
    latest_altitude = data['altitude'][-1] if data['altitude'] else "No data"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data['time'],
            y=data['altitude'],
            mode='lines+markers',
            name='Altitude',
        )
    )
    fig.update_layout(
        title='Live Altitude Graph',
        xaxis=dict(title='Time'),
        yaxis=dict(title='Altitude (feet)'),
    )

    return fig, f"Latest Altitude: {latest_altitude} feet"

if __name__ == "__main__":
    app.run_server(debug=False)
