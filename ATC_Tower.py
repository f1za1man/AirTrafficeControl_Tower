# streamlit_app.py
# Air Traffic Control System — Streamlit version with:
# ✅ Pre-stored Pakistani logs (Domestic + International flights)
# ✅ Auto-save after every operation
# ✅ Blue theme + single airplane background (no slideshow; no duplicate element errors)
# ✅ Full CRUD: airports, flights, weather, runways, pilot requests
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
        /* Improve readability on background */
        .block-container {{
            background: rgba(0, 20, 40, 0.35);
            border-radius: 12px;
            padding: 1.2rem;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def set_blue_theme():
    st.markdown(
        """
        <style>
        .stApp { color: #e6f0ff; background-color: #001f3f; }
        h1, h2, h3, h4 { color: #66b2ff; }
        .stButton>button { background-color: #004080; color: white; border-radius: 8px; border: 1px solid #66b2ff; }
        .stSelectbox, .stRadio label, .stTextInput>div>div>input { color: #e6f0ff !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

def save_files():
    with open("airports.txt", "w", encoding="utf-8") as af:
        for a in st.session_state.airports:
            af.write(f'{a["code"]} {a["status"]} {a["weather"]} {int(a["runwayAvailable"])}\n')

    with open("flights.txt", "w", encoding="utf-8") as ff:
        for f in st.session_state.flights:
            ff.write(
                f'{f["number"]} {f["source"]} {f["destination"]} '
                f'{f["type"]} {f["category"]} {int(f["emergency"])}\n'
            )

    with open("requests.txt", "w", encoding="utf-8") as rf:
        for pr in st.session_state.requests:
            rf.write(f'{pr["flightNumber"]} {pr["type"]} {int(pr["emergency"])}\n')

def auto_save():
    save_files()

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
        # Domestic (6)
        {"number": "PK-301", "source": "KHI", "destination": "LHE", "type": "Departure", "category": "Domestic", "emergency": False},
        {"number": "PK-302", "source": "LHE", "destination": "ISB", "type": "Arrival",  "category": "Domestic", "emergency": False},
        {"number": "PK-303", "source": "ISB", "destination": "PEW", "type": "Departure", "category": "Domestic", "emergency": False},
        {"number": "PK-304", "source": "SKT", "destination": "KHI", "type": "Arrival",   "category": "Domestic", "emergency": False},
        {"number": "PK-305", "source": "PEW", "destination": "LHE", "type": "Departure", "category": "Domestic", "emergency": False},
        {"number": "PK-306", "source": "KHI", "destination": "SKT", "type": "Arrival",   "category": "Domestic", "emergency": False},
        # International (7)
        {"number": "PK-401", "source": "KHI", "destination": "DXB", "type": "Departure", "category": "International", "emergency": False},
        {"number": "PK-402", "source": "LHE", "destination": "LHR", "type": "Departure", "category": "International", "emergency": False},
        {"number": "PK-403", "source": "ISB", "destination": "JED", "type": "Departure", "category": "International", "emergency": False},
        {"number": "PK-404", "source": "PEW", "destination": "DOH", "type": "Departure", "category": "International", "emergency": False},
        {"number": "PK-405", "source": "KHI", "destination": "IST", "type": "Departure", "category": "International", "emergency": False},
        {"number": "PK-406", "source": "LHE", "destination": "DXB", "type": "Arrival",   "category": "International", "emergency": False},
        {"number": "PK-407", "source": "ISB", "destination": "RUH", "type": "Departure", "category": "International", "emergency": False},
    ]

if "requests" not in st.session_state:
    st.session_state.requests = [
        {"flightNumber": "PK-301", "type": "Takeoff", "emergency": False},
        {"flightNumber": "PK-302", "type": "Landing", "emergency": True},
    ]

auto_save()

set_blue_theme()
set_background("https://images.pexels.com/photos/358319/pexels-photo-358319.jpeg?cs=srgb&dl=pexels-pixabay-358319.jpg&fm=jpg")

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

if menu == "Airport & Flight Management":
    col_left, col_right = st.columns(2)

    # Airports
    with col_left:
        st.subheader("Add Airport")
        with st.form("add_airport", clear_on_submit=True):
            code = st.text_input("Airport Code (e.g., KHI)").strip()
            submitted = st.form_submit_button("Add")
            if submitted:
                if not validate_airport_code(code):
                    st.error("Invalid code! Use 3 uppercase letters (e.g., KHI).")
                elif find_airport(code) is not None:
                    st.error("Airport already exists.")
                else:
                    st.session_state.airports.insert(0, {
                        "code": code, "status": "Open", "weather": "Clear", "runwayAvailable": True
                    })
                    auto_save()
                    st.success("Airport added!")

        st.subheader("View Airports")
        st.table([
            {
                "Code": a["code"],
                "Status": a["status"],
                "Runway": "Available" if a["runwayAvailable"] else "Occupied",
                "Weather": a["weather"]
            } for a in st.session_state.airports
        ])

        st.subheader("Delete Airport")
        with st.form("delete_airport"):
            del_code = st.text_input("Enter Airport Code").strip()
            del_submit = st.form_submit_button("Delete")
            if del_submit:
                a = find_airport(del_code)
                if a is None:
                    st.error("Airport not found!")
                else:
                    # Remove associated flights
                    st.session_state.flights = [
                        f for f in st.session_state.flights
                        if f["source"] != del_code and f["destination"] != del_code
                    ]
                    # Remove airport
                    st.session_state.airports = [
                        x for x in st.session_state.airports if x["code"] != del_code
                    ]
                    auto_save()
                    st.success("Airport and associated flights deleted!")

        st.subheader("Toggle Airport Status / Release Runway")
        codes = [a["code"] for a in st.session_state.airports]
        if len(codes):
            sel_code = st.selectbox("Select Airport", options=codes, key="airport_manage_select")
            a = find_airport(sel_code)
            colA, colB = st.columns(2)
            with colA:
                if st.button(f'Toggle Status (Currently: {a["status"]})'):
                    a["status"] = "Closed" if a["status"] == "Open" else "Open"
                    auto_save()
                    st.success(f'Status set to {a["status"]}')
            with colB:
                if st.button("Release Runway"):
                    a["runwayAvailable"] = True
                    auto_save()
                    st.success("Runway released (Available)")

    # Flights
    with col_right:
        st.subheader("Add Flight")
        with st.form("add_flight", clear_on_submit=True):
            fn   = st.text_input("Flight Number (PK-123)").strip()
            src  = st.text_input("Source Airport").strip()
            dest = st.text_input("Destination Airport").strip()
            type_ = st.selectbox("Type", ["Arrival", "Departure"])
            cat   = st.selectbox("Category", ["Domestic", "International"])
            f_submit = st.form_submit_button("Add Flight")
            if f_submit:
                if not validate_flight_number(fn):
                    st.error("Invalid flight number! Format: XX-123 (uppercase + dash + digits).")
                elif find_flight(fn) is not None:
                    st.error("Flight already exists.")
                else:
                    st.session_state.flights.insert(0, {
                        "number": fn, "source": src, "destination": dest,
                        "type": type_, "category": cat, "emergency": False
                    })
                    auto_save()
                    st.success("Flight added!")

        st.subheader("View Flights")
        view_choice = st.radio("Choose view:", ["All Flights", "Domestic Only", "International Only"])
        if view_choice == "All Flights":
            flights_to_show = st.session_state.flights
        elif view_choice == "Domestic Only":
            flights_to_show = [f for f in st.session_state.flights if f["category"] == "Domestic"]
        else:
            flights_to_show = [f for f in st.session_state.flights if f["category"] == "International"]

        if len(flights_to_show) == 0:
            st.warning("No flights found for this category.")
        else:
            st.table([
                {
                    "Number": f["number"],
                    "Route": f'{f["source"]}->{f["destination"]}',
                    "Type": f["type"],
                    "Category": f["category"],
                    "Emergency": "Yes" if f["emergency"] else "No"
                } for f in flights_to_show
            ])

        st.subheader("Delete Flight")
        with st.form("delete_flight"):
            del_fn = st.text_input("Enter Flight Number").strip()
            del_f_submit = st.form_submit_button("Delete")
            if del_f_submit:
                f = find_flight(del_fn)
                if f is None:
                    st.error("Flight not found!")
                else:
                    st.session_state.flights = [
                        x for x in st.session_state.flights if x["number"] != del_fn
                    ]
                    auto_save()
                    st.success("Flight deleted!")

elif menu == "Runway & ATC":
    st.subheader("Runway Status")
    st.table([
        {"Airport": a["code"], "Runway": "Available" if a["runwayAvailable"] else "Occupied"}
        for a in st.session_state.airports
    ])

    st.subheader("Assign Runway")
    codes = [a["code"] for a in st.session_state.airports]
    if len(codes) == 0:
        st.warning("No airports available.")
    else:
        selected_code = st.selectbox("Select Airport", options=codes)
        if st.button("Assign Runway"):
            a = find_airport(selected_code)
            if a is None:
                st.error("Airport not found!")
            elif not a["runwayAvailable"]:
                st.error("Runway already occupied!")
            else:
                a["runwayAvailable"] = False
                auto_save()
                st.success("Runway assigned!")

elif menu == "Pilot Requests":
    st.subheader("Submit Request")
    with st.form("submit_request", clear_on_submit=True):
        pr_fn = st.text_input("Flight Number").strip()
        pr_type = st.selectbox("Type", ["Landing", "Takeoff"])
        pr_emergency = st.checkbox("Emergency?")
        pr_submit = st.form_submit_button("Submit Request")
        if pr_submit:
            if len(st.session_state.requests) >= MAX_QUEUE:
                st.error("Queue full!")
            else:
                st.session_state.requests.append({
                    "flightNumber": pr_fn,
                    "type": pr_type,
                    "emergency": pr_emergency
                })
                f = find_flight(pr_fn)
                if f is not None:
                    f["emergency"] = pr_emergency
                auto_save()
                st.success("Request submitted!")

    st.subheader("Current Queue")
    if len(st.session_state.requests) == 0:
        st.info("No pending requests!")
    else:
        st.table([
            {"Flight": pr["flightNumber"], "Type": pr["type"], "Emergency": "Yes" if pr["emergency"] else "No"}
            for pr in st.session_state.requests
        ])

    st.subheader("Process Requests")
    if st.button("Process All Requests"):
        if len(st.session_state.requests) == 0:
            st.warning("No pending requests!")
        else:
            for pr in st.session_state.requests:
                msg = f'Processing {pr["flightNumber"]} | {pr["type"]} | Emergency: '
                if pr["emergency"]:
                    st.error(msg + "Yes")
                else:
                    st.success(msg + "No")
            st.session_state.requests = []
            auto_save()
            st.info("All requests processed and queue cleared.")

elif menu == "Weather & Airport Status":
    st.subheader("Update Weather")
    if len(st.session_state.airports) == 0:
        st.warning("No airports added yet.")
    else:
        codes = [a["code"] for a in st.session_state.airports]
        code_sel = st.selectbox("Airport Code", options=codes)
        weather_sel = st.selectbox("Weather", options=["Clear", "Rain", "Fog"], index=0)
        if st.button("Update Weather"):
            a = find_airport(code_sel)
            if a is None:
                st.error("Airport not found!")
            else:
                a["weather"] = weather_sel
                auto_save()
                st.success("Weather updated!")

elif menu == "Airport Status Board":
    st.subheader("Airport Status Board")
    if len(st.session_state.airports) == 0:
        st.warning("No airports added yet!")
    else:
        st.table([
            {
                "Code": a["code"],
                "Status": a["status"],
                "Runway": "Available" if a["runwayAvailable"] else "Occupied",
                "Weather": a["weather"]
            } for a in st.session_state.airports
        ])
