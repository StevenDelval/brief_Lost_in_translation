import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlalchemy as db

engine = db.create_engine("sqlite:///donnees_sncf.db")
connection = engine.connect()

df = pd.read_sql_table(table_name="sncf",con=engine)
df['date'] = pd.to_datetime(df['date']) - pd.to_timedelta(7, unit='d')
df_semaine= pd.DataFrame(df.groupby([pd.Grouper(key='date', freq='W')])["type_objet"].count().reset_index())

fig, ax = plt.subplots()
ax.hist(df_semaine)


st.pyplot(fig)
