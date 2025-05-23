import pandas as pd
import streamlit as st
import json
from azure.storage.blob import BlobServiceClient
from io import StringIO

connection_string = "DefaultEndpointsProtocol=https;AccountName=ecoadls;AccountKey=RyxI1xmK4Apcvpq8wucB3Zv8vMB6f5OpjUjOA5q9Y7490HR9Q5bUBW4nLsKg23hGJDokm3ozvVBk+AStheaw3A==;EndpointSuffix=core.windows.net"
container_name = "hr-admin/ticket"
users_blob = "users.json"
queries_blob = "queries.csv"

blob_service_client = BlobServiceClient.from_connection_string(connection_string)

def get_blob(blob_name):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    return blob_client

#@st.cache_data
def load_user_data():
    try:
        data = get_blob(users_blob).download_blob().readall()
        return json.loads(data)
    except:
        # 🟢 Default Super Admin is hardcoded here
        return {"Shivank": {"password": "Shanks@241456", "role": "Super-Admin"}}

def save_user_data(users):
    data = json.dumps(users)
    get_blob(users_blob).upload_blob(data, overwrite=True)

#@st.cache_data
def load_queries():
    try:
        csv_data = get_blob(queries_blob).download_blob().readall().decode("utf-8")
        return pd.read_csv(StringIO(csv_data))
    except:
        return pd.DataFrame(columns=[
            "Date & Time Added","Platform", "Customer Name", "Contact Number", "Location", "Query",
            "Query Resolved Date", "Remark", "My Response", "Resolve In Time",
            "Status", "SLA", "Alert Type"
        ])

def save_queries(df):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    get_blob(queries_blob).upload_blob(csv_buffer.getvalue(), overwrite=True)
