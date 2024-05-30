#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template

app = Flask(__name__)

# [/]へアクセスがあった場合に、"title.html"を返す
@app.route('/')
def index():
    return render_template('title.html') #htmlファイルの表示

# [/]へアクセスがあった場合、"main.html"を返す
@app.route('/main')
def main():
    return render_template('main.html')

# [/]へアクセスがあった場合、"check.html"を返す
@app.route('/check')
def check():
    return render_template('check.html')

# [/]へアクセスがあった場合、"intro.html"を返す
@app.route('/introduction')
def intro():
    return render_template('intro.html')

# [/]へアクセスがあった場合、"demo.html"を返す
@app.route('/demonstration')
def demo():
    return render_template('demo.html')

# [/]へアクセスがあった場合、"play.html"を返す
@app.route('/play')
def exp():
    return render_template('play.html')

# [/]へアクセスがあった場合、"result1.html"を返す
@app.route('/result1')
def result1():
    return render_template('result1.html')

# [/]へアクセスがあった場合、"result2.html"を返す
@app.route('/result2')
def result2():
    return render_template('result2.html')

# [/]へアクセスがあった場合、"result3.html"を返す
@app.route('/result3')
def result3():
    return render_template('result3.html')

# [/]へアクセスがあった場合、"result4.html"を返す
@app.route('/result4')
def result4():
    return render_template('result4.html')

# [/]へアクセスがあった場合、"score.html"を返す
@app.route('/score')
def score():
    return render_template('score.html')

# [/]へアクセスがあった場合、"end.html"を返す
@app.route('/end')
def end():
    return render_template('end.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
