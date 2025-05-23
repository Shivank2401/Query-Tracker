import streamlit as st
import pandas as pd
from datetime import datetime
from utils.azure_storage import load_queries, save_queries, load_user_data
import uuid

# ✅ Helper function to render queries with edit buttons
def render_query_rows(df_to_render, prefix=""):
    for index, row in df_to_render.iterrows():
        cols = st.columns([1, 20])

        with cols[0]:
            if st.button("✏️", key=f"{prefix}_edit_{row['Query ID']}"):
                st.session_state.show_add_form = True
                st.session_state.edit_mode = True
                st.session_state.edit_index = index
                st.session_state.edit_data = row.to_dict()
                st.rerun()

        with cols[1]:
            st.dataframe(df_to_render.loc[[index]], use_container_width=True, hide_index=True)

# ------------------------------------------------------------- Query Tracker Page -------------------------------------------------------------

def run():
    # Initialize session states
    for key, default in {
        "show_add_form": False,
        "edit_mode": False,
        "edit_index": None,
        "edit_data": {},
        "new_query_id": str(uuid.uuid4())
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    with st.container():
        st.markdown(
            """
            <div style='background-color:#073349; padding:10px 25px; border-radius:15px; width:80%; margin:auto; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <h3 style='margin:0; color:#ffffff;'>📋 All Queries</h3>  </div> """,unsafe_allow_html=True )

    st.markdown("<br>", unsafe_allow_html=True)

    df = load_queries()
    users_data = load_user_data()
    user_list = [u for u in users_data.keys() if users_data[u]["role"] in ["User", "Admin"]]
    user_list.sort()

    if "df" not in st.session_state:
        st.session_state.df = df.copy()

    col_spacer, col_left, col4, col5, col_right1, col_right2 = st.columns([4, 3, 3, 3, 3, 3])

    with col_left:
        if st.button("➕ Add New Query"):
            st.session_state.show_add_form = True
            st.session_state.edit_mode = False
            st.session_state.new_query_id = str(uuid.uuid4())

    with col5:
        search_query = st.text_input("🔍 Search", placeholder="Enter keyword to search")
        if search_query:
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]

    with col_right2:
        alert_filter = st.selectbox("Alert Filter", ["All", "Safe", "Critical", "Warning"], key="alert_filter_global")
        if alert_filter != "All":
            df = df[df["Alert Type"] == alert_filter]

    if st.session_state.role == "User":
        df = df[df["Query Assigned To"] == st.session_state.username]

    tab_all, tab_open, tab_inprog, tab_closed = st.tabs(["All", "Open", "In-Progress", "Closed"])

    with tab_all:
        st.subheader("🔍 All Queries")
        render_query_rows(df, prefix="all")

    with tab_open:
        st.subheader("🟢 Open Queries")
        df_open = df[df["Status"].str.lower() == "open"]
        render_query_rows(df_open, prefix="open")

    with tab_inprog:
        st.subheader("🟠 In-Progress Queries")
        df_prog = df[df["Status"].str.lower().isin(["in-progress", "in progress"])]
        render_query_rows(df_prog, prefix="progress")

    with tab_closed:
        st.subheader("🔴 Closed Queries")
        df_closed = df[df["Status"].str.lower() == "closed"]
        render_query_rows(df_closed, prefix="closed")

    if st.session_state.get("show_add_form", False):
        render_add_query_form(users_data)

