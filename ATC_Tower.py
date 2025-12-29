# streamlit_app.py
# Air Traffic Control System — Streamlit version with:
# ✅ Pre-stored Pakistani logs (Domestic + International flights)
# ✅ Auto-save after every operation
# ✅ Blue theme + single airplane background
# ✅ Separate viewing options for Domestic vs International flights

import streamlit as st

# ===================== PAGE CONFIG =====================
st.set_page_config(page_title="Air Traffic Control System", page_icon="🛫", layout="wide")

MAX_QUEUE = 50

# ===================== DESIGN FUNCTIONS =====================
def set_background(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def set_blue_theme():
    st.markdown(
        """
        <style>
        .stApp {
            color: #e6f0ff;
            background-color: #001f3f;
        }
        h1, h2, h3, h4 {
            color: #66b2ff;
        }
        .stButton>button {
            background-color: #004080;
            color: white;
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# ===================== FILE SAVE =====================
def save_files():
    with open("airports.txt", "w", encoding="utf-8") as af:
        for a in st.session_state.airports:
            af.write(f'{a["code"]} {a["status"]} {a["weather"]} {int(a["runwayAvailable"])}\n')

    with open("flights.txt", "w", encoding="utf-8") as ff:
        for f in st.session_state.flights:
            ff.write(f'{f["number"]} {f["source"]} {f["destination"]} '
                     f'{f["type"]} {f["category"]} {int(f["emergency"])}\n')

    with open("requests.txt", "w", encoding="utf-8") as rf:
        for pr in st.session_state.requests:
            rf.write(f'{pr["flightNumber"]} {pr["type"]} {int(pr["emergency"])}\n')

def auto_save():
    save_files()

# ===================== VALIDATION =====================
def validate_airport_code(code: str) -> bool:
    return len(code) == 3 and all(c.isupper() for c in code)

def validate_flight_number(fn: str) -> bool:
    if len(fn) < 4 or len(fn) > 6: return False
    if not (fn[0].isupper() and fn[1].isupper() and fn[2] == '-'): return False
    return all(c.isdigit() for c in fn[3:])

def find_airport(code: str):
    for a in st.session_state.airports:
        if a["code"] == code: return a
    return None

def find_flight(number: str):
    for f in st.session_state.flights:
        if f["number"] == number: return f
    return None

def delete_airport_and_associated_flights(code: str):
    st.session_state.flights = [f for f in st.session_state.flights if f["source"] != code and f["destination"] != code]
    st.session_state.airports = [a for a in st.session_state.airports if a["code"] != code]
    auto_save()

# ===================== PRE-STORED LOGS =====================
if "airports" not in st.session_state:
    st.session_state.airports = [
        {"code": "KHI", "status": "Open", "weather": "Clear", "runwayAvailable": True},
        {"code": "LHE", "status": "Open", "weather": "Rain", "runwayAvailable": True},
        {"code": "ISB", "status": "Open", "weather": "Fog", "runwayAvailable": False},
        {"code": "PEW", "status": "Open", "weather": "Clear", "runwayAvailable": True},
        {"code": "SKT", "status": "Open", "weather": "Clear", "runwayAvailable": True},
    ]

if "flights" not in st.session_state:
    st.session_state.flights = [
        # --- Domestic flights (5–7) ---
        {"number": "PK-301", "source": "KHI", "destination": "LHE", "type": "Departure", "category": "Domestic", "emergency": False},
        {"number": "PK-302", "source": "LHE", "destination": "ISB", "type": "Arrival", "category": "Domestic", "emergency": False},
        {"number": "PK-303", "source": "ISB", "destination": "PEW", "type": "Departure", "category": "Domestic", "emergency": False},
        {"number": "PK-304", "source": "SKT", "destination": "KHI", "type": "Arrival", "category": "Domestic", "emergency": False},
        {"number": "PK-305", "source": "PEW", "destination": "LHE", "type": "Departure", "category": "Domestic", "emergency": False},
        {"number": "PK-306", "source": "KHI", "destination": "SKT", "type": "Arrival", "category": "Domestic", "emergency": False},

        # --- International flights (7–8) ---
        {"number": "PK-401", "source": "KHI", "destination": "DXB", "type": "Departure", "category": "International", "emergency": False},
        {"number": "PK-402", "source": "LHE", "destination": "LHR", "type": "Departure", "category": "International", "emergency": False},
        {"number": "PK-403", "source": "ISB", "destination": "JED", "type": "Departure", "category": "International", "emergency": False},
        {"number": "PK-404", "source": "PEW", "destination": "DOH", "type": "Departure", "category": "International", "emergency": False},
        {"number": "PK-405", "source": "KHI", "destination": "IST", "type": "Departure", "category": "International", "emergency": False},
        {"number": "PK-406", "source": "LHE", "destination": "DXB", "type": "Arrival", "category": "International", "emergency": False},
        {"number": "PK-407", "source": "ISB", "destination": "RUH", "type": "Departure", "category": "International", "emergency": False},
    ]

if "requests" not in st.session_state:
    st.session_state.requests = [
        {"flightNumber": "PK-301", "type": "Takeoff", "emergency": False},
        {"flightNumber": "PK-302", "type": "Landing", "emergency": True},
    ]

auto_save()

# ===================== DESIGN INIT =====================
set_blue_theme()

# 👉 Use one static airplane image here
set_background("https://images.pexels.com/photos/358319/pexels-photo-358319.jpeg?cs=srgb&dl=pexels-pixabay-358319.jpg&fm=jpg")

# ===================== UI =====================
st.title("🛫 Air Traffic Control Tower")

menu = st.sidebar.radio(
    "Main Menu",
    [
        "Airport & Flight Management",
        "Runway & ATC",
        "Pilot Requests",
        "Weather & Airport Status",
        "Airport Status Board",
    ],
    index=0
)

# ===================== (rest of your menus: Airport & Flight, Runway, Pilot Requests, Weather, Status Board) =====================
# Keep the same logic as we finalized earlier, with auto_save after each operation
