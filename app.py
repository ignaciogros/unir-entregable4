from flask import Flask, render_template

app = Flask(__name__)


@app.get("/")
def hello():
    return render_template("index.html")


if __name__ == "__main__":
    # OBLIGATORIO: 0.0.0.0 para que sea accesible desde fuera del contenedor
    app.run(host="0.0.0.0", port=5000)
