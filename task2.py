import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import serial
import time

app = dash.Dash(__name__)

data = {'time': [], 'altitude': []}

# Open the CSV file in write mode
with open(r"C:\Users\Saanvi\Desktop\Arduino IDE\ultrasonic_test\Ultrasonic.csv", 'w', newline='') as file:
    # Write the header row
    file.write("Time,Altitude\n")

app.layout = html.Div(
    [
        html.H2("Real-Time Altitude Measurement"),
        html.Div(id="real-time-value", style={"fontSize": "18px", "marginBottom": "20px"}),
        dcc.Graph(id="live-graph", animate=True),
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
                    # Open the CSV file in append mode and write the data
                    with open(r"Ultrasonic.csv", 'a') as file:
                        file.write(f"{time.strftime('%H:%M:%S')},{altitude}\n")
                  
    except Exception as e:
        print(f"Error reading altitude data: {e}")


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

    return fig, html.Span(f"Latest Altitude: {latest_altitude} feet", style={"fontSize": "1.0in"})

# Define a function to write "User intended break" to the CSV file
def write_user_break():
    with open(r"Ultrasonic.csv", 'a') as file:
        file.write("User intended break\n")

if __name__ == "__main__":
    try:
        app.run(debug=False)
    finally:
        write_user_break()
