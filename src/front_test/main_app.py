import streamlit as st
import requests
import subprocess

# Base URL for the FastAPI application
BASE_URL = "http://localhost:8000/api/auth"

# Streamlit App State
class State:
    current_page = "Sign Up"
    redirect_to_login = False
    redirect_to_main = False
    user_info = {}

state = State()

# Function to sign up a new user
def signup():
    st.title("Sign Up")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    api_key = st.text_input("ApiKey")

    if st.button("Sign Up"):
        if password == confirm_password:
            data = {
                "username": username,
                "email": email,
                "password": password,
                "api_key": api_key
            }
            response = requests.post(f"{BASE_URL}/signup", json=data)
            st.write("Response Status Code:", response.status_code)
            # st.write("Response Content:", response.content.decode("utf-8"))
            try:
                # response_json = response.json()
                # st.write("Response JSON:", response_json)  # Print the entire JSON response for debugging
                message = response.status_code

                if message == 201:
                    st.success("Sign up successful! Please confirm your email and you may proceed with login!")
                    # Set the redirect flag to True
                    state.redirect_to_login = True

                else:
                    st.error("No message found in the response.")
            except KeyError:
                st.error("Unexpected response format. Please check the server response.")
        else:
            st.error("Passwords do not match.")

        # Check if redirection is required
        if getattr(state, 'redirect_to_login', False):
            # Reset the redirect flag
            state.redirect_to_login = True
            # Redirect to the login page
            state.current_page = "Log In"

# Function to log in a user
def login():
    st.title("Log In")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        data = {
            "username": email,
            "password": password
        }
        response = requests.post(f"{BASE_URL}/login", data=data)
        if response.status_code == 200:
            st.success("Log In Successful")
            state.redirect_to_main = True
            state.user_info = response.json().get("user_info")
            # st.json(response.json())


        else:
            st.error("Log In Failed")
            st.text(response.text)


        if getattr(state, 'redirect_to_main', False):
            # Reset the redirect flag
            state.redirect_to_main = False
            # Redirect to the main page
            st.experimental_set_query_params(page="Main Page")


def main_page():
    st.title("Main Page")


# Function to refresh the access token
def refresh_token():
    st.title("Refresh Token")
    refresh_token = st.text_input("Refresh Token")

    if st.button("Refresh Token"):
        headers = {"Authorization": f"Bearer {refresh_token}"}
        response = requests.get(f"{BASE_URL}/refresh_token", headers=headers)
        if response.status_code == 200:
            st.success("Token Refreshed Successfully")
            st.json(response.json())
        else:
            st.error("Token Refresh Failed")
            st.text(response.text)

# Function to confirm email
def confirmed_email():
    st.title("Confirm Email")
    token = st.text_input("Confirmation Token")

    if st.button("Confirm Email"):
        response = requests.get(f"{BASE_URL}/confirmed_email/{token}")
        st.json(response.json())

# Function to request email confirmation
def request_email():
    st.title("Request Email Confirmation")
    email = st.text_input("Email")

    if st.button("Request Email Confirmation"):
        data = {"email": email}
        response = requests.post(f"{BASE_URL}/request_email", json=data)
        st.json(response.json())

# Function to reset password
def reset_password():
    st.title("Reset Password")
    email = st.text_input("Email")

    if st.button("Reset Password"):
        data = {"email": email}
        response = requests.post(f"{BASE_URL}/reset_password", json=data)
        st.json(response.json())

# Function to confirm password reset
def password_reset_confirm():
    st.title("Password Reset Confirmation")
    token = st.text_input("Reset Password Token")

    if st.button("Confirm Password Reset"):
        response = requests.get(f"{BASE_URL}/password_reset_confirm/{token}")
        st.json(response.json())

# Function to update password
def update_password():
    st.title("Update Password")
    reset_password_token = st.text_input("Reset Password Token")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Update Password"):
        if new_password == confirm_password:
            data = {
                "reset_password_token": reset_password_token,
                "new_password": new_password,
                "confirm_password": confirm_password
            }
            response = requests.post(f"{BASE_URL}/set_new_password", json=data)
            st.json(response.json())
        else:
            st.error("Passwords do not match.")

# Streamlit App
def main():
    st.sidebar.title("FastAPI Streamlit App")
    selected_page = st.sidebar.selectbox("Select a page", ["Sign Up", "Log In", "Refresh Token",
                                                           "Confirm Email", "Request Email Confirmation",
                                                           "Reset Password", "Password Reset Confirmation",
                                                           "Update Password"])


    if selected_page == "Sign Up":
        signup()
    elif selected_page == "Log In":
        login()
    elif selected_page == "Refresh Token":
        refresh_token()
    elif selected_page == "Confirm Email":
        confirmed_email()
    elif selected_page == "Request Email Confirmation":
        request_email()
    elif selected_page == "Reset Password":
        reset_password()
    elif selected_page == "Password Reset Confirmation":
        password_reset_confirm()
    elif selected_page == "Update Password":
        update_password()

if __name__ == "__main__":
    main()

