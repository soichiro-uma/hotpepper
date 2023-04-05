import requests
import pandas as pd
import re
import datetime
import warnings
warnings.filterwarnings('ignore')


def hotpepper(count,keyword,turnover_rate,business_days,hourly_wage,employee,rent,other):
    API_KEY = "d70f5128bf847e1e"
    URL = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
    body = {
        'key':API_KEY,
        'keyword':keyword,
        'range':2,
        'format':'json',
        'count':count
    }
    #API情報のすべて
    response = requests.get(URL,body).json()
    #shop情報すべて
    df_shop_data = pd.DataFrame(response['results']['shop'])
    #必要エレメント
    element = ["id","name","capacity","open","budget"]

    shop_info_list = []
    for i in range(0,count):
        shop_info = {}
        shop_info['総席数'] = df_shop_data['capacity'][i]

        #営業時間：open}
        s = df_shop_data['open'][i]
        match = re.findall(r'\d+', s)
        #00:00の場合24:00にする
        if match[2] == "0":
            match[2] = "00"

        for a in range(0,4):
            if len(match[a]) == 1:
                match[a] = f"0{match[a]}"
        shop_info['オープン'] = f"{match[0]}:{match[1]}"
        shop_info['クローズ'] = f"{match[2]}:{match[3]}"

        #単価(平均予算ver)：budget_average
        t = df_shop_data['budget'][i]['average'].replace(",","")
        shop_info['単価'] = re.findall(r'\d+', t)[0]

        shop_info_list.append(shop_info)
    df_shop_alt = pd.DataFrame(shop_info_list)

    df_shop_alt['営業時間'] = (pd.to_datetime(df_shop_alt['クローズ']) - pd.to_datetime(df_shop_alt['オープン']))/ datetime.timedelta(hours=1)
    #24時間表記へ書き換え
    n_24 = 0
    for add24 in df_shop_alt['営業時間']:
        if add24 <= 0: 
            df_shop_alt['営業時間'][n_24] = df_shop_alt['営業時間'][n_24] + 24
        n_24 += 1

    #来店人数 = 回転率 * 席数
    df_shop_alt['回転率'] = turnover_rate
    df_shop_alt['来店人数'] =  df_shop_alt['総席数'] * df_shop_alt['回転率']

    ##売り上げ(単価 * 来店人数
    df_shop_alt['営業日数　'] = business_days
    df_shop_alt['売上'] = df_shop_alt['単価'].astype('int') * df_shop_alt['来店人数'] * df_shop_alt['営業日数　']

    #人件費計算
    df_shop_alt['時給'] = hourly_wage
    df_shop_alt['従業員数'] = employee

    df_shop_alt['人件費'] = df_shop_alt['時給'] * df_shop_alt['従業員数'] * df_shop_alt['営業時間']

    ##経費(家賃 + 人件費 + 水道光熱費 + 消耗品) + (原価)
    df_shop_alt['家賃'] = rent
    df_shop_alt['その他'] = other

    df_shop_alt['経費'] = (df_shop_alt['家賃'] + df_shop_alt['人件費'] + df_shop_alt['家賃'] + df_shop_alt['売上']*0.25).astype('int') +df_shop_alt['その他']

    ##利益
    df_shop_alt['利益'] = df_shop_alt['売上'] - df_shop_alt['経費']

    #識別
    df_shop_alt["ID"] = df_shop_data["id"] 
    df_shop_alt["掲載店名"] = df_shop_data["name"]


    re_columns = [ 'ID','掲載店名','利益','売上', '単価','総席数','回転率','来店人数',
                  '経費','人件費', '従業員数','時給', '営業時間','オープン', 'クローズ' , '家賃','その他']
    return df_shop_alt[re_columns]  