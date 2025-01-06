import pandas as pd
import streamlit as st
import os
from datetime import datetime

def create_empty_df(field_names):
    return pd.DataFrame({field_name: [] for field_name in field_names})

def main():
    st.header('Create New Database')

    st.subheader('Current Fields')

    if not 'field_names' in st.session_state:
        st.session_state['field_names'] = ['datum']

    for field_name in st.session_state['field_names']:
        col1, col2 = st.columns([0.9, 0.1], vertical_alignment='bottom')
        col1.write(field_name)
        if field_name != 'datum':
            if col2.button(':x:', key=f'x_{field_name}'):
                st.session_state['field_names'].remove(field_name)
                st.rerun()
    
    st.write('*datum field is mandatory.*')

    st.subheader('1. Add New Field')

    col1, col2 = st.columns([0.9, 0.1], vertical_alignment='bottom')

    new_field_name = col1.text_input(f'Field Name:')

    if col2.button(':heavy_plus_sign:', key='add_database'):
        st.session_state['field_names'].append(new_field_name)
        st.rerun()

    st.subheader('2. Save')

    col1, col2 = st.columns([0.8, 0.2], vertical_alignment='bottom')
    filename = col1.text_input(f'Filename (w/o suffix):')
    filetype = col2.selectbox('Filetype', ('CSV', 'Parquet'))

    st.write('*CSV - Comma Separated Values (can be manually edited as text)*')
    st.write('*Parquet - Storage effective*')

    if st.button('Save'):
        df = create_empty_df(st.session_state['field_names'])
        if not os.path.isdir('data'):
            os.mkdir('data')
        if filetype == 'CSV':
            df.to_csv(os.path.join('data', f'{filename}.csv'), index=False)
        elif filetype == 'Parquet':
            df.to_parquet(os.path.join('data', f'{filename}.parquet'), index=False)
        st.rerun()

main()