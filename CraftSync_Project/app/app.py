#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template

app = Flask(__name__)

# [/]へアクセスがあった場合に、"page1.html"を返す
@app.route('/')
def index():
    return render_template('page1.html') #htmlファイルの表示

# [/]へアクセスがあった場合、"page2.html"を返す
@app.route('/introduction')
def introduction():
    return render_template('page2.html')

# [/]へアクセスがあった場合、"page3.html"を返す
@app.route('/check')
def check():
    return render_template('page3.html')

# [/]へアクセスがあった場合、"page4.html"を返す
@app.route('/select')
def select():
    return render_template('page4.html')

# [/]へアクセスがあった場合、"page5.html"を返す
@app.route('/model')
def model():
    return render_template('page5.html')

# [/]へアクセスがあった場合、"page6.html"を返す
@app.route('/experience')
def experience():
    return render_template('page6.html')

# [/]へアクセスがあった場合、"page7.html"を返す
@app.route('/result1')
def result1():
    return render_template('page7.html')

# [/]へアクセスがあった場合、"page8.html"を返す
@app.route('/result2')
def result2():
    return render_template('page8.html')

# [/]へアクセスがあった場合、"page9.html"を返す
@app.route('/result3')
def result3():
    return render_template('page9.html')

# [/]へアクセスがあった場合、"page10.html"を返す
@app.route('/result4')
def result4():
    return render_template('page10.html')

# [/]へアクセスがあった場合、"page11.html"を返す
@app.route('/score')
def score():
    return render_template('page11.html')

# [/]へアクセスがあった場合、"page12.html"を返す
@app.route('/end')
def end():
    return render_template('page12.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
