# general
import warnings
import time
import gc

#data
import pandas as pd
import numpy as np
from datetime import (datetime, date)

#preprocess
from _preprocess import *

#model
import joblib

### Global Variables
PATH_RAWDATA = "../raw_data/"
PATH_FILES = "../notebooks/"
DATA = "20220520_rawdata_original.xlsx"
#MODEL = "20220522_set1_poc_XGBClassifier.sav"
MODEL = "20220522_set1_mvp_XGBClassifier.sav"
DATE = time.strftime("%Y%m%d")

### List of Resources
selected = [
    'Valor',
    'Cartão',
    'Data',
    'pure_time',
    'same_day_count',
    'same_day_valor_count',
    'rank_same_day',
    'diff_time',
    'day_name_Friday',
    'day_name_Monday',
    'day_name_Saturday',
    'day_name_Sunday',
    'day_name_Thursday',
    'day_name_Tuesday',
    'day_name_Wednesday',
    'day_of_month_RANGE_1-5',
    'day_of_month_RANGE_11-15',
    'day_of_month_RANGE_16-20',
    'day_of_month_RANGE_21-25',
    'day_of_month_RANGE_6-10',
    'day_of_month_RANGE_>25',
]

features_set1 = [
    'Valor',
    'pure_time',
    'same_day_count',
    'same_day_valor_count',
    'rank_same_day',
    'diff_time',
    'day_name_Friday',
    'day_name_Monday',
    'day_name_Saturday',
    'day_name_Sunday',
    'day_name_Thursday',
    'day_name_Tuesday',
    'day_name_Wednesday',
    'day_of_month_RANGE_1-5',
    'day_of_month_RANGE_11-15',
    'day_of_month_RANGE_16-20',
    'day_of_month_RANGE_21-25',
    'day_of_month_RANGE_6-10',
    'day_of_month_RANGE_>25'
]

def main():
        
    print("Running...")
    
    # Load Data
    df = pd.read_excel(PATH_RAWDATA + DATA, sheet_name='Aba 2')

    # Preprocess
    
    ## Check for typos
    df = preprocessToolKit.checkTypo(df)

    ## Feature Engineering
    df = preprocessToolKit.dataTimeConverter(df, 'Dia', 'Hora')
    df = preprocessToolKit.merges(df, 'Cartão','Dia','Valor')
    df = preprocessToolKit.rankTransacao(df)
    df = preprocessToolKit.diffTime(df)

    # Encoding
    df = pd.get_dummies(df, columns=['day_name', 'day_of_month_RANGE'])

    df.set_index(['Cartão', 'Data'],inplace=True)

    # Load Model & Predict
    model = joblib.load(PATH_FILES + MODEL)
    y_hat = model.predict(df[features_set1])

    # Save Predictions
    df['y_hat'] = y_hat
    df.reset_index(drop=False, inplace=True)
    df[['Cartão', 'Data', 'y_hat']].to_csv(DATE + "_outputs.csv", sep=',', index=False)
    
    print("Done!")
        
if __name__ == "__main__":
    main()