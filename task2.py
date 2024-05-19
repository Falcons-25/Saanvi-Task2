import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
from dash.dash import no_update
from dash_daq import StopButton
import plotly.graph_objs as go
import serial
import threading
import time
import signal
import sys

app = dash.Dash(__name__)

data = {'time': [], 'altitude': []}
reading_data = True  # Flag to control whether to read altitude data or not

# Open the CSV file in write mode
with open("Ultrasonic.csv", 'w', newline='') as file:
    # Write the header row
    file.write("Time,Altitude\n")

lock = threading.Lock()

def read_altitude_data(port: str, baudrate: int) -> None:
    global ser, reading_data
    ser = serial.Serial(port=port, baudrate=baudrate)
    try:
        while reading_data:
            line = ser.readline().decode().strip()
            if line:
                timestamp, altitude = line.split(',')
                with lock:
                    data['time'].append(time.strftime("%H:%M:%S"))
                    data['altitude'].append(float(altitude))
                # Open the CSV file in append mode and write the data
                with open("Ultrasonic.csv", 'a') as file:
                    file.write(f"{time.strftime('%H:%M:%S')},{altitude}\n")
    except serial.serialutil.SerialException:
        print("Arduino disconnected.")
        with open("Ultrasonic.csv", 'a') as file:
            file.write("Arduino disconnected.\n")
    except KeyboardInterrupt:
        print("User terminated operation.")
        with open("Ultrasonic.csv", 'a') as file:
            file.write("User terminated operation.\n")
    finally:
        if hasattr(ser, 'is_open') and ser.is_open:
            ser.close()

def stop_reading_data(n_clicks):
    global reading_data
    if n_clicks:
        reading_data = False
        with open("Ultrasonic.csv", 'a') as file:
            file.write("User terminated operation.\n")

@app.callback(
    Output("live-graph", "figure"),
    [Input("interval-component", "n_intervals")],
    [State("stop-button", "n_clicks")]
)
def update_graph_and_value(n_intervals, stop_clicks):
    if stop_clicks:
        raise dash.exceptions.PreventUpdate
    else:
        with lock:
            time_data = data['time']
            altitude_data = data['altitude']
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=time_data,
                y=altitude_data,
                name='Altitude',
                mode='lines+markers',
                type='scatter'
            )
        )
        return fig

@app.callback(
    Output("real-time-value", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_altitude_value(n):
    style = {"padding": "15px", "fontSize": "60px"}
    with lock:
        current_altitude = data['altitude'][-1] if data['altitude'] else "No data"
    return html.Span(f'Altitude: {current_altitude}ft', style=style)

@app.callback(
    Output("stop-button", "n_clicks"),
    [Input("stop-button", "n_clicks")],
    [State("stop-button", "n_clicks")]
)
def stop_reading_data_callback(n_clicks, current_n_clicks):
    stop_reading_data(n_clicks)
    return current_n_clicks

app.layout = html.Div([
    html.Div([
        html.H4("Arduino Live Data Feed"),
        html.Div(id="real-time-value"),
        dcc.Graph(id="live-graph"),
        dcc.Interval(id="interval-component", interval=1000, n_intervals=0),
    ]),
    StopButton(id="stop-button", n_clicks=0),
])

def write_user_break():
    with open("Ultrasonic.csv", 'a') as file:
        file.write("User intended break\n")

def signal_handler(sig, frame):
    global reading_data
    reading_data = False
    write_user_break()
    sys.exit(0)

if __name__ == "__main__":
    port = "COM6"
    baudrate = 9600

    signal.signal(signal.SIGINT, signal_handler)

    thread_serial = threading.Thread(target=read_altitude_data, args=(port, baudrate))
    thread_serial.start()

    try:
        app.run(debug=False)
    finally:
        reading_data = False
        thread_serial.join()
        write_user_break()
