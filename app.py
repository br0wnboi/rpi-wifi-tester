from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/config", methods=["GET", "POST"])
def config():
    result = False
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

        try:
            subprocess.run(command, check=True)
            result = True
        except Exception as error:
            print(error)
            result = False
    return render_template("config.html", context={"result": result})


@app.route("/status")
def status():
    # Logic to retrieve the current status of the wireless adapter
    # Capture the output and pass it to the template
    adapter_status = "Monitor mode"
    return render_template("status.html", adapter_status=adapter_status)


@app.route("/attack")
def attack():
    # Logic for the attack page
    return render_template("attack.html")


if __name__ == "__main__":
    app.run(debug=True)
