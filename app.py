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

@app.route('/attack')
def attack():
    # Logic for the attack page
    return render_template('attack.html')

if __name__ == '__main__':
    app.run(debug=True)
