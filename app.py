import streamlit as st
import pandas as pd
import os
import pyrebase
import time
import base64
import hashlib

file_paths_with_titles = {
    "TIMBAO-BUKAL-BUKAL CIS.xlsx": "TIMBAO-BUKAL",
    "2 row.xlsx": "DILA",
    "Ma. Pelaez.xlsx": "Ma. Pelaez",
    "Puypuy.xlsx": "Puypuy",
    "Bangyas.xlsx": "Bangyas"
}

# Define a list of file paths
file_paths = ["TIMBAO-BUKAL-BUKAL CIS.xlsx", "2 row.xlsx", "Ma. Pelaez.xlsx", "Puypuy.xlsx", "Bangyas.xlsx"]
num_files = len(file_paths)

# Function to read and display the Excel file based on the current index
def display_inventory(file_index):
    # Read the Excel file
    df_inventory = pd.read_excel(file_paths[file_index])
    title = file_paths_with_titles.get(file_paths[file_index], "Unknown Title")
    st.markdown(f"## {title}")
    # Display the contents of the Excel file
    st.write(df_inventory)

def hash_pin(pin):
    # Encode the PIN as bytes
    pin_bytes = pin.encode('utf-8')
    # Hash the PIN using SHA-256 algorithm
    hashed_pin = hashlib.sha256(pin_bytes).hexdigest()
    return hashed_pin


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

