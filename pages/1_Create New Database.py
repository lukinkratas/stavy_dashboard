import pandas as pd
import streamlit as st
from custom_utils import s3_put_df
from constants import BUCKET_NAME

def create_empty_df(field_names):
    return pd.DataFrame({field_name: [] for field_name in field_names})

def main():
    st.header('Create New Database')

    st.subheader('1. Database Name')
    filename = st.text_input(f'Database Name:')

    st.subheader('2. Fields')

    col1, col2 = st.columns([0.9, 0.1], vertical_alignment='bottom')

    new_field_name = col1.text_input(f'Field Name:')

    if col2.button(':heavy_plus_sign:', key='add_database'):
        st.session_state['field_names'].append(new_field_name)
        st.rerun()

    st.subheader('Current Fields')

    if not 'field_names' in st.session_state:
        st.session_state['field_names'] = ['datum']

    for field_name in st.session_state['field_names']:
        col1, col2, col3 = st.columns([0.4, 0.5, 0.1], vertical_alignment='bottom')
        col1.write(field_name)
        if field_name == 'datum':
            col2.write('*datum field is mandatory.*')
        else:
            if col3.button(':x:', key=f'x_{field_name}'):
                st.session_state['field_names'].remove(field_name)
                st.rerun()

    if st.button('Create'):
        df = create_empty_df(st.session_state['field_names'])
        s3_put_df(df, bucket_name=BUCKET_NAME, key_name=filename, index=False)
        del st.session_state['field_names']
        st.rerun()

main()