import streamlit as st
import requests
# import subprocess

# Base URL for the FastAPI application
BASE_URL = "http://localhost:8000/api/auth"

# Streamlit App State

class State:
    current_page = "Sign Up"
    redirect_to_login = False
    redirect_to_main = False
    user_info = False

# state = State()



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
                    # state.redirect_to_login = True

                else:
                    st.error("No message found in the response.")
            except KeyError:
                st.error("Unexpected response format. Please check the server response.")
        else:
            st.error("Passwords do not match.")

        # Check if redirection is required
        # if getattr(state, 'redirect_to_login', False):
        #     # Reset the redirect flag
        #     state.redirect_to_login = True
        #     # Redirect to the login page
        #     state.current_page = "Log In"

# Function to log in a user
def login():
    state = State()
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
            state.user_info = True
            print(f"state.user_info: !!! IS {state.user_info}")
            # state.redirect_to_main = True
            # state.user_info = response.json().get("user_info")
            # st.json(response.json())
            # st.session_state.runpage = main_page
            return True

        else:
            st.error("Log In Failed")
            st.text(response.text)
            print(f"{state.user_info=}")
            return False

        # if getattr(state, 'redirect_to_main', False):
        #     # Reset the redirect flag
        #     state.redirect_to_main = False
        #     # Redirect to the main page
        #     st.experimental_set_query_params(page="Main Page")


def main_page(state):
    st.title("Main Page")
    # Check if the user is logged in
    if state.user_info:
        st.write("Welcome to the main page!")
        st.button("Log Out", on_click=lambda: state.__setattr__("user_info", False))
    else:
        st.write("Please log in to access the main page.")
        st.button("Log In", on_click=lambda: state.__setattr__("current_page", "Log In"))






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
# def reset_password(email: str):
#     st.title("Reset Password")
#     # email = st.text_input("Email")
#     email = email
#
#     if st.button("Reset Password"):
#         data = {"email": email}
#         response = requests.post(f"{BASE_URL}/reset_password", json=data)
#         st.json(response.json())
#
#         reset_password_token = response.json().get("reset_password_token")
#
#         return reset_password_token
#
#
# # Function to confirm password reset
# def password_reset_confirm():
#     st.title("Password Reset Confirmation")
#     email = st.text_input("Email")
#     token = reset_password(email)
#
#
#     if st.button("Confirm Password Reset"):
#         response = requests.get(f"{BASE_URL}/password_reset_confirm/{token}")
#         st.json(response.json())
#         result = response.json().get("token")
#         print(result)
#         return result
#
# # Function to update password
# def update_password():
#     st.title("Update Password")
#     reset_password_token = password_reset_confirm()
#     print(reset_password_token, type(reset_password_token))
#     new_password = st.text_input("New Password", type="password")
#     confirm_password = st.text_input("Confirm Password", type="password")
#
#     if st.button("Update Password"):
#         if new_password == confirm_password:
#             data = {
#                 "reset_password_token": reset_password_token,
#                 "new_password": new_password,
#                 "confirm_password": confirm_password
#             }
#             response = requests.post(f"{BASE_URL}/set_new_password", json=data)
#             st.json(response.json())
#         else:
#             st.error("Passwords do not match.")


# def reset_password(email):
#     data = {"email": email}
#     response = requests.post(f"{BASE_URL}/reset_password", json=data)
#     print(f"{response.json()}")
#     print(f'Message is: {response.json().get("message")}')


