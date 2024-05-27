
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template

app = Flask(__name__, static_folder = './templates/images2')

# [/]へアクセスがあった場合に、"page1.html"を返す
@app.route('/')
def index():
    return render_template('test.html') #htmlファイルの表示

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
