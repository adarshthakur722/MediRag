import streamlit as st
from database import create_user, login_user


def initialize_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "page" not in st.session_state:
        st.session_state.page = "login"

    if "user" not in st.session_state:
        st.session_state.user = None


def login_page():

    st.title("🔐 Login")

    st.write("Welcome back!")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        login = st.button("Login", use_container_width=True)

    with col2:
        signup = st.button("Create Account", use_container_width=True)

    if signup:
        st.session_state.page = "signup"
        st.rerun()

    if login:

        if email == "" or password == "":
            st.warning("Please fill all fields.")
            return

        user = login_user(email, password)

        if user is None:
            st.error("Invalid email or password.")
        else:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.success("Login Successful!")
            st.rerun()


def signup_page():

    st.title("📝 Create Account")

    full_name = st.text_input("Full Name")

    username = st.text_input("Username")

    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password"
    )

    col1, col2 = st.columns(2)

    with col1:
        create = st.button(
            "Create Account",
            use_container_width=True
        )

    with col2:
        back = st.button(
            "Back to Login",
            use_container_width=True
        )

    if back:
        st.session_state.page = "login"
        st.rerun()

    if create:

        if (
            full_name == ""
            or username == ""
            or email == ""
            or password == ""
            or confirm_password == ""
        ):
            st.warning("Please fill all fields.")
            return

        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        success, message = create_user(
            full_name,
            username,
            email,
            password
        )

        if success:
            st.success(message)

            st.session_state.page = "login"

            st.rerun()

        else:
            st.error(message)


def logout():

    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.page = "login"

    st.rerun()


def authentication():

    initialize_session()

    if st.session_state.logged_in:
        return True

    if st.session_state.page == "login":
        login_page()

    else:
        signup_page()

    return False