def reset_password(email):
    data = {"email": email}

    try:
        response = requests.post(f"{BASE_URL}/get_new_token", json=data)
        print(response.json())
        if response.status_code == 200:
            token = response.json().get("token")
            # print(f"TOKEN IS :::::: NOW::: ::: is: !!! {token=}")
            return token
        else:
            print(f"Failed to initiate password reset. Response: {response}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def password_reset_confirm(token):
    print(f"TOKEN:::{token}")
    response = requests.get(f"{BASE_URL}/password_reset_confirm/{token}")
    # answer = requests.post(f"{BASE_URL}/password_reset_confirm/{token}")
    # st.write(f"Password Reset Confirmation Response: {response.json().get('token')}")
    # st.write(f"Password Reset Confirmation Answer: {answer.json().get('token')}")
    print(f"Password Reset Confirmation Response: {response.json().get('token')}")
    # print((f"Password Reset Confirmation Answer: {answer.json().get('token')}"))
    # return response.json().get("token")
    return response.json().get("token")


def update_password(reset_password_token, new_password, confirm_password):
    st.title("Update Password")
    if new_password == confirm_password:
        data = {
            "reset_password_token": reset_password_token,
            "new_password": new_password,
            "confirm_password": confirm_password
        }
        response = requests.post(f"{BASE_URL}/set_new_password", json=data)
        st.json(response.json())
        return response.json()





def main():
    state = State()
    selected_page = None
    # user_info = None
    st.sidebar.title("FastAPI Streamlit App")

    # Add a radio button to choose between "Auth" and "Chat" options
    selected_option = st.sidebar.radio("Select an option:", ["Auth", "Chat"])

    # Based on the selected option, display different page choices
    if selected_option == "Auth":
        print(state.user_info)
        selected_page = st.sidebar.selectbox("Select a page", ["Sign Up", "Log In", "Refresh Token",
                                                               "Confirm Email", "Request Email Confirmation",
                                                               "Reset Password", "Password Reset Confirmation",
                                                               "Update Password"])

    elif selected_option == "Chat":
        # print(user_info)
        # Add your chat-related page choices here

        if not state.user_info:
            st.write("Login success !!!!!!!!!!!!!!")
            selected_page = st.sidebar.selectbox("Select a page for Chat",  ["Chat Page 1", "Chat Page 2", "Chat Page 3"])

        else:
            st.warning("Please log in to access the chat.")
            # selected_page = "Log In"


        # selected_page = st.sidebar.selectbox("Select a page for Chat", ["Chat Page 1", "Chat Page 2", "Chat Page 3"])





    if selected_page == "Sign Up":
        signup()
    elif selected_page == "Log In":
        state.user_info = login()
        # st.success("Login successfully")

    elif selected_page == "Request Email Confirmation":
        request_email()




    elif selected_page == "Password Reset Confirmation":
        st.title("Password Reset Flow")

        # Step 1: Reset Password
        email_for_reset = st.text_input("Enter your email for password reset:")
        reset_token = reset_password(email_for_reset)
        # st.write(f"Reset Password Token: {reset_token}")
        # if reset_token:
        #     st.success("Password reset initiated. ")
        #     st.write(f"Reset Password Token: {reset_token}")
        # else:
        #     st.error("Failed to initiate password reset.")

        # if st.button("Reset Password"):
        #     # reset_token = reset_password(email_for_reset)
        #     st.success("Password reset initiated. Check your email for instructions.")

        # Step 2: Confirm Password Reset
        if reset_token:
            st.success("Password reset initiated. ")
            st.write(f"Reset Password Token: {reset_token}")
            password_reset_confirm(reset_token)
            new_password = st.text_input("Enter your new password:", type="password")
            print(f"!!!!!!! !!!!First Pas {new_password}")
            confirm_password = st.text_input("Confirm your new password:")
            print(f"!!!!!!! !!!!!Second Pas {confirm_password}")
            # if st.button("Confirm Password Reset"):
            #     st.success("Password reset confirmed.")

                # Step 3: Update Password
                # confirmed_token = password_reset_confirm(email_for_reset, token_for_confirmation)
                # new_password = st.text_input("Enter your new password:", type="password")
                # print(f"!!!!!!! !!!!First Pas {new_password}")
                # confirm_password = st.text_input("Confirm your new password:")
                # print(f"!!!!!!! !!!!!Second Pas {confirm_password}")
            if st.button("Update Password"):
                # if new_password == confirm_password:
                    # Use the confirmed_token from the confirmation step
                    # confirmed_token = password_reset_confirm(email_for_reset, token_for_confirmation)
                update_password(reset_token, new_password, confirm_password)
                st.success("Password updated successfully.")



if __name__ == "__main__":
    main()