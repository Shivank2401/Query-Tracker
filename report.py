import streamlit as st
import pandas as pd
from utils.azure_storage import load_queries

def filter_queries(df, role, username):
    if role == "Super Admin":
        return df
    return df[df["Query Assigned To"] == username]

def export_csv(dataframe, filename, key):
    csv = dataframe.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"📥 Download {filename}",
        data=csv,
        file_name=f"{filename}.csv",
        mime="text/csv",
        key=key
    )

def run():
    st.title("📑 Export Reports")

    with st.container():
        st.markdown("<div style='max-width: 900px; margin: auto;'>", unsafe_allow_html=True)

        df = st.session_state.get("users_data")
        if df is None:
            df = load_queries()

        role = st.session_state.get("role", "")
        username = st.session_state.get("username", "")

        df_filtered = filter_queries(df, role, username)

        st.subheader(f"Hello, {role}")
        st.info("Select a report below to export as CSV:")

        all_queries = df_filtered
        open_queries = df_filtered[df_filtered["Status"] == "Open"]
        closed_queries = df_filtered[df_filtered["Status"] == "Closed"]

        st.markdown("### 📊 All Queries")
        export_csv(all_queries, "All_Queries_Report", key="all_queries")

        st.markdown("### ✅ Open Queries")
        export_csv(open_queries, "Open_Queries_Report", key="open_queries")

        st.markdown("### 🏁 Closed Queries")
        export_csv(closed_queries, "Closed_Queries_Report", key="closed_queries")

        st.markdown("</div>", unsafe_allow_html=True)
