from flask import Flask, render_template
import patentexp
app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hello World</h1>'

@app.route('/patent/<patent_number>')
def patent_number(patent_number):
    patent_exp_str = patentexp.patent_term_expire(patent_number)
    return '<p>{}</p>'.format(patent_exp_str)