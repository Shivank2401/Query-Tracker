import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils.azure_storage import load_queries

def run():
    st.title("📊 Overview")

    st.markdown("---")

    df = st.session_state.get('users_data')
    if df is None:
        df = load_queries()

    # Convert date column upfront
    df['Date & Time Added'] = pd.to_datetime(df['Date & Time Added'], errors='coerce')

    def metric_box(label, value, bg_color, text_color="white", width="300px"):
        box_html = f"""
        <div style="
            background-color: {bg_color};
            color: {text_color};
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-family: 'Arial', sans-serif;
            width: {width};
            margin-left: auto;
            margin-right: auto;
            ">
            <div style="font-size:20px; font-weight:bold;">{label}</div>
            <div style="font-size:36px; font-weight:bold; margin-top:8px;">{value}</div>
        </div>
        """
        st.markdown(box_html, unsafe_allow_html=True)


    # Top row: Total, Open, Closed, In Progress
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_box("Total Queries", len(df), "#22577a")  # Blue
    with col2:
        metric_box("Open", df['Status'].eq('Open').sum(), "#2E8B57")  # Darker Blue
    with col3:
        metric_box("Closed", df['Status'].eq('Closed').sum(), "#38a3a5",) #text_color="#333")  # Yellow
    with col4:
        metric_box("In Progress", df['Status'].eq('In Progress').sum(), "#e09f3e")  # Gray

    # Add spacing after first row
    st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)

    # 2nd row: Safe, Critical, Warning Alert Type
    col5, col6, col7 = st.columns(3)
    with col5:
        metric_box("🟢 Safe", df['Alert Type'].eq('Safe').sum(), "#2E8B57")  # SeaGreen
    with col6:
        metric_box("🔴 Critical", df['Alert Type'].eq('Critical').sum(), "#B22222")  # FireBrick Red
    with col7:
        metric_box("🟠 Warning", df['Alert Type'].eq('Warning').sum(), "#FF8C00")  # DarkOrange

    # Add spacing after second row
    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    st.markdown("---")

    # Current week start and end
    today = datetime.now()
    start_of_week = today - pd.to_timedelta(today.weekday(), unit='d')  # Monday
    end_of_week = start_of_week + pd.Timedelta(days=6)  # Sunday

    df_current_week = df[(df['Date & Time Added'] >= start_of_week) & (df['Date & Time Added'] <= end_of_week)]

    # Group by date (day) and count queries
    daily_counts = df_current_week.groupby(df_current_week['Date & Time Added'].dt.date).size().reset_index(name='Total Queries')

    # Format date column to d-b-y (e.g., 23-May-25)
    daily_counts['DateStr'] = daily_counts['Date & Time Added'].apply(lambda x: x.strftime('%d-%b-%y'))

    col8, col9 = st.columns(2)
    with col8:
        fig = px.bar(daily_counts, x='DateStr', y='Total Queries', title='Current Week Daily Query Volume')
        fig.update_layout(xaxis_title='Date', yaxis_title='Total Queries')
        st.plotly_chart(fig, use_container_width=True)

    # Add spacing below chart
    st.markdown("<div style='margin-bottom:40px;'></div>", unsafe_allow_html=True)

    with col9:
        current_month = today.month
        username = st.session_state.get('username', None)
        if username:
            user_query_count = df[
                (df['Date & Time Added'].dt.month == current_month) &
                (df['Query Assigned To'] == username)
            ].shape[0]
        else:
            user_query_count = 0
        metric_box("📅 My Queries (This Month)", user_query_count, "#335c67")  # Dodger Blue

    # Add spacing below right box too
    st.markdown("<div style='margin-bottom:40px;'></div>", unsafe_allow_html=True)
