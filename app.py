from flask import Flask

app = Flask(__name__)


@app.get("/")
def hello():
    return "¡Hola! Soy una aplicación desplegada con CI/CD."


if __name__ == "__main__":
    # OBLIGATORIO: 0.0.0.0 para que sea accesible desde fuera del contenedor
    app.run(host="0.0.0.0", port=5000)