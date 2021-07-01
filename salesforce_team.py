from itertools import groupby

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from numpy.core.defchararray import count

st.set_page_config(layout="wide")
team_analytics_01 = st.beta_container()
team_analytics_02 = st.beta_container()
team_analytics_03 = st.beta_container()


@st.cache
def load_data(file_name01):
    dframe = pd.read_csv(
        file_name01,
        na_values=['NA', 'Missing', None],
        error_bad_lines=False, sep='\t',
        lineterminator='\n',
        dtype=str,
    )
    dframe.columns = dframe.columns.str.replace(" ", "", regex=True)
    dframe['Date/TimeGrabbed'] = pd.to_datetime(dframe['Date/TimeGrabbed'], errors='coerce')
    dframe['Date/TimeClosed'] = pd.to_datetime(dframe['Date/TimeClosed'], errors='coerce')
    dframe['year_month'] = dframe['Date/TimeGrabbed'].dt.strftime('%Y-%m')
    dframe['diffTime'] = (dframe['Date/TimeClosed'] - dframe['Date/TimeGrabbed']).dt.days
    dframe['DateGrabbed'] = dframe['Date/TimeGrabbed'].dt.strftime('%Y-%m-%d')
    dframe['DateClosed'] = dframe['Date/TimeGrabbed'].dt.strftime('%Y-%m-%d')
    dframe = dframe.rename(columns={'SIS(StudentInformationSystem)': 'SIS'})
    dframe['CaseOwner'] = dframe['CaseOwner'].replace(
        {'Alejandro Hassan': 'Ale', 'Alexander Rodriguez': 'Alex', 'Douglas Carmona': 'Doug',
         'Fabricio Chungo': 'Fabri', 'Federico Bufanio': 'Fede', 'Fernando Diaz Coetzee': 'Fer',
         'Fernando Zavatto': 'Steven', 'Martin Belzunce': 'Tincho',
         'Matias Zulberti': 'Mati', 'Nicolas Pantazis': 'Nico', 'Raul Sosa': 'Rulo', 'Sergio Leyes': 'Sergio'},
        regex=True)
    owners = dframe['CaseOwner'].drop_duplicates()
    year_month = dframe['year_month'].drop_duplicates()
    return dframe, owners, year_month


uploaded_file = st.sidebar.file_uploader(
    label="Uploade CSV file to use as Dataframe",
    type=['csv']
    )
print(uploaded_file)

if uploaded_file is not None and "bb_team" in uploaded_file.name:
    print(uploaded_file)
    print("Ready to start..!")
    try:
        df, owners, year_month = load_data(uploaded_file)
    except Exception as e:
        print(e)

try:
    with team_analytics_01:
        st.title('Team Cases Analytics')
        st.header('Dataframe')
        st.write(df)

        st.header('Total Cases/Month')
        cases_month = df['year_month'].value_counts()
        st.bar_chart(cases_month)

        st.header('Total Cases/Owner')
        cant_cases = df['CaseOwner'].value_counts()
        st.bar_chart(cant_cases)

        st.header('Total Cases/Owner')
        cases_by_owner = df.groupby('CaseOwner')['Subject'].count().reset_index()
        plot1 = px.pie(cases_by_owner, values='Subject', names='CaseOwner')
        st.plotly_chart(plot1)

    with team_analytics_02:
        left_col, right_col = st.beta_columns(2)

        cases_pivot1 = df.pivot_table(index='CaseOwner', columns='year_month', values='Status', aggfunc='count')
        cases_pivot2 = df.pivot_table(index='year_month', columns='CaseOwner', values='Status', aggfunc='count')
        cases_month_owner = df.groupby(['year_month', 'CaseOwner'])['CaseNumber']. \
            count().to_frame('count').reset_index().set_index(['year_month'])
        cases_owner_month = df.groupby(['CaseOwner', 'year_month'])['CaseNumber']. \
            count().to_frame('count').reset_index().set_index('CaseOwner')

        left_col.header('Cases/Owner/Month')
        left_col.write(cases_pivot1)
        right_col.header('Cases/Month/Owner')
        right_col.write(cases_pivot2)

        left_col.header('Total Cases/Owner')
        plot1 = px.bar(data_frame=cases_pivot1)
        left_col.plotly_chart(plot1)

        right_col.header('Total Cases/Month')
        plot2 = px.bar(data_frame=cases_pivot2)
        right_col.plotly_chart(plot2)

        st.header('Avg Cases/Month/Owner')
        avg_cases1 = cases_pivot1.reset_index().mean().round(0).to_frame('avg')
        st.bar_chart(avg_cases1)
        avg_cases1 = avg_cases1.reset_index()
    
    with team_analytics_03:
       
        selectbox01 = st.sidebar.selectbox("Select Search Field: ", options=['CaseNumber',
                                                                             'CaseOwner',
                                                                             'SIS',
                                                                             'AccountName'])

        options = df[selectbox01].drop_duplicates().tolist()
        selectbox02 = st.sidebar.selectbox("Select an Option: ", options=options)
        header = "Search Analysis Criteria: " + str(selectbox01) + " - " + str(selectbox02)
        st.header(header)
        df_owner = df[df[selectbox01] == selectbox02]
        df_owner2 = df_owner.loc[:, ['DateGrabbed', 'DateClosed', 'CaseOwner', 'CaseNumber', 'AccountName',
                                     'SIS', 'Subject']].drop(selectbox01, axis='columns').sort_values('DateGrabbed')
        st.write(df_owner2)


except Exception as e:
    print("Error de la aplicacion: ", e)