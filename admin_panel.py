import streamlit as st
import pandas as pd
from utils.azure_storage import load_user_data, save_user_data

def run():
    if st.session_state.role not in ["Admin", "Super-Admin"]:
        st.warning("Access denied.")
        return

    users = load_user_data()

    # ---------- 🎯 Title Banner ----------
    with st.container():
        st.markdown(
            """
            <div style='background-color:#ccc5b9; padding:10px 25px; border-radius:15px; width:80%; margin:auto; text-align:center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <h3 style='margin:0; color:#333;'>⚙️ Admin Panel - Manage Users</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------- All Details Inside Standard Width ----------
    
    with st.container():
        st.markdown(
            """
            <div style='width:40%; margin:auto; background-color:#403d39; padding:10px 25px; border-radius:15px; margin-bottom:30px;'>
                <h4 style='text-align:center;'>➕ Add New User</h4>
            """,
            unsafe_allow_html=True )
        
        # Limiting width using columns (Streamlit doesn't support max-width directly on input, so we simulate it with columns)
        col1, col2, col3 = st.columns([1, 6, 1])  # middle column is 6x wider
        with col2:
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["User", "Admin"])

            if st.button("Create User"):
                if new_username in users:
                    st.error("Username already exists.")
                elif not new_username or not new_password:
                    st.error("Username and Password are required.")
                else:
                    users[new_username] = {"password": new_password, "role": new_role}
                    save_user_data(users)
                    st.success(f"✅ User `{new_username}` created successfully.")
                    st.rerun()
        st.markdown("---")
        st.markdown("</div>", unsafe_allow_html=True)

        # ------------------------------👥 Existing Users ------------------------------
        
        st.markdown("""
            <div style='width:40%; margin:auto; background-color:#403d39; padding:10px 25px; border-radius:15px; margin-bottom:30px;'>
                <h4 style='text-align:center;'> 👥 Existing Users</h4> """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 6, 1])  # middle column is 6x wider
        with col2:        
            user_list = [{"Username": uname, "Role": uinfo["role"]} for uname, uinfo in users.items()]
            df_users = pd.DataFrame(user_list)
            st.dataframe(df_users, use_container_width=True)

        st.markdown("---")

        # ------------------------------ 🛠️ Modify/Delete User ------------------------------
        
        st.markdown("""
            <div style='width:40%; margin:auto; background-color:#403d39; padding:10px 25px; border-radius:15px; margin-bottom:30px;'>
                <h4 style='text-align:center;'> 🛠️ Modify/Delete User </h4> """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 6, 1])  # middle column is 6x wider
        with col2:
        
            mod_user = st.selectbox("Select user", list(users.keys()))

            if mod_user:
                if mod_user == st.session_state.username:
                    st.info("You cannot modify or delete your own account.")
                elif mod_user == "Shivank":
                    st.warning("Super Admin cannot be modified or deleted.")
                else:
                    updated_role = st.selectbox("Change Role", ["User", "Admin"], index=["User", "Admin"].index(users[mod_user]["role"]))
                    if st.button("Update Role"):
                        users[mod_user]["role"] = updated_role
                        save_user_data(users)
                        st.success(f"Role updated for `{mod_user}` to `{updated_role}`.")
                        st.rerun()
                    if st.button("Delete User"):
                        del users[mod_user]
                        save_user_data(users)
                        st.success(f"User `{mod_user}` deleted.")
                        st.rerun()

        # Close container div
        st.markdown("</div>", unsafe_allow_html=True)
