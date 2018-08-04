from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import patentexp

#DEBUG = True
app = Flask(__name__)
app.config['SECRET_KEY'] = '888' 

class ReusableForm(Form):
    patent = TextField('Patent number:', validators=[validators.required()])


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ReusableForm(request.form)
    

    print(form.errors)
    if request.method == 'POST':
        patent=request.form['patent']
        patent_exp_str = patentexp.patent_term_expire(patent)
        print(patent)

        if form.validate():
            # Save the coment here.
            flash(patent_exp_str)
        else:
            flash('All the form fields are required. ')
    return render_template('index.html', form=form)

@app.route('/patent/<patent_number>')
def patent_number(patent_number):
    patent_exp_str = patentexp.patent_term_expire(patent_number)
    return '<p>{}</p> <p>Patent term disclaimer and patent term extension based on regulatory review is not supported.'.format(patent_exp_str)

