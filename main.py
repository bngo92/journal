from flask import Flask, request, url_for
from flask.templating import render_template
from flask.ext.bootstrap3 import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.utils import redirect

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    achievements = db.relationship('Achievement', backref='category', lazy='dynamic')

    def __init__(self, name):
        self.name = name
        db.session.add(self)
        db.session.commit()

    def progress(self):
        completed_achievements = self.achievements.filter_by(completed=True).count()
        total_achievements = self.achievements.count()
        return completed_achievements, total_achievements

    def progress_percent(self):
        completed_achievements, total_achievements = self.progress()
        return completed_achievements * 100 // total_achievements


class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    heading = db.Column(db.String(80))
    body = db.Column(db.String(80))
    completed = db.Column(db.Boolean)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    def __init__(self, heading, body, category_id, completed=False):
        self.heading = heading
        self.body = body
        self.completed = completed
        self.category_id = category_id
        db.session.add(self)
        db.session.commit()

    @classmethod
    def all_progress(cls):
        completed_achievements = cls.query.filter_by(completed=True).count()
        total_achievements = cls.query.count()
        return completed_achievements, total_achievements

db.drop_all()
db.create_all()

category = Category('Health')
Achievement("Run a 5k", "", category.id)
Achievement("Row 7500m", "", category.id)
category = Category('Life')
Achievement("Get a job", "Offer has been signed", category.id, completed=True)
#Achievement("Roast a chicken", "", category.id)
category = Category('Work')
Achievement("Finish intended topology", "", category.id)
Achievement("Finish performance review", "", category.id)
category = Category('Angela')
Achievement("Ask Angela out", "Ask Angela out", category.id, completed=True)
Achievement("Plan an adventure", "", category.id)
Achievement("Make a scrapbook", "", category.id)


@app.route('/')
def index():
    return render_template("index.html", categories=Category.query.all(), achievements=Achievement.query.filter_by(completed=True))


@app.route('/category/<category_id>')
def category(category_id):
    return render_template("category.html", categories=Category.query.all(), category=Category.query.get(category_id))


@app.route('/achievement/<achievement_id>')
def achievement(achievement_id):
    return render_template("achievement.html", categories=Category.query.all(), achievement=Achievement.query.get(achievement_id))


@app.route('/add', methods=['POST'])
def add():
    print(request)
    heading = request.form['heading']
    body = request.form['body']
    db.session.add(Achievement(heading, body))
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()