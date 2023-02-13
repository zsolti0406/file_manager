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
    index_tag = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"{self.content}"


class TagRelation(db.Model):
    id = db.Column(db.Integer, db.Sequence("tag_relation_id_seq", start=1), primary_key=True)
    parent_tag = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)
    child_tag = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)
    def __repr__(self):
        return f"{self.id} {self.parent_tag} {self.child_tag}"


@app.route('/')
def index():
    tags = Tag.query.filter_by(index_tag=True)
    return render_template('index.html', tags=tags)


@app.route('/browser/<int:id>')
def browser(id):
    child_tag_ids = TagRelation.query.with_entities(TagRelation.child_tag).filter(TagRelation.parent_tag == id).all()

    ids = set()
    for set_in_list in child_tag_ids:
        for element in set_in_list:
            ids.add(element)

    child_tags = Tag.query.filter(Tag.id.in_(ids)).all()

    browser_object = []
    for child_tag in child_tags:
        element = {'tag': child_tag}
        if len(TagRelation.query.filter_by(parent_tag=child_tag.id).all()):
            element['has_subtag'] = True
        else:
            element['has_subtag'] = False
        browser_object.append(element)

    return render_template('browser.html', browser_object=browser_object)


@app.route('/tags')
def tags():
    tags = Tag.query.all()
    return render_template('tags.html', tags=tags)


@app.route('/add_tag', methods=["POST"])
def add_tag():
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
        return redirect('/tags')
    else:
        return redirect('/tags')


@app.route('/make_index_tag/<int:id>')
def make_index_tag(id):
    tag = Tag.query.get(id)
    tag.index_tag = True
    db.session.commit()
    return redirect('/tags')




@app.route('/delete_tag/<int:id>')
def delete_tag(id):
    # deletes the data on the basis of unique id and
    # directs to home page
    data = Tag.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect('/tags')


@app.route('/tag_relations')
def tag_relations():
    tags = Tag.query.all()
    tag_relations = TagRelation.query.all()
    return render_template('tag_relations.html', tags=tags, tag_relations=tag_relations)


@app.route('/add_tag_relation', methods=["POST"])
def add_tag_relation():
    parent_tag_content = request.form.get("parent_tag")
    child_tag_content = request.form.get("child_tag")
    parent_tag = Tag.query.filter_by(content=parent_tag_content).first()
    child_tag = Tag.query.filter_by(content=child_tag_content).first()
    tag_relation = TagRelation(parent_tag=parent_tag.id, child_tag=child_tag.id)
    db.session.add(tag_relation)
    db.session.commit()
    return redirect('/tag_relations')

@app.route('/delete_tag_relation/<int:id>')
def delete_tag_relation(id):
    # deletes the data on the basis of unique id and
    # directs to home page
    data = TagRelation.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect('/tag_relations')




if __name__ == '__main__':
    app.run()