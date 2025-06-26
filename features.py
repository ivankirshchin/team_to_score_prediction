import pandas as pd
import numpy as np
import json

top_clubs = ['CSKA Moscow', 'Lokomotiv Moscow', 'FK Krasnodar', 'Spartak Moscow', 'Zenit St Petersburg', 'Dinamo Moscow']
underdogs = {
    '2020/21': ['Rotor Volgograd', 'FC Khimki'],
    '2021/22': ['Krylia Sovetov', 'Nizhny Novgorod'],
    '2022/23': ['Torpedo Moscow', 'Fakel Voronezh', 'Orenburg', 'FC Khimki'],
    '2023/24': ['Rubin Kazan', 'Baltika Kaliningrad', 'Nizhny Novgorod', 'Fakel Voronezh'],
    '2024/25': ['Akron', 'Dinamo Makhachkala', 'FC Khimki', 'Nizhny Novgorod']
}

def avg_scored(row, matches, n):
    if row['MD'] < n:
        return None
    df = matches[(matches['Team'] == row['Team']) & (matches['Date'] < row['Date'])]
    df = df.sort_values(by=['Date'], ascending=False).head(n)
    return df['scored'].mean() if not df.empty else None

def avg_missed(row, matches, n):
    if row['MD'] < n:
        return None
    df = matches[(matches['Team'] == row['Team']) & (matches['Date'] < row['Date'])]
    df = df.sort_values(by=['Date'], ascending=False).head(n)
    return df['missed'].mean() if not df.empty else None

def avg_target(row, matches, n):
    if row['MD'] < n:
        return None
    df = matches[(matches['Team'] == row['Team']) & (matches['Date'] < row['Date'])]
    df = df.sort_values(by=['Date'], ascending=False).head(n)
    return df['target'].mean() if not df.empty else None

def opponent_avg_scored(row, matches, n):
    if row['MD'] < n:
        return None
    df = matches[(matches['Team'] == row['Opponent']) & (matches['Date'] < row['Date'])]
    df = df.sort_values(by=['Date'], ascending=False).head(n)
    return df['scored'].mean() if not df.empty else None

def opponent_avg_missed(row, matches, n):
    if row['MD'] < n:
        return None
    df = matches[(matches['Team'] == row['Opponent']) & (matches['Date'] < row['Date'])]
    df = df.sort_values(by=['Date'], ascending=False).head(n)
    return df['missed'].mean() if not df.empty else None

def opponent_avg_target(row, matches, n):
    if row['MD'] < n:
        return None
    df = matches[(matches['Team'] == row['Opponent']) & (matches['Date'] < row['Date'])]
    df = df.sort_values(by=['Date'], ascending=False).head(n)
    return df['target'].mean() if not df.empty else None

def prev_target(x, matches):
    team = x['Team']
    opponent = x['Opponent']
    season = x['Season']
    date = x['Date']
    
    new_df = matches[(matches['Team'] == team) & (matches['Opponent'] == opponent) & \
                    (matches['Date'] < date)]
    if new_df.shape[0] > 0:
        return new_df.sort_values(by='Date', ascending=False).iloc[0]['target']
    else:
        return None

def positions_diff_then(x):
    with open('team_positions.json', "r", encoding="utf-8") as json_file:
        team_positions = json.load(json_file)
    return team_positions[x['Opponent']][x['Season']] - team_positions[x['Team']][x['Season']]

def positions_diff_now(row):
    with open('table_positions.json', "r", encoding="utf-8") as json_file:
        table_positions = json.load(json_file)
    return table_positions[row['Season']][str(row['MD'])][row['Opponent']] - table_positions[row['Season']][str(row['MD'])][row['Team']]

def positions_diff(row):
    diff_now = positions_diff_now(row)
    diff_then = positions_diff_then(row)
    return (row['MD'] / 30) * diff_now + (1 - (row['MD'] / 30)) * diff_then

def team_status(x, season):
    if x in top_clubs:
        return 'top_club'
    if x in underdogs[season]:
        return 'underdog'
    else:
        return 'mid_class_team'

def underdog(row):
    if row['Team'] in underdogs[row['Season']]:
        return 1
    return 0

def last_rel_result(x, matches, n):
    dist_set = {}
    for team in matches[matches['Season'] == x['Season']]['Team'].unique():
        if team == x['Opponent'] or team == x['Team']:
            continue
        dist_set[team] = abs(positions_diff({'Team': team, 'Opponent': x['Opponent'], 'MD': x['MD'], 'Season': x['Season']}))
    closest_teams = list(pd.Series(dist_set).sort_values().head(n).index) + [x['Opponent']]
    if len(closest_teams) == 0:
        return None

    df = matches[(matches['Date'] < x['Date']) & (matches['Team'] == team) & (np.isin(matches['Opponent'], closest_teams))]

    if df.shape[0] == 0:
        return None

    return df.sort_values(by='Date', ascending=False).head(1).iloc[0]['scored']

def transitive_wins(x, matches, k):
    df = matches[(matches['Date'] < x['Date']) & (matches['Team'] == x['Opponent'])].sort_values(by='Date', ascending=False).head(k)
    df = df[df['Result'] == 'L']
    if df.shape[0] == 0:
        return 0
    transitive_teams = list(df['Opponent'].unique())
    df2 = matches[(matches['Date'] < x['Date']) & (matches['Team'] == x['Team']) & np.isin(matches['Opponent'], transitive_teams)]
    df2 = df2.sort_values(by='Date', ascending=False)
    if df2.shape[0] == 0:
        return 0
    seen = set()
    cnt = 0
    for i in range(df2.shape[0]):
        row = df2.iloc[i]
        if seen == set(transitive_teams):
            break
        if row['Opponent'] in seen:
            continue
        seen.add(row['Opponent'])
        if row['Result'] == 'W':
            cnt += 1
    return cnt

