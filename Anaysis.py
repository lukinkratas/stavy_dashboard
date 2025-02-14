import pandas as pd
import streamlit as st
from datetime import datetime
# import plotly.express as px
import plotly.graph_objects as go
import boto3
import io
from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client('s3')

BUCKET_NAME = 'stavy'

# TODO:
# [ ] add parquet table
# [ ] change bar width in diffs graphs
# [ ] refactor
# [ ] files to cloud
# [ ] add logging?

def list_s3_csvs():

    # Get object from S3
    response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        MaxKeys=1,
    )
    
    contents = response['Contents']
    return [content['Key'] for content in contents if content['Key'].endswith('.csv')]

def fetch_csv(filename):

    # Get object from S3
    response = s3_client.get_object(
        Bucket=BUCKET_NAME,
        Key=filename
    )
    
    # Read the CSV data from the response
    csv_bytes = response['Body'].read().decode('utf-8')
    return pd.read_csv(io.StringIO(csv_bytes))

def transform_df(df):
    df['datum'] = pd.to_datetime(df['datum'])
    return df

def get_diff_df(df):
    diff_df = df.diff()

    # replace negative values with zeros
    num_df = diff_df._get_numeric_data()
    num_df[num_df < 0] = 0

    diff_df['datum'] = df['datum']

    return diff_df

def get_avg_df(diff_df):
    return diff_df.groupby(diff_df.datum.dt.year).mean().drop(columns='datum')

def main():

    st.set_page_config(layout="wide")
    st.title('Stavy')

    csvs = list_s3_csvs()

    if not csvs:
        st.write('Files in data directory not found.')
        return

    if filename := st.selectbox('Select File', csvs):
        col1, col2, col3 = st.columns(3)

        col1.header(f'{filename} - Absolute')
        df = fetch_csv(filename)
        df = transform_df(df)
        min_dt = df['datum'].min()
        col1.dataframe(df)

        col2.header('Diffs')
        diff_df = get_diff_df(df)
        col2.dataframe(diff_df)

        col3.header('Avg Diff')
        avg_df = get_avg_df(diff_df)
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
                    title_text=f'{col.capitalize()} - Absolute',
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
                    title_text=f'{col.capitalize()} - Diffs',
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