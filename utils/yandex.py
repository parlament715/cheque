import pandas as pd
import random
import asyncio
import numpy as np
class Сonstructor:
    file_name = "constructor.xlsx"
    @classmethod
    async def get_excel(cls,cnx):
        yandex_df = pd.DataFrame()
        df = pd.read_sql_query("SELECT * FROM cards", cnx)
        df = df[df["status"] == 1]
        df["company_name"] = df["company_name"].apply(lambda x: x.lower().strip())
        df['date_time'] = pd.to_datetime(df['date_time'], format='%d.%m.%Y %H:%M')


        df['point'] = df['company_name'] + ' - ' + df['address']

        # Сортируем датафрейм по дате и времени в обратном порядке
        df = df.sort_values(by=['date_time'], ascending=False)

        # Группируем по точке
        grouped = df.groupby('point')

        # Выбираем самый свежий чек для каждой точки
        latest_checks = grouped.first()

        # Если в одной точке есть несколько чеков с одинаковой датой и временем,
        # выбираем тот, у которого больше символов в столбце 'comment'
        for point in latest_checks.index:
          if grouped.get_group(point).shape[0] > 1:
            # Фильтруем чеки с одинаковой датой и временем
            same_time_checks = grouped.get_group(point)[grouped.get_group(point)['date_time'] == latest_checks.loc[point, 'date_time']]
            # Сортируем по количеству символов в 'comment' в обратном порядке
            same_time_checks = same_time_checks.sort_values(by=['comment'], key=lambda x: x.str.len(), ascending=False)
            # Выбираем первый чек 
            latest_checks.loc[point] = same_time_checks.iloc[0]
        latest_checks["FD/shift"] = (latest_checks["FD"] / latest_checks["shift_number"]).round()
        yandex_df[['Широта', 'Долгота']] = latest_checks['coordinates'].str.split(' ', expand=True)
        yandex_df["Широта"] = yandex_df["Широта"].astype(str).str.replace(",","")
        yandex_df["random"] = np.random.uniform(low=-9/100000, high=9/100000, size=len(yandex_df))
        yandex_df["Широта"] = yandex_df["Широта"].astype(float) + yandex_df["random"]
        yandex_df["random"] = np.random.uniform(low=-9/100000, high=9/100000, size=len(yandex_df))
        yandex_df["Долгота"] = yandex_df["Долгота"].astype(float) + yandex_df["random"]
        yandex_df["Описание"] = "Адрес = " + latest_checks["address"].astype(str) + "    " + "дата и время = " + latest_checks["date_time"].astype(str) + "    "+"комментарий = " + latest_checks["comment"].astype(str) 
        yandex_df["Подпись"] = latest_checks["company_name"]
        yandex_df["Номер метки"] = latest_checks["FD/shift"]
        yandex_df = yandex_df[["Широта", "Долгота", "Описание", "Подпись", "Номер метки"]]
        yandex_df.to_excel(cls.file_name,index = False)


if __name__ == "__main__":
    import sqlite3
    cnx = sqlite3.connect("request.db")
    asyncio.run(Сonstructor.get_excel(cnx))
    # Сonstructor.get_excel(cnx)