import pandas as pd
import streamlit as st
from datetime import datetime
# import plotly.express as px
import plotly.graph_objects as go
from custom_utils import list_s3_csvs, fetch_csv, transform_df, append_to_csv

def main():

    st.set_page_config(layout="wide")
    st.title('Add New Entries')

    csvs = list_s3_csvs()

    if not csvs:
        st.write('Files in data directory not found.')
        return

    if filename := st.selectbox('Select File', csvs):

        st.header(f'{filename.capitalize()} - Absolute')
        df = fetch_csv(filename)
        df = transform_df(df)
        st.dataframe(df)

        st.subheader('Add New Entry')
        append_data = {}
        for col in df.columns:
            if col == 'datum':
                append_data[col] = st.date_input(col, datetime.today())
            else:
                append_data[col] = st.text_input(col, 0.)

        if st.button(':heavy_plus_sign:', key='add_row'):
            appends_df = pd.DataFrame(append_data, index=[0])
            append_to_csv(appends_df, filename)
            st.rerun()

main()