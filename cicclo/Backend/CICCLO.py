
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'  # Cambia esto a tu base de datos SQL
db = SQLAlchemy(app)

class Empresa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    area = db.Column(db.String(120), unique=True, nullable=False)
    persona = db.Column(db.String(120), unique=True, nullable=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nombre = request.form['nombre']
        area = request.form['area']
        persona = request.form['persona']
        empresa = Empresa(nombre=nombre, area=area, persona=persona)
        db.session.add(empresa)
        db.session.commit()
        return 'Empresa añadida'
    return render_template('index.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)