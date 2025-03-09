import pandas as pd
import streamlit as st
from datetime import datetime
# import plotly.express as px
import plotly.graph_objects as go
from custom_utils import s3_list_objects, s3_read_df, transform_df, s3_put_df
from constants import BUCKET_NAME

def main():

    st.set_page_config(layout="wide")
    st.title('Add New Entries')

    s3_key_names = s3_list_objects(BUCKET_NAME)
    csvs = [key_name for key_name in  s3_key_names if key_name.endswith('csv')]

    if not csvs:
        st.write('Files in data directory not found.')
        return

    if filename := st.selectbox('Select File', csvs):

        st.header(f'{filename.capitalize()} - Absolute')
        df = s3_read_df(bucket_name=BUCKET_NAME, key_name=filename)
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
            append_df = pd.DataFrame(append_data, index=[0])
            append_df = transform_df(append_df)
            merged_df = pd.concat([df, append_df], ignore_index=True)
            s3_put_df(merged_df, bucket_name=BUCKET_NAME, key_name=filename, index=False)
            st.rerun()

main()