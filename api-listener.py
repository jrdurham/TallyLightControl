from flask import Flask, request, Response

# Simple Flask app to mimic the Kuando busylight's HTTP API for
# testing the main script.

app = Flask(__name__)

@app.route('/', methods=['GET'])
def handle_request():
    action = request.args.get('action')
    green = request.args.get('green')
    red = request.args.get('red')
    
    if action not in ['light', 'blink']:
        return respond("UNKNOWN COMMAND")
    
    return respond("OK")

def respond(msg):
    msg_str = str(f"{msg}")
    # The busylight HTTP API returns a JSON response in plaintext format.
    return Response(f'{{ "response": "{msg_str}"}}', content_type='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8989)
