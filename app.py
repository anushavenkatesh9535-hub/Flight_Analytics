import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

# ----------------------------------------------------
# 1. INITIALIZE HIGH-PERFORMANCE IN-MEMORY DATABASE
# ----------------------------------------------------
if 'db_conn' not in st.session_state:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = conn.cursor()
    
    # Generate Database Schema
    cursor.execute("""
        CREATE TABLE airport (
            iata_code TEXT PRIMARY KEY,
            name TEXT,
            city TEXT,
            country TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE aircraft (
            registration TEXT PRIMARY KEY,
            model TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE flights (
            flight_number TEXT,
            airline_code TEXT,
            origin_iata TEXT,
            destination_iata TEXT,
            status TEXT,
            scheduled_departure TEXT,
            scheduled_arrival TEXT,
            aircraft_registration TEXT
        );
    """)
    
    # Inject Mock Data Payload
    airports_data = [
        ('DEL', 'Indira Gandhi International Airport', 'Delhi', 'India'),
        ('BOM', 'Chhatrapati Shivaji Maharaj Airport', 'Mumbai', 'India'),
        ('BLR', 'Kempegowda International Airport', 'Bengaluru', 'India'),
        ('HYD', 'Rajiv Gandhi International Airport', 'Hyderabad', 'India'),
        ('MAA', 'Chennai International Airport', 'Chennai', 'India'),
        ('LHR', 'London Heathrow Airport', 'London', 'United Kingdom'),
        ('SIN', 'Singapore Changi Airport', 'Singapore', 'Singapore'),
        ('SYD', 'Sydney Kingsford Smith Airport', 'Sydney', 'Australia'),
        ('JFK', 'John F. Kennedy International Airport', 'New York', 'United States'),
        ('LAX', 'Los Angeles International Airport', 'Los Angeles', 'United States')
    ]
    cursor.executemany("INSERT INTO airport VALUES (?,?,?,?);", airports_data)
    
    aircraft_data = [
        ('VT-EXX', 'Airbus A320'), ('VT-IND', 'Airbus A321neo'), 
        ('N104AA', 'Boeing 737-800'), ('G-XWBA', 'Airbus A350-1000'),
        ('9V-SMF', 'Airbus A350-900'), ('VH-VNJ', 'Boeing 787-9')
    ]
    cursor.executemany("INSERT INTO aircraft VALUES (?,?);", aircraft_data)
    
    flights_data = [
        ('6E 1605', '6E', 'BLR', 'DEL', 'Departed', '2026-06-12 10:00', '2026-06-12 12:45', 'VT-IND'),
        ('AI 2758', 'AI', 'BLR', 'DEL', 'Arrived', '2026-06-12 11:15', '2026-06-12 14:00', 'VT-EXX'),
        ('6E 5293', '6E', 'BLR', 'BOM', 'Departed', '2026-06-12 08:30', '2026-06-12 10:15', 'VT-IND'),
        ('VJ 1802', 'VJ', 'BLR', 'SIN', 'Departed', '2026-06-12 01:20', '2026-06-12 08:00', '9V-SMF'),
        ('AA 102', 'AA', 'JFK', 'LAX', 'Delayed', '2026-06-12 15:00', '2026-06-12 18:30', 'N104AA'),
        ('BA 115', 'BA', 'LHR', 'JFK', 'Canceled', '2026-06-12 16:20', '2026-06-12 19:50', 'G-XWBA'),
        ('SQ 421', 'SQ', 'SIN', 'BOM', 'Arrived', '2026-06-12 07:45', '2026-06-12 11:00', '9V-SMF'),
        ('QF 2', 'QF', 'SYD', 'LHR', 'Departed', '2026-06-12 18:00', '2026-06-13 05:00', 'VH-VNJ'),
        ('6E 839', '6E', 'BLR', 'DEL', 'Arrived', '2026-06-12 13:00', '2026-06-12 15:45', 'VT-IND'),
        ('AI 2016', 'AI', 'LHR', 'DEL', 'Arrived', '2026-04-05 06:44', '2026-04-05 18:30', 'VT-EXX'),
        ('DL 5947', 'DL', 'LHR', 'DEL', 'Arrived', '2026-04-05 03:20', '2026-04-05 15:10', 'N104AA')
    ]
    cursor.executemany("INSERT INTO flights VALUES (?,?,?,?,?,?,?,?);", flights_data)
    conn.commit()
    
    st.session_state['db_conn'] = conn

