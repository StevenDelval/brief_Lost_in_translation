import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlalchemy as db

engine = db.create_engine("sqlite:///db.sqlite")
connection = engine.connect()

df = pd.read_sql_table(table_name="LostItem",con=engine)
df['date'] = pd.to_datetime(df['date']) - pd.to_timedelta(7, unit='d')
df_semaine= pd.DataFrame(df.groupby([pd.Grouper(key='date', freq='W')])["type_objet"].count())

fig, ax = plt.subplots()
ax.hist(df_semaine,bins=30,color = "#45d4a1", ec="red",lw=2)



st.pyplot(fig)


df_semaine_type= pd.DataFrame(df[['date',"type_objet",'id']].groupby([pd.Grouper(key='date', freq='W'),"type_objet"]).count().reset_index().set_index("date"))
mask_objet =st.multiselect("Choisissez un type d'objet",df_semaine_type["type_objet"].unique())
if st.button("Cree le graphique"):
    combo_mask = df_semaine_type["type_objet"] == mask_objet[0]
    for mask in mask_objet:
        combo_mask |= df_semaine_type["type_objet"] == mask

    st.line_chart(df_semaine_type[combo_mask]["id"])
