import streamlit as st
import pandas as pd
import os
import pyrebase
import time
import base64

def get_img_as_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def set_background(background_image_path):
    background_image_ext = 'png'  # Modify the extension if needed
    encoded_image = base64.b64encode(open(background_image_path, "rb").read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url('data:image/{background_image_ext};base64,{encoded_image}');
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def sidebar_bg(side_bg):
    try:
        # Get the file extension
        _, side_bg_ext = os.path.splitext(side_bg)
        # Read the image file and encode it as base64
        with open(side_bg, "rb") as img_file:
            img_data = img_file.read()
            encoded_img = base64.b64encode(img_data).decode()
        # Set the background style for the sidebar
        st.markdown(
            f"""
            <style>
            [data-testid="stSidebar"] > div:first-child {{
                background: url(data:image/{side_bg_ext};base64,{encoded_img}) !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
    except FileNotFoundError:
        st.error(f"Image file '{side_bg}' not found.")
    except Exception as e:
        st.error(f"Error: {e}")

side_bg = "static/image1.jpg"
sidebar_bg(side_bg)


# Firebase initialization
firebaseConfig = {
    'apiKey': "AIzaSyAF25avieiXm9XIZezYaL1JCEAux0-Gl1w",
    'authDomain': "nia-mis.firebaseapp.com",
    'projectId': "nia-mis",
    'storageBucket': "nia-mis.appspot.com",
    'messagingSenderId': "333239771011",
    'appId': "1:333239771011:web:51f1310ff4894b6cc0e0b6",
    'measurementId': "G-SND6D820B7",
    'databaseURL': ''
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Function to authenticate user
def authenticate(email, password):
    try:
        login = auth.sign_in_with_email_and_password(email, password)
        return login
    except Exception as e:
        error_message = str(e)
        if "INVALID_PASSWORD" in error_message:
            st.error("Invalid password. Please check your password.")
            time.sleep(2)
        elif "INVALID_EMAIL" in error_message:
            st.error("Invalid email address. Please check your email.")
            time.sleep(2)
        else:
            st.error("Please make sure if your email is correct")
            time.sleep(2)
        return None
    
# Function to send a password reset email
def send_password_reset_email(email):
    if not email:
        st.error("Please, input email.")
        time.sleep(2)
        return

    try:
        auth.send_password_reset_email(email)
        st.success("Password reset email sent.")
        time.sleep(2)
    except Exception as e:
        error_message = str(e)
        if "INVALID_EMAIL" in error_message:
            st.error("Invalid email address. Please check your email.")
            time.sleep(2)
        elif "MISSING_EMAIL" in error_message:
            st.error("Missing email address. Please enter your email.")
            time.sleep(2)
        else:
            st.error(f"Error sending password reset email: {e}")
            time.sleep(2)


# Function to logout user
def logout():
    # Clear user info from session state
    st.session_state.user = None


def save_to_csv(new_entry, csv_file_path):
    try:
        # Check if the CSV file already exists
        if os.path.exists(csv_file_path):
            # Read the existing CSV file
            df = pd.read_csv(csv_file_path)
            
            # Check if the new entry already exists in the DataFrame
            if df.equals(pd.DataFrame([new_entry])):
                st.warning("Entry already exists.")
                return
            
            # Append the new entry to the DataFrame
            df = df.append(new_entry, ignore_index=True)
        else:
            # If the file doesn't exist, create a new DataFrame with the new entry
            df = pd.DataFrame([new_entry])

        # Save the DataFrame to CSV
        df.to_csv(csv_file_path, index=False)
        st.success("Entry saved successfully!")
    except Exception as e:
        st.error(f"Error saving entry: {e}")

def edit_entry(index, edited_entry, csv_file_path):
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path)

        # Update the entry at the specified index
        df.loc[index] = edited_entry

        # Save the DataFrame back to CSV
        df.to_csv(csv_file_path, index=False)
        st.success("Entry edited successfully!")
    except Exception as e:
        st.error(f"Error editing entry: {e}")

# Streamlit app content
def main():
    background_image_path = "static/2nd.png"  # Adjust the path accordingly
    global csv_file_path  # Declare csv_file_path as a global variable
    csv_file_path = r'sample.csv'

    # Create a session state object
    if 'user' not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        st.markdown("<h1 style=' color: #545454;'>LOGIN</h1>", unsafe_allow_html=True)

        st.markdown(
        """
        <style>
        .st-emotion-cache-q8sbsg p {
            color: black;
        }
        .st-emotion-cache-16idsys p{
            color: #545454;
        }
        button.st-emotion-cache-hc3laj.ef3psqc12 {
            background-color: #2ECC71;
            position: relative;
            border: 1px solid black;
            margin: 0;
            color: #fff;
            display: inline-block;
            text-decoration: none;
            text-align: center;
        }
        .st-b2 {
        background-color: white;
        }
            button.st-emotion-cache-13ejsyy.ef3psqc12{
            background-color: #2f9e36;
            color: #fff;
            transition: 0.2s;
            height: 2.5rem;
        }
        div.st-emotion-cache-1wmy9hl.e1f1d6gn0{
            width: 325px;
            height: 400px;
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            margin: 20px;
            padding: 10px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            left: 30px;
            border: 3px solid #73AD21;
            border-radius: 2rem;
            margin-top: 90px;
        }
        .st-bo{
            width: 300px;
        }
        .st-emotion-cache-10trblm{
            font-size: 25px;
            text-align: center;
            margin-right: 20px;
        }
        .st-emotion-cache-1vbkxwb p{
            font-size: 12px;
            text-align: center;
        }
        button.st-emotion-cache-7ym5gk.ef3psqc12{
           
            height: 1px;
        }
        .st-gw{
            height: auto;
            width: 300px;
        }
        .st-h9{
            
        }
        .dataframe tbody tr:nth-child(odd) {
            background-color: #f2f2f2;
        }
        .dataframe tbody tr:nth-child(even) {
            background-color: #dddddd;
        }
        table.dataframe {
            font-size: 20px;
            text-align: left;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

        set_background(background_image_path)
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")

        login_button_clicked = st.button("LOGIN", key="login_button")
        reset_button_clicked = st.button("Forgot Password", key="reset_button")

        if login_button_clicked:
            if email and password:
                user = authenticate(email, password)
                if user:
                    st.session_state.user = user
                    st.success("Login successful.")
                    time.sleep(1)
            else:
                st.error("Please enter both email and password.")
                time.sleep(2)
        if reset_button_clicked:
            send_password_reset_email(email)


    else:
        st.sidebar.image("static/[Hi-Res] BAGONG PILIPINAS LOGO.png", use_column_width=True)

        st.sidebar.markdown("## :blue[Menu]")


        # Dropdown menu with options
        menu_selection = st.sidebar.selectbox(":blue[Select Option]", ["READ", "CREATE", "EDIT", "DELETE"])

        if menu_selection == "READ":
        
            try:
                # Read the CSV file with a specified encoding and skip problematic lines
                df = pd.read_csv(csv_file_path, encoding='latin1', error_bad_lines=False)

                st.markdown("<h3>Search</h3>", unsafe_allow_html=True)
                search_query = st.text_input("", "")
                if search_query:
                    # Convert all columns to string type
                    df = df.astype(str)
                    # Filter the DataFrame based on the search query
                    df = df[df.apply(lambda row: row.str.contains(search_query, case=False)).any(axis=1)]
                
                # Display the DataFrame with increased width and font size
                st.dataframe(df.style.set_table_styles([{'selector': 'td', 'props': [('font-size', '18px')]}]), width=2000)
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")

        elif menu_selection == "CREATE":

            # Container for styling
            create_container = st.container()

            with create_container:
                # Set the form width
                st.markdown('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
                st.markdown('<style>div.row-widget.stRadio > div > label{flex-direction:row;}</style>', unsafe_allow_html=True)
                st.markdown('<style>div.row-widget.stRadio > div > label > div{flex-direction:row;}</style>', unsafe_allow_html=True)
                st.markdown('<style>div.row-widget.stRadio > div > label > span{margin-top: 25px;}</style>', unsafe_allow_html=True)
                
                # Input fields for creating a new entry
                name_of_cis = st.text_input("Name of CIS", placeholder="Enter CIS name")
                location = st.text_input("Location", placeholder="Enter location")
                source_of_water = st.text_input("Source of Water", placeholder="Enter water source")
                scheme_of_irrigation = st.text_input("Scheme of Irrigation", placeholder="Enter irrigation scheme")
                service_area = st.number_input("Service Area (Has.)", min_value=0.0, placeholder="Enter service area")
                firmed_up_service_area = st.number_input("Firmed-Up Service Area (Has.)", min_value=0.0, placeholder="Enter firmed-up service area")
                operational_area = st.number_input("Operational Area (Has.)", min_value=0.0, placeholder="Enter operational area")
                no_of_farmer_beneficiaries = st.number_input("No. of Farmer Beneficiaries", min_value=0, placeholder="Enter number of farmer beneficiaries")
                name_of_ia = st.text_input("Name of IA", placeholder="Enter IA name")
                main_canals = st.text_input("Main Canal(s)", placeholder="Enter main canals")
                laterals = st.text_input("Lateral(s) & Sub-Lateral(s)", placeholder="Enter laterals and sub-laterals")

                # Create button to submit the form
                create_button_clicked = st.button("Create Entry")

                if create_button_clicked:
                    # Create a dictionary with the user inputs
                    new_entry = {
                        "Name of CIS": name_of_cis,
                        "Location": location,
                        "Source of Water": source_of_water,
                        "Scheme of Irrigation": scheme_of_irrigation,
                        "Service Area (Has.)": service_area,
                        "Firmed-Up Service Area (Has.)": firmed_up_service_area,
                        "Operational Area (Has.)": operational_area,
                        "No. of Farmer Beneficiaries": no_of_farmer_beneficiaries,
                        "Name of IA": name_of_ia,
                        "Main Canal(s)": main_canals,
                        "Lateral(s) & Sub-Lateral(s)": laterals
                    }
                    # Save the new entry to CSV file
                    save_to_csv(new_entry, csv_file_path)
                    st.success("Entry created successfully!")
                    # Print the new entry (you can replace this with your preferred way of saving the data)
                    st.write("New Entry:", new_entry)

        elif menu_selection == "EDIT":

            # Container for styling
            edit_container = st.container()

            with edit_container:
                # Input field to specify the index of the entry to edit
                edit_index = st.number_input("Index of Entry to Edit", min_value=0, placeholder="Enter index")

                # Read the CSV file to retrieve data of the chosen index
                try:
                    df = pd.read_csv(csv_file_path)
                    if edit_index < len(df):
                        # Display the data of the chosen index in input fields
                        name_of_cis = st.text_input("Name of CIS", value=df.loc[edit_index, "Name of CIS"])
                        location = st.text_input("Location", value=df.loc[edit_index, "Location"])
                        source_of_water = st.text_input("Source of Water", value=df.loc[edit_index, "Source of Water"])
                        scheme_of_irrigation = st.text_input("Scheme of Irrigation", value=df.loc[edit_index, "Scheme of Irrigation"])
                        service_area = st.number_input("Service Area (Has.)", value=df.loc[edit_index, "Service Area (Has.)"])
                        firmed_up_service_area = st.number_input("Firmed-Up Service Area (Has.)", value=df.loc[edit_index, "Firmed-Up Service Area (Has.)"])
                        operational_area = st.number_input("Operational Area (Has.)", value=df.loc[edit_index, "Operational Area (Has.)"])
                        no_of_farmer_beneficiaries = st.number_input("No. of Farmer Beneficiaries", value=df.loc[edit_index, "No. of Farmer Beneficiaries"])
                        name_of_ia = st.text_input("Name of IA", value=df.loc[edit_index, "Name of IA"])
                        main_canals = st.text_input("Main Canal(s)", value=df.loc[edit_index, "Main Canal(s)"])
                        laterals = st.text_input("Lateral(s) & Sub-Lateral(s)", value=df.loc[edit_index, "Lateral(s) & Sub-Lateral(s)"])

                        # Button to apply changes
                        apply_changes_button_clicked = st.button("Apply Changes")

                        if apply_changes_button_clicked:
                            # Create a dictionary with the edited entry
                            edited_entry = {
                                "Name of CIS": name_of_cis,
                                "Location": location,
                                "Source of Water": source_of_water,
                                "Scheme of Irrigation": scheme_of_irrigation,
                                "Service Area (Has.)": service_area,
                                "Firmed-Up Service Area (Has.)": firmed_up_service_area,
                                "Operational Area (Has.)": operational_area,
                                "No. of Farmer Beneficiaries": no_of_farmer_beneficiaries,
                                "Name of IA": name_of_ia,
                                "Main Canal(s)": main_canals,
                                "Lateral(s) & Sub-Lateral(s)": laterals
                            }
                            # Apply changes to the entry at the specified index
                            edit_entry(edit_index, edited_entry, csv_file_path)
                    else:
                        st.warning("Index out of range.")
                except Exception as e:
                    st.error(f"Error reading CSV file: {e}")

        elif menu_selection == "DELETE":

            # Container for styling
            delete_container = st.container()

            with delete_container:
                # Input field to specify the index of the entry to delete
                delete_index = st.number_input("Index of Entry to Delete", min_value=0, placeholder="Enter index")

                # Button to delete the entry
                delete_button_clicked = st.button("Delete Entry")

                if delete_button_clicked:
                    try:
                        # Read the CSV file
                        df = pd.read_csv(csv_file_path)

                        # Check if the index is within the range of the DataFrame
                        if delete_index < len(df):
                            # Delete the entry at the specified index
                            df = df.drop(delete_index)

                            # Save the modified DataFrame back to CSV
                            df.to_csv(csv_file_path, index=False)
                            st.success("Entry deleted successfully!")
                        else:
                            st.warning("Index out of range.")
                    except Exception as e:
                        st.error(f"Error deleting entry: {e}")


        if st.session_state.user is not None:
                # Add logout button
            if st.sidebar.button("Logout"):
                logout()




if __name__ == "__main__":
    main()