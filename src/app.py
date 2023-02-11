from flask import Flask, request, redirect
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate

app = Flask(__name__)
app.debug = True

# adding configuration for using a sqlite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Creating an SQLAlchemy instance
db = SQLAlchemy(app)

# Settings for migrations
migrate = Migrate(app, db)


class Tag(db.Model):
    id = db.Column(db.Integer, db.Sequence("tag_id_seq", start=1), primary_key=True)
    content = db.Column(db.String(255), unique=True, nullable=False)
    main_page_tag = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"{self.content}"


class TagRelation(db.Model):
    id = db.Column(db.Integer, db.Sequence("tag_relation_id_seq", start=1), primary_key=True)
    parent_tag = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)
    child_tag = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)


@app.route('/')
def index():
    tags = Tag.query.all()
    return render_template('index.html', tags=tags)


@app.route('/add_data')
def add_data():
    return render_template('add_data.html')


# function to add profiles
@app.route('/add', methods=["POST"])
def tag():
    # In this function we will input data from the
    # form page and store it in our database.
    # Remember that inside the get the name should
    # exactly be the same as that in the html
    # input fields
    tag_content = request.form.get("tag_content")

    # create an object of the Profile class of models
    # and store data as a row in our datatable
    if tag_content != '':
        t = Tag(content=tag_content)
        db.session.add(t)
        db.session.commit()
        return redirect('/')
    else:
        return redirect('/')


@app.route('/delete/<int:id>')
def erase(id):
    # deletes the data on the basis of unique id and
    # directs to home page
    data = Tag.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run()