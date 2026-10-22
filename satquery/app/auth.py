import os

from dotenv import load_dotenv
from supabase import create_client


load_dotenv()


def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    try:
        import streamlit as st

        if not url:
            url = st.secrets.get("SUPABASE_URL")

        if not key:
            key = st.secrets.get("SUPABASE_KEY")
    except Exception:
        pass

    if not url or not key:
        raise ValueError("Supabase credentials are not configured.")

    return create_client(url, key)


def signup(email, password):
    supabase = get_supabase()

    return supabase.auth.sign_up({
        "email": email,
        "password": password
    })


def login(email, password):
    supabase = get_supabase()

    return supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })


def logout():
    supabase = get_supabase()
    supabase.auth.sign_out()