# ------------------------------------------------------------- Add / Edit Query Form -------------------------------------------------------------
def render_add_query_form(users_data):
    user_list = [u for u in users_data if users_data[u]["role"] in ["User", "Admin"]]
    user_list.sort()
    st.markdown("---")
    st.subheader("✍️ Edit Query" if st.session_state.edit_mode else "➕ Add New Query")
    col1, col2 = st.columns(2)

    data = st.session_state.edit_data if st.session_state.edit_mode else {}

    with col1:
        query_id = st.text_input("Query ID", value=st.session_state.new_query_id, disabled=True)
        date_added = st.text_input("Date & Time Added", value=data.get("Date & Time Added", datetime.now().strftime("%d-%b-%Y %H:%M:%S")))
        platform = st.selectbox("Platform*", ["Call", "Website", "Quick Api", "Email", "Bulk Enquiry: US Website", "Other"], index=0 if not data else ["Call", "Website", "Quick Api", "Email", "Bulk Enquiry: US Website", "Other"].index(data.get("Platform", "Call")))
        name = st.text_input("Customer Name*", value=data.get("Customer Name", ""))
        contact = st.text_input("Contact Number*", value=data.get("Contact Number", ""))
        location = st.text_input("Location*", value=data.get("Location", ""))
        query = st.text_area("Query*", value=data.get("Query", ""))

    with col2:
        resolved_date_obj = st.date_input("Query Resolved Date", format="DD/MM/YYYY")
        resolved_date = resolved_date_obj.strftime("%d-%b-%Y")
        remark = st.text_input("Remark", value=data.get("Remark", ""))
        response = st.text_input("My Response", value=data.get("My Response", ""))
        resolve_in = st.text_input("Resolve In Time", value=data.get("Resolve In Time", ""))
        status = st.selectbox("Status", ["Open", "In Progress", "Closed"], index=["Open", "In Progress", "Closed"].index(data.get("Status", "Open")))
        sla = st.text_input("SLA", value=data.get("SLA", ""))
        alert = st.selectbox("Alert Type", ["Safe", "Critical", "Warning"], index=["Safe", "Critical", "Warning"].index(data.get("Alert Type", "Safe")))
        query_added_by = st.text_input("Query Added By", value=st.session_state.username, disabled=True)

    if st.session_state.role == "User":
        query_assigned_to = st.text_input("Query Assigned To", value=st.session_state.username, disabled=True)

    elif st.session_state.role == "Admin":
        assignable_users = [u for u in users_data if users_data[u]["role"] in ["User", "Admin"]]
        if st.session_state.username not in assignable_users:
            assignable_users.append(st.session_state.username)
        query_assigned_to = st.selectbox(
            "Query Assigned To", 
            assignable_users,
            index=assignable_users.index(data.get("Query Assigned To", st.session_state.username)) if data.get("Query Assigned To", st.session_state.username) in assignable_users else 0
        )

    elif st.session_state.role == "Super-Admin":
        assignable_users = [u for u in users_data if users_data[u]["role"] in ["User", "Admin", "Super-Admin"]]
        if st.session_state.username not in assignable_users:
            assignable_users.append(st.session_state.username)
        query_assigned_to = st.selectbox(
            "Query Assigned To", 
            assignable_users,
            index=assignable_users.index(data.get("Query Assigned To", st.session_state.username)) if data.get("Query Assigned To", st.session_state.username) in assignable_users else 0
        )


    submit_col, cancel_col = st.columns([1, 1])

    with submit_col:
        if st.button("✅ Submit Query"):
            if not all([platform, name, contact, location, query]):
                st.warning("Please fill all required fields.")
            else:
                new_data = {
                    "Query ID": st.session_state.new_query_id,
                    "Date & Time Added": date_added,
                    "Platform": platform,
                    "Customer Name": name,
                    "Contact Number": contact,
                    "Location": location,
                    "Query": query,
                    "Query Resolved Date": resolved_date,
                    "Remark": remark,
                    "My Response": response,
                    "Resolve In Time": resolve_in,
                    "Status": status,
                    "SLA": sla,
                    "Alert Type": alert,
                    "Query Added By": query_added_by,
                    "Query Assigned To": query_assigned_to
                }

                full_df = load_queries()
                if st.session_state.edit_mode:
                    full_df.loc[full_df["Query ID"] == st.session_state.new_query_id] = new_data
                else:
                    full_df = pd.concat([full_df, pd.DataFrame([new_data])], ignore_index=True)

                save_queries(full_df)
                st.success("✅ Query saved successfully.")
                st.session_state.show_add_form = False
                st.session_state.edit_mode = False
                st.rerun()

    with cancel_col:
        if st.button("❌ Cancel"):
            st.session_state.show_add_form = False
            st.session_state.edit_mode = False
            st.rerun()
