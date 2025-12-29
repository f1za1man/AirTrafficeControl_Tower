# streamlit_app.py
# Air Traffic Control System — Streamlit version with pre-stored Pakistani logs + auto-save

import streamlit as st

# ===================== PAGE CONFIG =====================
st.set_page_config(page_title="Air Traffic Control System", page_icon="🛫", layout="wide")

MAX_QUEUE = 50

# ===================== FILE SAVE =====================
def save_files():
    # Save airports
    with open("airports.txt", "w", encoding="utf-8") as af:
        for a in st.session_state.airports:
            af.write(f'{a["code"]} {a["status"]} {a["weather"]} {int(a["runwayAvailable"])}\n')

    # Save flights
    with open("flights.txt", "w", encoding="utf-8") as ff:
        for f in st.session_state.flights:
            ff.write(f'{f["number"]} {f["source"]} {f["destination"]} '
                     f'{f["type"]} {f["category"]} {int(f["emergency"])}\n')

    # Save requests
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
    ]

if "flights" not in st.session_state:
    st.session_state.flights = [
        {"number": "PK-301", "source": "KHI", "destination": "LHE", "type": "Departure", "category": "Domestic", "emergency": False},
        {"number": "PK-302", "source": "LHE", "destination": "ISB", "type": "Arrival", "category": "Domestic", "emergency": False},
        {"number": "PK-401", "source": "KHI", "destination": "DXB", "type": "Departure", "category": "International", "emergency": False},
        {"number": "PK-501", "source": "ISB", "destination": "JED", "type": "Departure", "category": "International", "emergency": False},
    ]

if "requests" not in st.session_state:
    st.session_state.requests = [
        {"flightNumber": "PK-301", "type": "Takeoff", "emergency": False},
        {"flightNumber": "PK-302", "type": "Landing", "emergency": True},
    ]

# Save immediately on startup
auto_save()

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

# ===================== AIRPORT & FLIGHT =====================
if menu == "Airport & Flight Management":
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Add Airport")
        with st.form("add_airport", clear_on_submit=True):
            code = st.text_input("Airport Code (e.g., KHI)").strip()
            submitted = st.form_submit_button("Add")
            if submitted:
                if not validate_airport_code(code):
                    st.error("Invalid code!")
                else:
                    st.session_state.airports.insert(0, {"code": code, "status": "Open", "weather": "Clear", "runwayAvailable": True})
                    auto_save()
                    st.success("Airport added!")

        st.subheader("View Airports")
        st.table([{"Code": a["code"], "Status": a["status"], "Runway": "Available" if a["runwayAvailable"] else "Occupied", "Weather": a["weather"]} for a in st.session_state.airports])

        st.subheader("Delete Airport")
        with st.form("delete_airport"):
            del_code = st.text_input("Enter Airport Code").strip()
            del_submit = st.form_submit_button("Delete")
            if del_submit:
                a = find_airport(del_code)
                if a is None:
                    st.error("Airport not found!")
                else:
                    delete_airport_and_associated_flights(del_code)
                    st.success("Airport and associated flights deleted!")

    with col_right:
        st.subheader("Add Flight")
        with st.form("add_flight", clear_on_submit=True):
            fn = st.text_input("Flight Number (PK-123)").strip()
            src = st.text_input("Source Airport").strip()
            dest = st.text_input("Destination Airport").strip()
            type_ = st.text_input("Type (Arrival/Departure)").strip()
            cat = st.text_input("Category (Domestic/International)").strip()
            f_submit = st.form_submit_button("Add Flight")
            if f_submit:
                if not validate_flight_number(fn):
                    st.error("Invalid flight number!")
                else:
                    st.session_state.flights.insert(0, {"number": fn, "source": src, "destination": dest, "type": type_, "category": cat, "emergency": False})
                    auto_save()
                    st.success("Flight added!")

        st.subheader("View Flights")
        st.table([{"Number": f["number"], "Route": f'{f["source"]}->{f["destination"]}', "Type": f["type"], "Category": f["category"], "Emergency": "Yes" if f["emergency"] else "No"} for f in st.session_state.flights])

        st.subheader("Delete Flight")
        with st.form("delete_flight"):
            del_fn = st.text_input("Enter Flight Number").strip()
            del_f_submit = st.form_submit_button("Delete")
            if del_f_submit:
                f = find_flight(del_fn)
                if f is None:
                    st.error("Flight not found!")
                else:
                    st.session_state.flights = [x for x in st.session_state.flights if x["number"] != del_fn]
                    auto_save()
                    st.success("Flight deleted!")

# ===================== RUNWAY =====================
elif menu == "Runway & ATC":
    st.subheader("Runway Status")
    st.table([{"Airport": a["code"], "Runway": "Available" if a["runwayAvailable"] else "Occupied"} for a in st.session_state.airports])

    st.subheader("Assign Runway")
    codes = [a["code"] for a in st.session_state.airports]
    selected_code = st.selectbox("Select Airport", options=codes)
    if st.button("Assign Runway"):
        a = find_airport(selected_code)
        if not a["runwayAvailable"]:
            st.error("Runway already occupied!")
        else:
            a["runwayAvailable"] = False
            auto_save()
            st.success("Runway assigned!")

# ===================== PILOT REQUESTS =====================
elif menu == "Pilot Requests":
    st.subheader("Submit Request")
    with st.form("submit_request", clear_on_submit=True):
        pr_fn = st.text_input("Flight Number").strip()
        pr_type = st.text_input("Type (Landing/Takeoff)").strip()
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
                # Update corresponding flight emergency flag if exists
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
                if pr["emergency"]:
                    st.error(f'Processing {pr["flightNumber"]} | {pr["type"]} | Emergency: Yes')
                else:
                    st.success(f'Processing {pr["flightNumber"]} | {pr["type"]} | Emergency: No')
            st.session_state.requests = []  # clear queue
            auto_save()
            st.info("All requests processed and queue cleared.")

# ===================== WEATHER & STATUS =====================
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

# ===================== AIRPORT STATUS BOARD =====================
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
