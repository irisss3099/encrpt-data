import streamlit as st
import hashlib
import base64

# Page settings
st.set_page_config(page_title="🔐 Secure Vault", page_icon="🛡️", layout="centered")

# Background & Styling
st.markdown("""
    <style>
    body {
        background-image: url("https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1470&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .stApp {
        background-color: rgba(255, 255, 255, 0.88);
        border-radius: 15px;
        padding: 30px;
    }
    h1, h3 {
        color: #003366;
    }
    footer {
        visibility: hidden;
    }
    .custom-footer {
        text-align: center;
        color: #555;
        font-size: 0.9em;
        margin-top: 50px;
    }
    </style>
""", unsafe_allow_html=True)


# Session states
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "users" not in st.session_state:
    st.session_state.users = {}
if "stored_data" not in st.session_state:
    st.session_state.stored_data = []
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

# Helper functions
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

def caesar_encrypt(text, shift=3):
    return "".join(chr((ord(char) - (65 if char.isupper() else 97) + shift) % 26 + (65 if char.isupper() else 97))
                   if char.isalpha() else char for char in text)

def caesar_decrypt(text, shift=3):
    return caesar_encrypt(text, -shift)

def encrypt_file(file):
    return base64.b64encode(file.read()).decode()

def decrypt_file(data):
    return base64.b64decode(data.encode())

# Title
st.markdown("<h1 style='text-align: center;'>🔐 Secure Data Encryption System</h1>", unsafe_allow_html=True)

# Sidebar
menu = ["🏠 Home", "📝 Register", "🔑 Login", "🗂️ Store Data", "🔍 Retrieve Data", "🚪 Logout"]
choice = st.sidebar.radio("Navigate", menu)

# Home
if choice == "🏠 Home":
    st.markdown("<h3 style='text-align: center;'>Welcome to your personal secure vault!</h3>", unsafe_allow_html=True)

# Register
elif choice == "📝 Register":
    st.subheader("📝 Create a New Account")
    new_user = st.text_input("Choose a username:")
    new_pass = st.text_input("Choose a password:", type="password")
    if st.button("✅ Register"):
        if new_user in st.session_state.users:
            st.error("🚫 Username already exists.")
        elif new_user and new_pass:
            st.session_state.users[new_user] = hash_passkey(new_pass)
            st.success("✅ Registration successful. Please login.")
        else:
            st.warning("⚠️ Please provide both username and password.")

# Login
elif choice == "🔑 Login":
    if st.session_state.is_logged_in:
        st.success(f"✅ Already logged in as {st.session_state.username}")
    else:
        username = st.text_input("Username:")
        password = st.text_input("Password:", type="password")
        if st.button("🔓 Login"):
            if username in st.session_state.users and st.session_state.users[username] == hash_passkey(password):
                st.session_state.is_logged_in = True
                st.session_state.username = username
                st.session_state.failed_attempts = 0
                st.success(f"✅ Welcome back, {username}!")
            else:
                st.error("❌ Invalid credentials.")

# Logout
elif choice == "🚪 Logout":
    if st.session_state.is_logged_in:
        st.subheader("⚠️ Confirm Logout")
        if st.button("✅ Yes, Log Me Out"):
            st.session_state.is_logged_in = False
            st.session_state.username = ""
            st.success("👋 You have successfully logged out.")
    else:
        st.info("ℹ️ You're already logged out.")

# Store Data
elif choice == "🗂️ Store Data":
    if not st.session_state.is_logged_in:
        st.warning("🔐 Please log in to store data.")
    else:
        st.subheader("📥 Store Data")
        data_type = st.selectbox("Select data type to store:", ["Text", "Image", "PDF"])
        passkey = st.text_input("Enter a secure passkey:", type="password")

        if data_type == "Text":
            text_data = st.text_area("Enter your sensitive text:")
            if st.button("🔐 Encrypt & Save"):
                if text_data and passkey:
                    encrypted = caesar_encrypt(text_data)
                    st.session_state.stored_data.append({
                        "username": st.session_state.username,
                        "type": "text",
                        "data": encrypted,
                        "passkey": hash_passkey(passkey)
                    })
                    st.success("✅ Text encrypted and stored.")
                    st.code(encrypted)
                else:
                    st.error("⚠️ Text and passkey required.")

        elif data_type in ["Image", "PDF"]:
            uploaded_file = st.file_uploader("Upload your file", type=["jpg", "jpeg", "png", "pdf"])
            if st.button("🔐 Encrypt & Save"):
                if uploaded_file and passkey:
                    encrypted = encrypt_file(uploaded_file)
                    st.session_state.stored_data.append({
                        "username": st.session_state.username,
                        "type": data_type.lower(),
                        "data": encrypted,
                        "filename": uploaded_file.name,
                        "passkey": hash_passkey(passkey)
                    })
                    st.success(f"✅ {data_type} encrypted and stored.")
                else:
                    st.error("⚠️ File and passkey required.")

# Retrieve Data
elif choice == "🔍 Retrieve Data":
    if not st.session_state.is_logged_in:
        st.warning("🔐 Please log in to retrieve your data.")
    else:
        st.subheader("🔓 Retrieve Data")
        passkey = st.text_input("Enter your passkey:", type="password")
        if st.button("🔍 Decrypt"):
            hashed = hash_passkey(passkey)
            found = False
            for entry in st.session_state.stored_data:
                if entry["username"] == st.session_state.username and entry["passkey"] == hashed:
                    found = True
                    st.success(f"✅ Decrypted {entry['type'].capitalize()}:")
                    if entry["type"] == "text":
                        st.code(caesar_decrypt(entry["data"]))
                    elif entry["type"] == "image":
                        st.image(decrypt_file(entry["data"]))
                    elif entry["type"] == "pdf":
                        st.download_button("📄 Download PDF", decrypt_file(entry["data"]), file_name=entry["filename"])
            if not found:
                st.session_state.failed_attempts += 1
                attempts_left = 3 - st.session_state.failed_attempts
                if attempts_left <= 0:
                    st.warning("🚫 Too many failed attempts. You have been logged out.")
                    st.session_state.is_logged_in = False
                else:
                    st.error(f"❌ Incorrect passkey. Attempts left: {attempts_left}")

# Footer
st.markdown('<div class="custom-footer">Developed by Sabila Aleem 💗</div>', unsafe_allow_html=True)
