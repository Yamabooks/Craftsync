#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, session, send_file, request
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import japanize_matplotlib
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
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

@app.route('/get_start_time')
def get_start_time():
    # スタート時刻を取得
    start_time = datetime.now()

    # 1秒を加える
    start_time += timedelta(seconds=1)

    start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    print("現在時刻:", start_time)

    # セッションにデータを保存
    session['start_time'] = start_time

    return jsonify({'start_time': start_time})

@app.route('/get_end_time')
def get_end_time():
    # エンド時刻を取得
    end_time = datetime.now()

    # 1秒を加える
    end_time += timedelta(seconds=1)

    end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
    print("終了時刻:", end_time)

    # セッションにデータを保存
    session['end_time'] = end_time

    return jsonify({'end_time': end_time})


@app.route('/analyze_data')

def analyze_data():

    def make_data():
        file_path = os.path.join(app.root_path, "static/data", "data.xlsx")
        sheet_name = 'Sheet1'
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        start_time = session.get('start_time')
        end_time = session.get('end_time')

        # 日付文字列をdatetimeオブジェクトに変換
        start_time = datetime.strptime(start_time, "%Y-%d-%m %H:%M:%S")
        end_time = datetime.strptime(end_time, "%Y-%d-%m %H:%M:%S")

        # 日付列をdatetime型に変換
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])

        # 時間範囲でデータをフィルタリング
        df = df[(df['Timestamp'] >= start_time) & (df['Timestamp'] <= end_time)]

        # 新しいフォーマットで日付を表示
        df['Timestamp'] = pd.to_datetime(df['Timestamp']).dt.strftime("%m/%d/%Y, %H:%M:%S")
        print('フォーマット後：',df)

        # データを新しいファイルに書き込み
        file_path = os.path.join(app.root_path, "static/data", "テストデータ.xlsx")
        df.to_excel(file_path, index=False)

        return None

    # 最新データの作成
    #make_data()

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
    plt.savefig(os.path.join(app.root_path, "static/images/graph", 'force_comparison.png'))  # グラフを保存する
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

    # データの標準化
    scaler = StandardScaler()
    features = ['force1', 'force2', 'force3', 'accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']

    # 職人データにフィットさせ、両方のデータセットを変換
    craftsman_scaled = scaler.fit_transform(craftsman_data[features])
    participant_scaled = scaler.transform(participant_data[features])

    # データをDataFrameに変換
    craftsman_scaled_df = pd.DataFrame(craftsman_scaled, columns=features)
    participant_scaled_df = pd.DataFrame(participant_scaled, columns=features)

    # 追加の特徴量生成: センサーデータの平均、標準偏差、範囲
    def add_features(df):
        df['force_mean'] = df[['force1', 'force2', 'force3']].mean(axis=1)
        df['accel_mean'] = df[['accel_x', 'accel_y', 'accel_z']].mean(axis=1)
        df['gyro_mean'] = df[['gyro_x', 'gyro_y', 'gyro_z']].mean(axis=1)

        df['force_std'] = df[['force1', 'force2', 'force3']].std(axis=1)
        df['accel_std'] = df[['accel_x', 'accel_y', 'accel_z']].std(axis=1)
        df['gyro_std'] = df[['gyro_x', 'gyro_y', 'gyro_z']].std(axis=1)

        df['force_range'] = df[['force1', 'force2', 'force3']].max(axis=1) - df[['force1', 'force2', 'force3']].min(axis=1)
        df['accel_range'] = df[['accel_x', 'accel_y', 'accel_z']].max(axis=1) - df[['accel_x', 'accel_y', 'accel_z']].min(axis=1)
        df['gyro_range'] = df[['gyro_x', 'gyro_y', 'gyro_z']].max(axis=1) - df[['gyro_x', 'gyro_y', 'gyro_z']].min(axis=1)

        return df

    # 特徴量生成を適用
    craftsman_features = add_features(craftsman_scaled_df)
    participant_features = add_features(participant_scaled_df)

    # ランダムフォレストモデルの訓練と予測
    model = RandomForestRegressor(n_estimators=100, random_state=42)

    # 特徴量とターゲット変数の準備
    X_craftsman = craftsman_features.drop('force_mean', axis=1)
    y_craftsman = craftsman_features['force_mean']

    # モデルの再訓練
    model.fit(X_craftsman, y_craftsman)

    # 参加者データのターゲット変数の予測
    participant_predictions_new_target = model.predict(participant_features.drop('force_mean', axis=1))

    # 予測値の平均と標準偏差の計算
    predicted_mean = np.mean(participant_predictions_new_target)
    predicted_std = np.std(participant_predictions_new_target)

    # クラフツマンデータのターゲット変数の平均と標準偏差の取得
    true_mean = y_craftsman.mean()
    true_std = y_craftsman.std()

    # 正規化平均絶対誤差（NMAE）の計算
    absolute_errors = np.abs(participant_predictions_new_target - true_mean)
    mean_absolute_error = np.mean(absolute_errors)
    range_of_values = y_craftsman.max() - y_craftsman.min()
    nmae = mean_absolute_error / range_of_values
    match_rate = 1 - nmae

    # 個別のマッチ率の計算とプロット
    individual_match_rates = []

    for prediction in participant_predictions_new_target:
        individual_error = np.abs(prediction - true_mean)
        individual_nmae = individual_error / range_of_values
        individual_match_rate = 1 - individual_nmae
        individual_match_rates.append(individual_match_rate)

    plt.figure(figsize=(10, 5))
    plt.plot(individual_match_rates, marker='o', linestyle='-', color='g')
    plt.title('あなたの体験データのAI評価結果')
    plt.xlabel('秒')
    plt.ylabel('評価値')
    plt.grid(True)
    plt.ylim(0, 1)  # マッチ率は0から1の間
    plt.xticks(range(0, 10), labels=range(1, 11))  # 1から10の全ての目盛りを表示
    plt.savefig(os.path.join(app.root_path, "static/images/graph", 'AI_evaluation_results.png'))
    plt.close()

    return jsonify({'rank': rank})

@app.route('/find_table', methods=['POST'])
def find_table():
    json_data = request.json
    sensor_name = json_data.get('sensor_name')
    sensor_table = session.get(sensor_name)
    return jsonify(sensor_table)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
