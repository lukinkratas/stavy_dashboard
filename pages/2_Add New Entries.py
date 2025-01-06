import pandas as pd
import streamlit as st
import os
from datetime import datetime
# import plotly.express as px
import plotly.graph_objects as go

def main():

    st.set_page_config(layout="wide")
    st.title('Add New Entries')

    if os.path.isdir('data'):
        data_files = os.listdir('data')
        if not data_files:            
            st.write('Files in data directory not found.')
            return

    if filename := st.selectbox('Select File', data_files):

        st.header(f'{filename} - Absolute')
        df = pd.read_csv(os.path.join('data', filename), index_col=False)
        df['datum'] = pd.to_datetime(df['datum'])
        st.dataframe(df)

        st.subheader('Add New Entry')
        new_data = {}
        for col in df.columns:
            if col == 'datum':
                new_data[col] = st.date_input(col, datetime.today())
            else:
                new_data[col] = st.text_input(col, 0.)

        if st.button(':heavy_plus_sign:', key='add_row'):
            new_df = pd.DataFrame(new_data, index=[0])
            with open(os.path.join('data', filename), 'a') as file:
                file.write('\n')
                if filename.endswith('csv'):
                    new_df.to_csv(file, header=False, index=False)
                elif filename.endswith('parquet'):
                    new_df.to_parquet(file, header=False, index=False)
            st.rerun()

main()