def search_inventory(search_query):
    # Clear the previous output
    st.session_state.search_query = search_query
    st.session_state.search_result_found = False
    st.session_state.search_result_container = None

    # Clear the sidebar background image
    st.sidebar.markdown("")
    
    # Clear the previous inventory display
    st.markdown("")

    # Initialize a variable to track if any search result is found
    search_result_found = False

    # Check if the search query is empty
    if not search_query:
        st.warning("Please enter a search query.")
        return

    # Search for the title in the file_paths_with_titles dictionary
    for file_path, title in file_paths_with_titles.items():
        if search_query.lower() in title.lower():
            # If the title matches the search query, display the data of the corresponding file
            df_inventory = pd.read_excel(file_path)
            result_container = st.container()
            st.session_state.search_result_container = result_container
            with result_container:
                st.markdown(f"## {title}")
                st.write(df_inventory)
            search_result_found = True

    # Update the session state with the search result status
    st.session_state.search_result_found = search_result_found

    # If no matching title is found, display a message
    if not search_result_found:
        st.warning("No matching title found.")

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
            df = pd.read_csv(csv_file_path, encoding='latin1', on_bad_lines='skip')
            
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

    if 'file_index' not in st.session_state:
        st.session_state.file_index = 0

    # Create a session state object
    if 'user' not in st.session_state:
        st.session_state.user = None  # Initialize st.session_state.user to None


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
        menu_selection = st.sidebar.selectbox(":blue[Select Option]", ["READ", "INVENTORY", "CREATE", "EDIT", "DELETE", "FARMER"])
        page_number = st.session_state.get('page_number', 1)

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
                
                # Calculate total number of rows and pages
                total_rows = len(df)
                num_pages = (total_rows + 9) // 10  # Ceiling division to get total number of pages

                # Input field to specify the page number
                page_number = st.number_input("Page Number", min_value=1, max_value=num_pages, value=page_number, key='page-number')

                # Calculate start and end indices for pagination
                start_index = (page_number - 1) * 10
                end_index = min(start_index + 10, total_rows)

                # Display the subset of rows for the specified page
                if total_rows > 0:
                    st.dataframe(df.iloc[start_index:end_index].reset_index(drop=True))
                else:
                    st.warning("No matching rows found.")
                
                # Display pagination information
                st.write(f"Showing page {page_number} of {num_pages}")

                # JavaScript for pagination
                pagination_script = """
                    <script>
                        function goToPage() {
                            var pageNumber = document.getElementById("page-number").value;
                            window.location.href = "?page=" + pageNumber;
                        }
                    </script>
                """
                st.markdown(pagination_script, unsafe_allow_html=True)

                # Download button for all pages
                if st.button("Download All Pages"):
                    # Save the entire DataFrame to a CSV file
                    df.to_csv("all_pages_data.csv", index=False)
                    st.success("All pages data downloaded successfully!")

            except Exception as e:
                st.error(f"Error reading CSV file: {e}")
                # If an exception occurs, retain the page number in session state
                st.session_state.page_number = page_number

        elif menu_selection == "CREATE":

            # Function to authenticate user
            def authenticate_user(pin):
                if pin == "123456":  # Change the hardcoded PIN here
                    return True
                else:
                    return False

            # Container for styling
            create_container = st.container()

            with create_container:
                # Set the form width
                st.markdown('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
                st.markdown('<style>div.row-widget.stRadio > div > label{flex-direction:row;}</style>', unsafe_allow_html=True)
                st.markdown('<style>div.row-widget.stRadio > div > label > div{flex-direction:row;}</style>', unsafe_allow_html=True)
                st.markdown('<style>div.row-widget.stRadio > div > label > span{margin-top: 25px;}</style>', unsafe_allow_html=True)

                # PIN input field for authentication
                pin = st.text_input("Enter PIN to access create tab", type="password", key="pin_input")
                create_access_granted = False

                if pin:  # Check if the PIN is entered
                    if authenticate_user(pin):
                        create_access_granted = True
                    else:
                        st.error("Invalid PIN. Please try again.")

                if create_access_granted:
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

            def authenticate_user(pin):
                if pin == "123456":  # Change the hardcoded PIN here
                    return True
                else:
                    return False

            pin = st.text_input("Enter PIN to access edit tab", type="password", key="pin_input")
            edit_access_granted = False

            # Function to authenticate user
            if pin:  # Check if the PIN is entered
                if authenticate_user(pin):
                    edit_access_granted = True
                else:
                    st.error("Invalid PIN. Please try again.")
  
            if edit_access_granted:
                # Proceed with the edit tab content
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
            def authenticate_user(pin):
                if pin == "123456":  # Change the hardcoded PIN here
                    return True
                else:
                    return False

            pin = st.text_input("Enter PIN to access delete tab", type="password", key="pin_input")
            delete_access_granted = False

            # Function to authenticate user
            if pin:  # Check if the PIN is entered
                if authenticate_user(pin):
                    delete_access_granted = True
                else:
                    st.error("Invalid PIN. Please try again.")
        
            if delete_access_granted:
                # Proceed with the delete tab content
                delete_container = st.container()
                with delete_container:
                    # Read the CSV file
                    df = pd.read_csv(csv_file_path)

                    # Calculate total number of rows and pages
                    total_rows = len(df)
                    num_pages = (total_rows + 9) // 10  # Ceiling division to get total number of pages

                    # Input field to specify the page number
                    delete_page_number = st.number_input("Page Number", min_value=1, max_value=num_pages, value=1)

                    # Input field to specify the index of the entry to delete
                    delete_index = st.number_input("Index of Entry to Delete", min_value=0, placeholder="Enter index")

                    # Button to show the data of the entry
                    show_data_button_clicked = st.button("Show Data")

                    if show_data_button_clicked:
                        try:
                            # Calculate the actual index in the DataFrame based on the provided page number and index
                            actual_index = (delete_page_number - 1) * 10 + delete_index

                            # Check if the index is within the range of the DataFrame
                            if 0 <= actual_index < len(df):
                                # Show the data of the entry at the specified index in a table
                                st.write("Data of Entry:")
                                st.write(df.iloc[actual_index:actual_index+1])  # Displaying only the chosen entry as a DataFrame
                            else:
                                st.warning("Index out of range.")
                        except Exception as e:
                            st.error(f"Error displaying entry: {e}")

                    # Button to delete the entry
                    delete_button_clicked = st.button("Delete Entry")

                    if delete_button_clicked:
                        try:
                            # Calculate the actual index in the DataFrame based on the provided page number and index
                            actual_index = (delete_page_number - 1) * 10 + delete_index

                            # Check if the index is within the range of the DataFrame
                            if 0 <= actual_index < len(df):
                                # Delete the entry at the specified index
                                df = df.drop(actual_index)

                                # Save the modified DataFrame back to CSV
                                df.to_csv(csv_file_path, index=False)
                                st.success("Entry deleted successfully!")
                            else:
                                st.warning("Index out of range.")
                        except Exception as e:
                            st.error(f"Error deleting entry: {e}")

        elif menu_selection == "INVENTORY":
            # Upload functionality
            st.markdown("## Upload New Excel File")
            uploaded_file = st.file_uploader("Choose an Excel file", type=["xls", "xlsx"])

            if uploaded_file is not None:
                try:
                    # Read the uploaded Excel file
                    new_df = pd.read_excel(uploaded_file)
                    
                    # Save the DataFrame to a new Excel file
                    new_excel_file_path = f"new_inventory_{int(time.time())}.xlsx"  # Generate a unique file name
                    new_df.to_excel(new_excel_file_path, index=False)
                    
                    st.success("Excel file uploaded and saved successfully!")
                except Exception as e:
                    st.error(f"Error uploading Excel file: {e}")

            # Search functionality
            search_query = st.text_input("Search", key="inventory_search_input")

            if st.button("Search", key="inventory_search_button"):
                search_inventory(search_query)

            # Display the default inventory table if no search query is entered
            if not search_query:
                display_inventory(st.session_state.file_index)

            # Next button to cycle through files
            if st.button("Next"):
                st.session_state.file_index = (st.session_state.file_index + 1) % num_files


        elif menu_selection == "FARMER":
            st. markdown ("Name of Presidents")

            farmer_menu_selection = st.selectbox(":green[SELECT TOWN]", ["PILA", "STA CRUZ", "VICTORIA"])


        if st.session_state.user is not None:
                # Add logout button
            if st.sidebar.button("Logout"):
                logout()




if __name__ == "__main__":
    main()