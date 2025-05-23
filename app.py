import streamlit as st
from streamlit_option_menu import option_menu
import importlib
from utils.auth import login, logout, is_authenticated

# ---------- Page Mapping (page label -> python file without .py) ----------
PAGES = {
    "Dashboard": "dashboard",
    "All Queries": "queries",
    "Reports": "report",           # Alerts logic is handled inside queries.py
    "Admin Panel": "admin_panel"
}

def main():

    st.set_page_config(page_title="Query Tracker", layout="wide")
    
    # ---------- Login Check ----------
    if not is_authenticated():
        login()
    else:
        # ---------- Sidebar Navigation ----------
        with st.sidebar:
            st.markdown(f"**👤 Welcome, {st.session_state.username}**")
            
            # Role-based Menu
            menu_options = ["Dashboard", "All Queries", "Reports"]
            if st.session_state.role in ["Admin", "Super-Admin"]:
                menu_options.append("Admin Panel")

            selected = option_menu("Query Tracker", options=menu_options, 
                                   icons=["bar-chart", "list-task", "bell", "gear"], 
                                   default_index=0)

            # Logout Button
            if st.button("🔓 Logout"):
                logout()
                st.rerun()

        # ---------- Dynamic Page Loading ----------
        if selected:
            page_module_name = PAGES[selected]
            try:
                module = importlib.import_module(page_module_name)
                module.run()  # Each page must have a `run()` function
            except ModuleNotFoundError:
                st.error(f"🔴 Module `{page_module_name}.py` not found.")
            except AttributeError:
                st.error(f"🔴 `{page_module_name}.py` must have a `run()` function.")

if __name__ == "__main__":
    main()
