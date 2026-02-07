import pandas as pd

df_name = pd.read_csv('nameregisvation.csv')

if __name__ == "__main__":

    print(df_name.columns)