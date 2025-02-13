import pandas as pd
import streamlit as st
import os
from datetime import datetime
# import plotly.express as px
import plotly.graph_objects as go
import boto3
import io
from dotenv import load_dotenv

load_dotenv()
s3_client = boto3.client('s3')

# TODO:
# [ ] add parquet table
# [ ] change bar width in diffs graphs
# [ ] refactor
# [ ] files to cloud
# [ ] add logging?

def fetch_data():

    bucket_name = 'stavy'
    key = 'data.csv'

    try:
        # Get object from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        
        # Read the CSV data from the response
        csv_bytes = response['Body'].read().decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_bytes))
        
        print(f"Successfully read CSV from S3. Shape: {df.shape}")
        
    except Exception as e:
        print(f"Error reading CSV from S3: {str(e)}")

    else:
        return df


def main():

    st.set_page_config(layout="wide")
    st.title('Stavy')

    if os.path.isdir('data'):
        data_files = os.listdir('data')
        if not data_files:            
            st.write('Files in data directory not found.')
            return

    if filename := st.selectbox('Select File', data_files):
        col1, col2, col3 = st.columns(3)

        col1.header(f'{filename} - Absolute')
        df = pd.read_csv(os.path.join('data', filename), index_col=False)
        df['datum'] = pd.to_datetime(df['datum'])
        min_dt = df['datum'].min()
        col1.dataframe(df)

        col2.header('Diffs')
        diff_df = df.diff()
        num_df = diff_df._get_numeric_data()
        num_df[num_df < 0] = 0 # replace negative values with zeros
        diff_df['datum'] = df['datum']
        col2.dataframe(diff_df)

        col3.header('Avg Diff')
        avg_df = diff_df.groupby(diff_df.datum.dt.year).mean()  
        avg_df = avg_df.drop(columns='datum')
        col3.dataframe(avg_df)

        for col in df.columns:
            if col != 'datum':
                col1, col2 = st.columns(2)

                # fig = px.line(df, x='datum', y=col, title=f'{col} - absolute')
                fig = go.Figure([
                    go.Scatter(
                        x=df['datum'].values,
                        y=df[col].values,
                        name='Absolute',
                        connectgaps=True
                    )
                ])
                fig.update_layout(
                    title_text=col,
                    autosize=False,
                    width=400,
                    height=400
                )

                for year_start_dt in pd.date_range(min_dt, datetime.today(), freq='YS'):
                    fig.add_vline(
                        x=year_start_dt,
                        line_width=1,
                        line_dash="dash",
                        line_color="green"
                    )
                col1.plotly_chart(fig)

                # fig = px.bar(diff_df, x='datum', y=col, title=f'{col} - diffs')
                fig = go.Figure([
                    go.Bar(
                        x=diff_df['datum'].values,
                        y=diff_df[col].values,
                        name='Diffs'
                    ),
                    go.Scatter(
                        x=avg_df.index.values,
                        y=avg_df[col].values,
                        name='Avg',
                        mode='lines',
                        line_shape='hv',
                        line=dict(width=1, dash='dash')
                    )
                ])
                fig.update_layout(
                    title_text=col,
                    autosize=False,
                    width=400,
                    height=400,
                    barcornerradius=15,
                    # bargap=0.1
                )

                for year_start_dt in pd.date_range(min_dt, datetime.today(), freq='YS'):
                    fig.add_vline(
                        x=year_start_dt,
                        line_width=1,
                        line_dash="dash",
                        line_color="green"
                    )
                col2.plotly_chart(fig)

main()