import numpy as np
import pandas as pd

def mape(row: pd.Series):
    if row['QUANTIDADE_VENDA'] > 0 and row['PREVISAO'] > 0:
        mape = np.mean(np.abs((row['QUANTIDADE_VENDA'] - row['PREVISAO']) / row['QUANTIDADE_VENDA']))
        return mape
    elif (row['QUANTIDADE_VENDA'] > 0 and row['PREVISAO'] == 0) or (row['QUANTIDADE_VENDA'] == 0 and row['PREVISAO'] > 0):
        return 1
    else:
        return 0