from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/python")
def hello_world():
    return jsonify({"message": "Hello from CVForge Flask API!"})

if __name__ == "__main__":
    app.run()
