import pandas as pd
import numpy as np
from datetime import (datetime, date)
import json

class preprocessToolKit:
    
    def dropDuplicates(dataset):
        dataset = dataset.drop_duplicates(keep='first').reset_index(drop=True).copy()    
        return dataset
    
    def checkTypo(dataset):
        dataset['Data'] = dataset.Dia.astype(str) + ' ' + dataset.Hora.astype(str)
        uniqueDataLen = []
        for i in range(len(dataset.Data)):
            uniqueDataLen.append(len(dataset.Data[i]))
        uniqueDataLen = list(set(uniqueDataLen))
        idx = []
        for i in range(len(dataset.Data)):
            if len(dataset.Data[i]) > 19 or len(dataset.Data[i]) < 19:
                idx.append(dataset[dataset.Data == dataset.Data[i]].index.values[0])
            else:
                None
        dataset.drop(index=idx, axis=0, inplace=True)
        return dataset
    
    def dataTimeConverter(dataset, col1, col2):
        
        # day_of_week
        dataset['day_of_week'] = list(pd.to_datetime(dataset[col1], format='%Y-%m-%d').dt.dayofweek)
        dataset['day_name'] = list(pd.to_datetime(dataset[col1], format='%Y-%m-%d').dt.day_name())#.dayofweek)

        # day_of_month
        dataset[[col1+'_Ano', col1+'_Mês', col1+'_Dia']] = dataset[col1].astype(str).str.split("-", expand=True)
        dataset.rename(columns={col1+'_Dia':'day_of_month'}, inplace=True)
        dataset['day_of_month'] = dataset['day_of_month'].astype(int)

        # pure_time
        dataset[[col2+'_HH', col2+'_MIN', col2+'_SEC']] = dataset[col2].astype(str).str.split(":", expand=True)
        dataset['pure_time'] = dataset[col2+'_HH'].astype(int) + (dataset[col2+'_MIN'].astype(int) / 60) + (dataset[col2+'_SEC'].astype(float) / 3600)

        del dataset[col1+'_Ano'], dataset[col1+'_Mês'], dataset[col2+'_HH'], dataset[col2+'_MIN'], dataset[col2+'_SEC']
        
        conditions = [
            (dataset.day_of_month <= 5),
            ((dataset.day_of_month > 5) & (dataset.day_of_month <= 10)),
            ((dataset.day_of_month > 10) & (dataset.day_of_month <= 15)),
            ((dataset.day_of_month > 15) & (dataset.day_of_month <= 20)),
            ((dataset.day_of_month > 20) & (dataset.day_of_month <= 25)),
            (dataset.day_of_month > 25),
        ]

        choices = ['1-5', '6-10', '11-15', '16-20', '21-25', '>25']

        dataset['day_of_month_RANGE'] = np.select(conditions, choices, default='Tie')
        return dataset
    
    def recorrenciaTransacaoDiaria(dataset, col1, col2):
        dataset_sameDay = dataset[['Cartão','Dia']].value_counts().to_frame().reset_index()
        dataset_sameDay.rename(columns={0:'same_day_count'}, inplace=True)
        return dataset_sameDay
    
    def recorrenciaTransacaoDiariaValor(dataset, col1, col2, col3):
        dataset_sameDayValor = dataset[['Cartão','Dia','Valor']].value_counts().to_frame().reset_index()
        dataset_sameDayValor.rename(columns={0:'same_day_valor_count'}, inplace=True)
        return dataset_sameDayValor
        
    def merges(dataset, col1, col2, col3):
        dataset_sameDay = preprocessToolKit.recorrenciaTransacaoDiaria(dataset, col1, col2)
        dataset_sameDayValor = preprocessToolKit.recorrenciaTransacaoDiariaValor(dataset, col1, col2, col3)
        dataseta = dataset.merge(
            dataset_sameDay[[col1, col2, 'same_day_count']], 
            how='left', 
            left_on = [col1, col2], 
            right_on = [col1, col2]
        )
        dataset = dataseta.merge(
            dataset_sameDayValor[[col1, col2, col3, 'same_day_valor_count']], 
            how='left', 
            left_on = [col1, col2, col3], 
            right_on = [col1, col2, col3]
        )
        dataset = dataset.sort_values(by=['Cartão','Dia','Hora']).reset_index(drop=True).copy()
        return dataset
    
    def rankTransacao(dataset):
        dataset['rank_same_day'] = dataset.groupby(by=['Cartão','Dia'])['pure_time'].rank(method='first')
        return dataset
    
    def diffTime(dataset):
        diff_time = []
        for i in range(len(dataset)):
            if dataset.rank_same_day[i] == 1:
                diff_time.append(0)
            else:
                diff_time.append(dataset.pure_time[i] - dataset.pure_time[i-1])
        dataset['diff_time'] = diff_time
        return dataset