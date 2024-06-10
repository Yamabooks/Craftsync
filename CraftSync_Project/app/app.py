#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, session, send_file, request
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import japanize_matplotlib
from datetime import datetime 
import os
import io

app = Flask(__name__)
app.secret_key='admin_secret_key'

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
def play():
    return render_template('play.html')

# [/]へアクセスがあった場合、"result.html"を返す
@app.route('/result')
def result():
    return render_template('result.html')

# [/]へアクセスがあった場合、"score.html"を返す
@app.route('/score')
def score():
    return render_template('score.html')

# [/]へアクセスがあった場合、"end.html"を返す
@app.route('/score2')
def score2():
    return render_template('score2.html', sensor_rank=session.get('sensor_rank_df'))

# [/]へアクセスがあった場合、"end.html"を返す
@app.route('/end')
def end():
    return render_template('end.html')

@app.route('/get_time')
def get_time():
    # 現在時刻を取得
    current_time = datetime.now()

    current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print("フォーマットされた現在時刻:", current_time)

    # セッションにデータを保存
    session['current_time'] = current_time

    return jsonify({'current_time': current_time})

@app.route('/analyze_data')
def analyze_data():
    # データの読み込み
    craftsman_file_path = os.path.join(app.root_path, "static/data", "職人データ.xlsx")
    participant_file_path = os.path.join(app.root_path, "static/data", "体験者データ.xlsx")
    craftsman_data = pd.read_excel(craftsman_file_path)
    participant_data = pd.read_excel(participant_file_path)

    # タイムスタンプを秒数に置き換える
    craftsman_data.reset_index(inplace=True)
    participant_data.reset_index(inplace=True)

    # 各データポイントに順番に秒数を割り当てる
    craftsman_data['秒'] = range(1, len(craftsman_data) + 1)
    participant_data['秒'] = range(1, len(participant_data) + 1)

    # 元の 'timestamp' カラムを削除(本当はこの前に取得時間を計算)
    craftsman_data.drop(columns=['Timestamp'], inplace=True)
    participant_data.drop(columns=['Timestamp'], inplace=True)

    # 'second' をインデックスとして設定
    craftsman_data.set_index('秒', inplace=True)
    participant_data.set_index('秒', inplace=True)

    # 'index' カラムを削除
    craftsman_data.drop(columns=['index'], inplace=True)
    participant_data.drop(columns=['index'], inplace=True)

    # センサーデータのカラム
    sensor_columns = ['force1', 'force2', 'force3', 'accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']

    # センサーデータに対して差分とランクを計算
    # 差分を計算(Craftsman_num を基準にしたパーセンテージ変化の計算)
    # 絶対値を取ってます
    combined_data = pd.concat([craftsman_data, participant_data], axis=1, keys=['Craftsman', 'Participant'])
    for col in sensor_columns:
        combined_data[f'{col}_Diff'] = abs((combined_data['Participant'][col] - combined_data['Craftsman'][col]) / combined_data['Craftsman'][col] * 100)
        combined_data[f'{col}_Rank'] = combined_data[f'{col}_Diff'].apply(
            lambda x: 'S' if x <= 10 else ('A' if x <= 20 else ('B' if x <= 30 else ('C' if x <= 40 else 'D')))
        )

    # 各センサーについて、職人データ、体験者データ、差異、ランクを含む表を作成する
    def create_sensor_table(data, sensor):
        df = pd.DataFrame({
            '職人の値': data['Craftsman'][sensor],
            'あなたの値': data['Participant'][sensor],
            '値の差': data[f'{sensor}_Diff'],
            'ランク': data[f'{sensor}_Rank']
        })
        return df.reset_index()


    # 各センサーに対して個別に表を作成して表示
    sensor_tables = {}
    i = 0
    for sensor in sensor_columns:
        sensor_table = create_sensor_table(combined_data, sensor)
        sensor_tables[sensor] = sensor_table
        #センサーテーブルを保存
        session[sensor] = sensor_table.to_html()
        i+=1

    # グラフ描画（force1, force2, force3）をそれぞれ保存する
    plt.figure(figsize=(12, 10))
    for i, force in enumerate(['force1', 'force2', 'force3'], 1):
        plt.subplot(3, 1, i)
        plt.plot(combined_data['Craftsman'][force], label='職人', color='blue')
        plt.plot(combined_data['Participant'][force], label='あなた', color='red')
        plt.title(f'職人とあなたの {force} センサーデータの比較結果')
        plt.xlabel('秒')
        plt.ylabel(f'{force} の値')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(app.root_path, "static/images/", f'{force}_comparison.png'))  # グラフを保存する
        plt.close()  # プロットをクリア

    # 各ランクに数値を割り当てる関数
    def rank_value(rank):
        return {'S': 5, 'A': 4, 'B': 3, 'C': 2, 'D': 1}.get(rank, 0)

    # 各センサーのランクに基づいて数値を割り当て
    sensor_values = {sensor: rank_value(combined_data[f'{sensor}_Rank'].iloc[0]) for sensor in sensor_columns}

    # ランクのみを表示するための DataFrame を更新
    sensor_rank_df = pd.DataFrame(list(sensor_values.items()), columns=['センサー名', 'ランク'])
    sensor_rank_df['ランク'] = sensor_rank_df['ランク'].map({5: 'S', 4: 'A', 3: 'B', 2: 'C', 1: 'D'})

    #センサーランクの保存
    session['sensor_rank_df'] = sensor_rank_df.to_html()

    # 設定した重みに従って加重平均を計算する
    weighted_sum = (
        (sensor_values['force1'] + sensor_values['force2'] + sensor_values['force3']) * 0.7 / 3 +
        (sensor_values['accel_x'] + sensor_values['accel_y'] + sensor_values['accel_z']) * 0.2 / 3 +
        (sensor_values['gyro_x'] + sensor_values['gyro_y'] + sensor_values['gyro_z']) * 0.1 / 3
    )

    # 加重平均に基づいて総合ランクを割り当て
    combined_data['Overall_Weighted_Rank'] = 'S' if weighted_sum >= 4.6 else 'A' if weighted_sum >= 3.6 else 'B' if weighted_sum >= 2.6 else 'C' if weighted_sum >= 1.6 else 'D'
    print('総合ランク:', combined_data['Overall_Weighted_Rank'].iloc[0])
    
    #総合ランクの保存
    rank = combined_data['Overall_Weighted_Rank'].iloc[0]

    session['rank'] = rank

    return jsonify({'rank': rank})

@app.route('/find_table', methods=['POST'])
def find_table():
    json_data = request.json
    sensor_name = json_data.get('sensor_name')
    sensor_table = session.get(sensor_name)
    return jsonify(sensor_table)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
