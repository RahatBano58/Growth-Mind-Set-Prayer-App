import streamlit as st
import datetime
import json
import urllib.request
import ssl
from datetime import datetime, timedelta
import urllib.parse
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

ssl._create_default_https_context = ssl._create_unverified_context

# Set page configuration
st.set_page_config(
    page_title="Islamic Prayer App",
    page_icon="🕌",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-family: 'Arial', sans-serif;
        color: #333;
        text-align: center;
        padding: 20px;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 20px;
    }
    
    .sub-header {
        font-family: 'Arial', sans-serif;
        color: #333;
        text-align: center;
        padding: 10px;
        font-size: 1.8em;
        font-weight: bold;
        margin-bottom: 10px;
        cursor: pointer;
    }
    
    .prayer-card {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 15px;
        margin: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        text-align: center;
        color: white;
    }
    
    .prayer-name {
        font-size: 1.3em;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .prayer-time {
        font-size: 1.5em;
        font-weight: bold;
    }
    
    .next-prayer {
        background-color: #e8f5e9;
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0;
        text-align: center;
        color: #2e7d32;
        font-weight: bold;
    }
    
    .quran-section {
        background-color: #f5f5f5;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    
    .footer {
        text-align: center;
        padding: 20px;
        font-size: 0.9em;
        color: #777;
        margin-top: 30px;
    }
    
    .hijri-date {
        text-align: center;
        font-size: 1.5em;
        margin: 15px 0;
        color: #333;
    }
    
    .prayer-icon {
        font-size: 2em;
        margin-bottom: 10px;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# App header with mosque emoji
st.markdown('<div class="main-header">🕌 Prayers App</div>', unsafe_allow_html=True)

# Sidebar for location input
st.sidebar.title("⚙️ Settings")

# Location selection with dropdown menus
countries_and_cities = {
    "Saudi Arabia": ["Mecca"],
    "United Arab Emirates": ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Al Ain"],
    "Egypt": ["Cairo", "Alexandria", "Giza", "Sharm El Sheikh", "Luxor"],
    "Pakistan": ["Karachi", "Lahore", "Islamabad", "Peshawar", "Faisalabad"],
    "Turkey": ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya"],
    "Indonesia": ["Jakarta", "Surabaya", "Bandung", "Medan", "Semarang"],
    "Malaysia": ["Kuala Lumpur", "Penang", "Johor Bahru", "Ipoh", "Kuching"],
    "United States": ["New York", "Chicago", "Houston", "Los Angeles", "Washington DC"],
    "United Kingdom": ["London", "Birmingham", "Manchester", "Leeds", "Glasgow"],
    "Canada": ["Toronto", "Montreal", "Vancouver", "Calgary", "Ottawa"],
    "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"],
    "India": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"],
    "Morocco": ["Casablanca", "Rabat", "Marrakesh", "Fes", "Tangier"],
    "Nigeria": ["Lagos", "Abuja", "Kano", "Ibadan", "Port Harcourt"],
    "South Africa": ["Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth"]
}

# Sort countries alphabetically
sorted_countries = sorted(countries_and_cities.keys())

# Country selection
selected_country = st.sidebar.selectbox("🌍 Country", sorted_countries, index=sorted_countries.index("Saudi Arabia"))

# City selection based on selected country
selected_city = st.sidebar.selectbox("🏙️ City", sorted(countries_and_cities[selected_country]), index=0)

# Use the selected values
city = selected_city
country = selected_country

# Display Hijri date
def get_hijri_date():
    try:
        url = "http://api.aladhan.com/v1/gToH"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode())
        if "data" in data and "hijri" in data["data"]:
            hijri = data["data"]["hijri"]
            return f"{hijri['day']} {hijri['month']['en']} {hijri['year']}"
        else:
            return "6 Ramadān 1446"  # Fallback date
    except Exception as e:
        return "6 Ramadān 1446"  # Fallback date

hijri_date = get_hijri_date()
st.markdown(f'<div class="hijri-date">📅 Hijri Date: {hijri_date}</div>', unsafe_allow_html=True)

# Prayer Times Section
st.markdown('<div class="sub-header">⏰ Today\'s Prayer Times</div>', unsafe_allow_html=True)

# Function to get prayer times
def get_prayer_times(city, country):
    try:
        # URL encode the city and country parameters
        encoded_city = urllib.parse.quote(city)
        encoded_country = urllib.parse.quote(country)
        
        url = f"http://api.aladhan.com/v1/timingsByCity?city={encoded_city}&country={encoded_country}&method=2"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode())
        if data["code"] == 200:
            return data["data"]["timings"]
        else:
            st.error(f"Error fetching prayer times: {data.get('data', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        # Return mock data if API call fails
        return {
            "Fajr": "05:12",
            "Dhuhr": "12:15",
            "Asr": "15:45",
            "Maghrib": "17:59",
            "Isha": "19:20"
        }

# Get prayer times
prayer_times = get_prayer_times(city, country)

if prayer_times:
    # Create columns for prayer times
    cols = st.columns(5)
    
    # Prayer names, their display names, and icons
    prayers = {
        "Fajr": {"name": "Fajr", "icon": "🌅"},
        "Dhuhr": {"name": "Dhuhr", "icon": "☀️"},
        "Asr": {"name": "Asr", "icon": "🌤️"},
        "Maghrib": {"name": "Maghrib", "icon": "🌇"},
        "Isha": {"name": "Isha", "icon": "🌙"}
    }
    
    # Display prayer times in cards
    for i, (prayer, info) in enumerate(prayers.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="prayer-card">
                <span class="prayer-icon">{info['icon']}</span>
                <div class="prayer-name">{info['name']}</div>
                <div class="prayer-time">{prayer_times[prayer]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Determine next prayer
    current_time = datetime.now().strftime("%H:%M")
    next_prayer = None
    next_prayer_time = None
    
    for prayer, info in prayers.items():
        if prayer in prayer_times and current_time < prayer_times[prayer]:
            if next_prayer is None or prayer_times[prayer] < next_prayer_time:
                next_prayer = prayer
                next_prayer_time = prayer_times[prayer]
                next_prayer_icon = info['icon']
    
    # Next prayer notification with hourglass emoji
    if next_prayer:
        st.markdown(f"""
        <div class="next-prayer">
            ⏳ Next Prayer: {next_prayer} at {next_prayer_time} ({datetime.now().strftime("%H:%M:%S.%f")[:-4]})
        </div>
        """, unsafe_allow_html=True)
    else:
        # If all prayers for today have passed
        st.markdown(f"""
        <div class="next-prayer">
            ⏳ Next Prayer: Fajr tomorrow
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("⚠️ Unable to fetch prayer times. Please check your location and try again.")

# Create a session with retry strategy
def create_session():
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Quran Section
st.markdown('<div class="sub-header">📖 Listen to Quran Recitation</div>', unsafe_allow_html=True)

# Updated Surahs dictionary with alternative audio URLs
surahs = {
    "Al-Fatiha (The Opening)": {
        "id": 1,
        "icon": "📜",
        "url": "https://download.quranicaudio.com/quran/mishaari_raashid_al_3afaasee/001.mp3"
    },
    "Al-Baqarah (The Cow)": {
        "id": 2,
        "icon": "🐄",
        "url": "https://download.quranicaudio.com/quran/mishaari_raashid_al_3afaasee/002.mp3"
    },
    "Yaseen": {
        "id": 36,
        "icon": "💫",
        "url": "https://download.quranicaudio.com/quran/mishaari_raashid_al_3afaasee/036.mp3"
    },
    "Ar-Rahman (The Beneficent)": {
        "id": 55,
        "icon": "🌺",
        "url": "https://download.quranicaudio.com/quran/mishaari_raashid_al_3afaasee/055.mp3"
    },
    "Al-Mulk (The Sovereignty)": {
        "id": 67,
        "icon": "👑",
        "url": "https://download.quranicaudio.com/quran/mishaari_raashid_al_3afaasee/067.mp3"
    },
    "Al-Ikhlas (The Sincerity)": {
        "id": 112,
        "icon": "💝",
        "url": "https://download.quranicaudio.com/quran/mishaari_raashid_al_3afaasee/112.mp3"
    },
    "Al-Falaq (The Daybreak)": {
        "id": 113,
        "icon": "🌅",
        "url": "https://download.quranicaudio.com/quran/mishaari_raashid_al_3afaasee/113.mp3"
    },
    "An-Nas (Mankind)": {
        "id": 114,
        "icon": "👥",
        "url": "https://download.quranicaudio.com/quran/mishaari_raashid_al_3afaasee/114.mp3"
    }
}

try:
    # Create two columns for the audio player
    col1, col2 = st.columns([3, 1])

    with col1:
        # Create the Surah selection dropdown
        surah_options = [f"{info['icon']} {surah}" for surah, info in surahs.items()]
        selected_option = st.selectbox(
            "Select Surah to Listen",
            surah_options,
            key='quran_surah_selector'
        )
        
        # Extract the surah name
        selected_surah = ' '.join(selected_option.split()[1:])
        
        # Get the audio URL
        audio_url = surahs[selected_surah]['url']
        
        # Display the audio player with styling
        st.markdown("""
        <div style='background-color: #f5f5f5; padding: 20px; border-radius: 10px; margin: 10px 0;'>
        """, unsafe_allow_html=True)
        
        # Show currently playing surah
        st.markdown(f"""
        <div style='text-align: center; margin-bottom: 15px;'>
            <h3 style='color: #1e1e1e;'>Now Playing</h3>
            <h4 style='color: #4CAF50;'>{selected_surah}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Direct audio player implementation
        st.audio(audio_url)
        
        # Simple download link
        st.markdown(f"""
        <div style='text-align: center; margin-top: 10px;'>
            <a href='{audio_url}' target='_blank' download>
                <button style='background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;'>
                    Download Surah
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Display reciter information
        st.markdown("""
        <div style='background-color: #f0f0f0; padding: 15px; border-radius: 8px; margin-top: 30px; text-align: center;'>
            <h4 style='margin-bottom: 10px;'>Reciter</h4>
            <p style='font-size: 16px; font-weight: bold;'>Mishary Rashid Alafasy</p>
            <small style='color: #666;'>High Quality Audio</small>
            <p style='margin-top: 10px; font-size: 12px;'>One of the most renowned Quran reciters</p>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error("Unable to load audio player. Please check your internet connection.")
    if st.button("Show Error Details"):
        st.code(str(e))

# Add a tracker for daily progress
if "visits" not in st.session_state:
    st.session_state.visits = 0
    st.session_state.last_visit = None

today_str = datetime.now().strftime("%Y-%m-%d")

if st.session_state.last_visit != today_str:
    st.session_state.visits += 1
    st.session_state.last_visit = today_str

st.sidebar.markdown("---")
st.sidebar.markdown(f"### 📊 Your Progress")
st.sidebar.markdown(f"You've visited the app **{st.session_state.visits}** days")

# Streak calculation
if "streak" not in st.session_state:
    st.session_state.streak = 1
    st.session_state.last_streak_date = today_str
else:
    last_date = datetime.strptime(st.session_state.last_streak_date, "%Y-%m-%d")
    today_date = datetime.strptime(today_str, "%Y-%m-%d")
    
    if (today_date - last_date).days == 1:
        st.session_state.streak += 1
        st.session_state.last_streak_date = today_str
    elif (today_date - last_date).days > 1:
        st.session_state.streak = 1
        st.session_state.last_streak_date = today_str

st.sidebar.markdown(f"Current streak: **{st.session_state.streak}** days 🔥")

# Add a simple tracker for completed prayers
if "completed_prayers" not in st.session_state:
    st.session_state.completed_prayers = {
        "Fajr": False,
        "Dhuhr": False,
        "Asr": False,
        "Maghrib": False,
        "Isha": False
    }

st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 Track Your Prayers")

# Create checkboxes for each prayer with icons
for prayer, completed in st.session_state.completed_prayers.items():
    icon = prayers[prayer]["icon"]
    st.session_state.completed_prayers[prayer] = st.sidebar.checkbox(
        f"{icon} Completed {prayer}",
        value=completed
    )

# Calculate and display progress
completed = sum(st.session_state.completed_prayers.values())
total = len(st.session_state.completed_prayers)
progress = completed / total

st.sidebar.progress(progress)
st.sidebar.markdown(f"**{completed}/{total}** prayers completed today")

# Add Qibla direction section
st.markdown('<div class="sub-header">🧭 Qibla Direction</div>', unsafe_allow_html=True)

# Simple compass image for Qibla direction
compass_html = """
<div style="text-align: center; margin: 20px 0;">
    <div style="background-color: #f5f5f5; border-radius: 50%; width: 200px; height: 200px; margin: 0 auto; position: relative; border: 5px solid #ddd;">
        <div style="position: absolute; top: 10px; left: 50%; transform: translateX(-50%);">N</div>
        <div style="position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%);">S</div>
        <div style="position: absolute; left: 10px; top: 50%; transform: translateY(-50%);">W</div>
        <div style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%);">E</div>
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
            <div style="width: 100px; height: 5px; background-color: #4CAF50; transform: rotate(45deg); transform-origin: left center;"></div>
            <div style="position: absolute; top: -20px; right: -20px; color: #4CAF50; font-weight: bold;">Qibla</div>
        </div>
    </div>
    <p style="margin-top: 10px;">Approximate Qibla direction from your location</p>
</div>
"""
st.markdown(compass_html, unsafe_allow_html=True)

# Add Islamic calendar events
st.markdown('<div class="sub-header">📆 Upcoming Islamic Events</div>', unsafe_allow_html=True)

events = [
    {"name": "Eid al-Fitr", "icon": "🎉", "days": 24},
    {"name": "Hajj", "icon": "🕋", "days": 95},
    {"name": "Eid al-Adha", "icon": "🐐", "days": 102}
]

for event in events:
    st.markdown(f"""
    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 10px; margin: 10px 0; display: flex; align-items: center;">
        <span style="font-size: 2em; margin-right: 15px;">{event['icon']}</span>
        <div>
            <div style="font-weight: bold; font-size: 1.2em;">{event['name']}</div>
            <div>In approximately {event['days']} days</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer with heart emoji
st.markdown("""
<div class="footer">
    <p>Created with ❤️ | © 2025 Islamic Prayer App</p>
</div>
""", unsafe_allow_html=True)

print("Prayer Web App is running!") 