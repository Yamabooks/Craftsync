from flask import Flask, render_template, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/run-script')
def run_script():
    # ファイルパスを設定（ローカルパスを使用）
    craftsman_file_path = '../app/static/職人データサンプル.xlsx'
    participant_file_path = 'static/体験者データサンプル.xlsx'

    # データを読み込む
    craftsman_data = pd.read_excel(craftsman_file_path)
    participant_data = pd.read_excel(participant_file_path)

    # タイムスタンプを秒数に置き換える
    craftsman_data.reset_index(inplace=True)
    participant_data.reset_index(inplace=True)

    # 各データポイントに順番に秒数を割り当てる
    craftsman_data['second'] = range(1, len(craftsman_data) + 1)
    participant_data['second'] = range(1, len(participant_data) + 1)

    # 元の 'day' カラムを削除
    craftsman_data.drop(columns=['day'], inplace=True)
    participant_data.drop(columns=['day'], inplace=True)

    # 'second' をインデックスとして設定
    craftsman_data.set_index('second', inplace=True)
    participant_data.set_index('second', inplace=True)

    # 'index' カラムを削除
    craftsman_data.drop(columns=['index'], inplace=True)
    participant_data.drop(columns=['index'], inplace=True)

    # インデックス (秒数) に基づいてデータを結合
    combined_data_seconds = pd.concat([craftsman_data, participant_data], axis=1, join='inner', keys=['Craftsman', 'Participant'])

    combined_data_seconds.columns = ['Craftsman_num', 'Participant_num']

    # 差分を計算(Craftsman_num を基準にしたパーセンテージ変化の計算)
    combined_data_seconds['Difference'] = abs((combined_data_seconds['Participant_num'] - combined_data_seconds['Craftsman_num']) / combined_data_seconds['Craftsman_num']) * 100

    # ランクを付与する関数
    def assign_rank(difference):
        if abs(difference) <= 10:
            return 'S'
        elif abs(difference) <= 20:
            return 'A'
        elif abs(difference) <= 30:
            return 'B'
        elif abs(difference) <= 40:
            return 'C'
        else:
            return 'D'

    # ランクを付与
    combined_data_seconds['Rank'] = combined_data_seconds['Difference'].apply(assign_rank)

    # 平均差分を計算
    average_difference_seconds = combined_data_seconds['Difference'].mean()

    # 最終ランクを付与する関数
    def final_rank(x):
        if x <= 10:
            return 'S'
        elif x <= 20:
            return 'A'
        elif x <= 30:
            return 'B'
        elif x <= 40:
            return 'C'
        else:
            return 'D'

    # データをプロット
    plt.figure(figsize=(12, 6))
    plt.plot(combined_data_seconds.index, combined_data_seconds['Craftsman_num'], label='職人', color='blue')
    plt.plot(combined_data_seconds.index, combined_data_seconds['Participant_num'], label='あなた', color='orange')
    plt.xlabel('秒数')
    plt.ylabel('測定値')
    plt.title('職人とあなたの測定値比較')
    plt.xticks(ticks=combined_data_seconds.index, labels=combined_data_seconds.index, rotation=0)
    plt.legend()
    plt.grid(True)

    # グラフの保存
    graph_path = os.path.join('static', 'sample_graph.png')
    plt.savefig(graph_path)
    plt.close()

    return jsonify({'graph_url': graph_path, 'average_difference': average_difference_seconds, 'rank': final_rank(average_difference_seconds)})

if __name__ == '__main__':
    app.run(debug=True)
