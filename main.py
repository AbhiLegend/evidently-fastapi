from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import pandas as pd
import numpy as np
import requests
import zipfile
import io

from datetime import datetime
from sklearn import datasets, ensemble

from evidently.dashboard import Dashboard
from evidently.pipeline.column_mapping import ColumnMapping
from evidently.dashboard.tabs import DataDriftTab, NumTargetDriftTab, RegressionPerformanceTab

content = requests.get("https://archive.ics.uci.edu/ml/machine-learning-databases/00275/Bike-Sharing-Dataset.zip").content
with zipfile.ZipFile(io.BytesIO(content)) as arc:
    raw_data = pd.read_csv(arc.open("hour.csv"), header=0, sep=',', parse_dates=['dteday'], index_col='dteday')

target = 'cnt'
prediction = 'prediction'
numerical_features = ['temp', 'atemp', 'hum', 'windspeed', 'hr', 'weekday']
categorical_features = ['season', 'holiday', 'workingday']

reference = raw_data.loc['2011-01-01 00:00:00':'2011-01-28 23:00:00']
current = raw_data.loc['2011-01-29 00:00:00':'2011-02-28 23:00:00']

regressor = ensemble.RandomForestRegressor(random_state = 0, n_estimators = 50)
regressor.fit(reference[numerical_features + categorical_features], reference[target])

ref_prediction = regressor.predict(reference[numerical_features + categorical_features])
current_prediction = regressor.predict(current[numerical_features + categorical_features])

reference['prediction'] = ref_prediction
current['prediction'] = current_prediction

column_mapping = ColumnMapping()

column_mapping.target = target
column_mapping.prediction = prediction
column_mapping.numerical_features = numerical_features
column_mapping.categorical_features = categorical_features

regression_perfomance_dashboard = Dashboard(tabs=[RegressionPerformanceTab()])
regression_perfomance_dashboard.calculate(reference, None, column_mapping=column_mapping)

regression_perfomance_dashboard.save('/static/index.html')

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
