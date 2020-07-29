from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/_temp_data.db'

db = SQLAlchemy(app)


class City(db.Model):
    __tablename__ = 'cities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    population = db.Column(db.Integer)

    def serialize(self):

        return {
            'id': self.id, 
            'name': self.name,
            'population': self.population,
        }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return app.send_static_file('about.html')

@app.route('/cities')
def all():

    cities = City.query.all()

    return jsonify(cities=[city.serialize() for city in cities])

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404