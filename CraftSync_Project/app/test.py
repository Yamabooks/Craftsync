import os
from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

# Excelファイルを読み込む関数
def read_excel_data():
    excel_file = os.path.join(app.root_path, "static", "data.xlsx")
    # ExcelファイルをDataFrameとして読み込む
    df = pd.read_excel(excel_file)
    # DataFrameを辞書形式に変換して返す
    return df.to_dict(orient='records')

@app.route('/')
def index():
    # Excelファイルからデータを読み込む
    data = read_excel_data()
    # index.htmlテンプレートにデータを渡してレンダリングする
    return render_template('index2.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