def run_query(query, params=()):
    return pd.read_sql_query(query, st.session_state['db_conn'], params=params)

# ----------------------------------------------------
# 2. STREAMLIT INTERFACE & VISUAL DECORATIONS
# ----------------------------------------------------
st.set_page_config(
    page_title="Global Aviation Analytics Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Design
st.sidebar.title("✈️ Flight Analytics")
st.sidebar.markdown("---") 

page = st.sidebar.radio(
    "📊 Select Workspace:",
    [
        "🏠 Homepage Dashboard", 
        "🔍 Search & Filter Flights", 
        "🏢 Airport Details Viewer", 
        "⏳ Delay Analysis", 
        "🏆 Route Leaderboards",
        "🗃️ Complete 11-Query Manifest"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Use the 'Complete 11-Query Manifest' workspace to check all core backend SQL queries built for this project.")

# ----------------------------------------------------
# PAGE 1: HOMEPAGE DASHBOARD
# ----------------------------------------------------
if page == "🏠 Homepage Dashboard":
    st.title("🏠 Global Aviation Network Dashboard")
    st.markdown("Real-time summary statistics of active flights, hubs, and carrier operations.")
    st.write("---")
    
    # KPI Summary Cards
    total_airports = run_query("SELECT COUNT(*) FROM airport").iloc[0, 0]
    total_flights = run_query("SELECT COUNT(*) FROM flights").iloc[0, 0]
    delay_stats = run_query("SELECT SUM(CASE WHEN status = 'Delayed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) FROM flights").iloc[0, 0]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tracked Airports", f"{total_airports} Hubs", help="Total nodes in database")
    col2.metric("Total Scheduled Flights", f"{total_flights} Legs", delta="Live Pipeline", delta_color="inverse")
    col3.metric("System-Wide Delay Rate", f"{delay_stats:.2f}%")
    
    st.write("---")
    st.subheader("📊 Operational Flight Status Distribution")
    status_df = run_query("SELECT status, COUNT(*) as volume FROM flights GROUP BY status ORDER BY volume DESC")
    fig = px.bar(status_df, x="status", y="volume", text="volume", color="status",
                 labels={"status": "Flight Status", "volume": "Number of Flights"},
                 template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# PAGE 2: SEARCH AND FILTER FLIGHTS
# ----------------------------------------------------
elif page == "🔍 Search & Filter Flights":
    st.title("🔍 Advanced Flight Manifest Lookup")
    st.markdown("Search individual flight identifiers or isolate carrier activities.")
    st.write("---")
    
    c1, c2 = st.columns(2)
    search_query = c1.text_input("✈️ Search Airline Code (e.g., 6E, AI)", "").strip()
    selected_status = c2.selectbox("Select Flight Status", ["All", "Arrived", "Departed", "Delayed", "Canceled"])
    
    conditions = ["1=1"]
    params = []
    
    if search_query:
        conditions.append("airline_code LIKE ?")
        params.append(f"%{search_query}%")
    if selected_status != "All":
        conditions.append("status = ?")
        params.append(selected_status)
        
    query = f"SELECT flight_number, airline_code, origin_iata, destination_iata, status FROM flights WHERE { ' AND '.join(conditions) }"
    st.dataframe(run_query(query, params), use_container_width=True, hide_index=True)

# ----------------------------------------------------
# PAGE 3: AIRPORT DETAILS VIEWER (UPDATED WITH TRAFFIC GRIDS)
# ----------------------------------------------------
elif page == "🏢 Airport Details Viewer":
    st.title("🏢 Airport Hub Profile Terminal")
    st.markdown("Select a global hub to view comprehensive airfield profiles and live terminal traffic loops.")
    st.write("---")
    
    # Dropdown choice parsing
    airport_df = run_query("SELECT iata_code || ' - ' || name AS label, iata_code FROM airport")
    selected_label = st.selectbox("Select Airport Hub", airport_df["label"])
    selected_iata = airport_df.loc[airport_df["label"] == selected_label, "iata_code"].values[0]
    
    # 1. Profile Display Banner
    details = run_query("SELECT * FROM airport WHERE iata_code = ?", (selected_iata,))
    st.info(f"📍 **Airport Profile:** {details.iloc[0]['name']} | **City:** {details.iloc[0]['city']} | **Country:** {details.iloc[0]['country']}")
    
    st.write("---")
    
    # 2. Parallel Live Inbound/Outbound Splits
    col_arr, col_dep = st.columns(2)
    
    with col_arr:
        st.subheader("🛬 Live Inbound Arrivals")
        arrivals_df = run_query("""
            SELECT flight_number AS [Flight], 
                   origin_iata AS [From], 
                   scheduled_arrival AS [ETA], 
                   status AS [Status]
            FROM flights 
            WHERE TRIM(destination_iata) = ?
            ORDER BY scheduled_arrival ASC;
        """, (selected_iata,))
        
        if not arrivals_df.empty:
            st.dataframe(arrivals_df, use_container_width=True, hide_index=True)
        else:
            st.caption("No scheduled inbound arrivals found for this station point.")
            
    with col_dep:
        st.subheader("🛫 Live Outbound Departures")
        departures_df = run_query("""
            SELECT flight_number AS [Flight], 
                   destination_iata AS [To], 
                   scheduled_departure AS [ETD], 
                   status AS [Status]
            FROM flights 
            WHERE TRIM(origin_iata) = ?
            ORDER BY scheduled_departure ASC;
        """, (selected_iata,))
        
        if not departures_df.empty:
            st.dataframe(departures_df, use_container_width=True, hide_index=True)
        else:
            st.caption("No scheduled outbound departures found for this station point.")

# ----------------------------------------------------
# PAGE 4: DELAY ANALYSIS
# ----------------------------------------------------
elif page == "⏳ Delay Analysis":
    st.title("⏳ Inbound Hub Delay Analysis Metrics")
    st.write("---")
    
    delay_data = run_query("""
        SELECT destination_iata, 
               SUM(CASE WHEN status='Delayed' THEN 1 ELSE 0 END) as delayed_flights,
               COUNT(*) as total_flights
        FROM flights GROUP BY destination_iata;
    """)
    st.dataframe(delay_data, use_container_width=True, hide_index=True)

# ----------------------------------------------------
# PAGE 5: ROUTE LEADERBOARDS
# ----------------------------------------------------
elif page == "🏆 Route Leaderboards":
    st.title("🏆 Aviation Volume Leaderboards")
    st.write("---")
    
    busiest_routes = run_query("""
        SELECT (origin_iata || ' ➔ ' || destination_iata) AS route, COUNT(*) as volume
        FROM flights GROUP BY origin_iata, destination_iata ORDER BY volume DESC;
    """)
    fig_volume = px.bar(busiest_routes, x="volume", y="route", orientation="h", color="volume", template="plotly_dark")
    st.plotly_chart(fig_volume, use_container_width=True)

# ----------------------------------------------------
# PAGE 6: COMPLETE 11-QUERY MANIFEST (CLEAN LOGIC W/ TABS)
# ----------------------------------------------------
elif page == "🗃️ Complete 11-Query Manifest":
    st.title("🗃️ Core Analytical Query Log")
    st.markdown("This section houses all foundational SQL queries built during pipeline prototyping.")
    st.write("---")
    
    t1, t2, t3, t4, t5 = st.tabs(["✈️ Aircraft Analysis", "🏢 Airport & Hub Metrics", "🗺️ Flight Routing", "📊 Delay Performance", "❌ System Anomalies"])
    
    with t1:
        st.subheader("Query 1: Total Flights by Aircraft Model")
        st.dataframe(run_query("""
            SELECT TRIM(a.model) AS model, COUNT(*) AS total_number
            FROM flights f
            JOIN aircraft a ON TRIM(f.aircraft_registration) = TRIM(a.registration)
            GROUP BY TRIM(a.model) ORDER BY total_number DESC;
        """), use_container_width=True, hide_index=True)

        st.subheader("Query 2: Aircraft Models Assigned to More Than 5 Flights")
        st.dataframe(run_query("""
            SELECT TRIM(a.model) AS model, COUNT(*) AS total_number
            FROM flights f
            JOIN aircraft a ON TRIM(f.aircraft_registration) = TRIM(a.registration)
            GROUP BY TRIM(a.model) ORDER BY total_number DESC;
        """), use_container_width=True, hide_index=True)

        st.subheader("Query 3: Registration and Model Flight Capacity")
        st.dataframe(run_query("""
            SELECT TRIM(a.registration) AS registration, TRIM(a.model) AS model, COUNT(*) AS flight_count
            FROM flights f
            JOIN aircraft a ON TRIM(f.aircraft_registration) = TRIM(a.registration)
            GROUP BY TRIM(a.registration), TRIM(a.model);
        """), use_container_width=True, hide_index=True)
        
    with t2:
        st.subheader("Query 4: Top Destination Airports by Inbound Flights")
        st.dataframe(run_query("""
            SELECT TRIM(ap.name) AS airport_name, TRIM(ap.city) AS city, COUNT(*) AS arrivals_count
            FROM flights f
            JOIN airport ap ON TRIM(f.destination_iata) = TRIM(ap.iata_code)
            GROUP BY ap.iata_code ORDER BY arrivals_count DESC LIMIT 3;
        """), use_container_width=True, hide_index=True)
        
        st.subheader("Query 6: Recent Arrivals scheduled to Delhi (DEL)")
        st.dataframe(run_query("""
            SELECT f.flight_number, f.aircraft_registration, TRIM(org_air.name) AS departure_airport, f.scheduled_arrival
            FROM flights f
            LEFT JOIN airport org_air ON TRIM(f.origin_iata) = TRIM(org_air.iata_code)
            WHERE TRIM(f.destination_iata) = 'DEL' ORDER BY f.scheduled_arrival DESC LIMIT 5;
        """), use_container_width=True, hide_index=True)
        
        st.subheader("Query 7: Airfields Lacking Inbound Air Traffic")
        st.dataframe(run_query("""
            SELECT iata_code, name, city FROM airport 
            WHERE TRIM(iata_code) NOT IN (SELECT DISTINCT TRIM(destination_iata) FROM flights);
        """), use_container_width=True, hide_index=True)

    with t3:
        st.subheader("Query 5: Categorizing Flights as Domestic vs International")
        st.dataframe(run_query("""
            SELECT f.flight_number, f.origin_iata, f.destination_iata,
            CASE WHEN TRIM(oa.country) = TRIM(da.country) THEN 'Domestic' ELSE 'International' END as flight_type
            FROM flights f
            LEFT JOIN airport oa ON TRIM(f.origin_iata) = TRIM(oa.iata_code)
            LEFT JOIN airport da ON TRIM(f.destination_iata) = TRIM(da.iata_code);
        """), use_container_width=True, hide_index=True)

        st.subheader("Query 10: Active City-Pairs Fleet Volume")
        st.dataframe(run_query("""
            SELECT origin_iata, destination_iata, COUNT(DISTINCT aircraft_registration) as unique_aircraft_count
            FROM flights GROUP BY origin_iata, destination_iata;
        """), use_container_width=True, hide_index=True)

    with t4:
        st.subheader("Query 8: Carrier Metrics Profile")
        st.dataframe(run_query("""
            SELECT airline_code, 
            SUM(CASE WHEN status IN ('Arrived','Departed') THEN 1 ELSE 0 END) as normal_count,
            SUM(CASE WHEN status='Delayed' THEN 1 ELSE 0 END) as delayed_count,
            COUNT(*) as total_flights
            FROM flights GROUP BY airline_code;
        """), use_container_width=True, hide_index=True)

    with t5:
        st.subheader("Query 11: Final Station Delay Percentages")
        st.dataframe(run_query("""
            SELECT destination_iata, 
            SUM(CASE WHEN status='Delayed' THEN 1 ELSE 0 END) as delayed,
            COUNT(*) as total,
            ROUND(SUM(CASE WHEN status='Delayed' THEN 1 ELSE 0 END)*100.0/COUNT(*), 2) as delay_rate
            FROM flights GROUP BY destination_iata;
        """), use_container_width=True, hide_index=True)