import datetime
import pytz
from astral import LocationInfo
from astral.sun import sun
from ics import Calendar, Event

# --- CONFIGURATION ---
LATITUDE = 45.487
LONGITUDE = -122.804
TIMEZONE = "America/Los_Angeles"
LOCATION_NAME = "Beaverton"
YEARS_TO_GENERATE = 5

# The 15 traditional Day Muhurtas (starting at Sunrise)
DAY_MUHURTAS = [
    "Rudra", "Ahi", "Mitra", "Pitru", "Vasu", "Varaha", 
    "Visvedeva", "Vidhi", "Sutamukhi", "Puruhuta", "Vahini", 
    "Naktanacara", "Varuna", "Aryaman", "Bhaga"
]

# The 15 traditional Night Muhurtas (starting at Sunset)
NIGHT_MUHURTAS = [
    "Girisha", "Ajapada", "Ahirbudhnya", "Pushya", "Ashvini", "Yama", 
    "Agni", "Vidhatru", "Kanda", "Aditi", "Jivamruta", "Vishnu", 
    "Dyumadgadyuti", "Brahma", "Samudra"
]

def generate_full_muhurtas_calendar():
    loc = LocationInfo(LOCATION_NAME, "", TIMEZONE, LATITUDE, LONGITUDE)
    tz = pytz.timezone(TIMEZONE)
    
    # Dynamically determine the current year and look ahead
    start_year = datetime.date.today().year
    target_years = range(start_year, start_year + YEARS_TO_GENERATE)
    
    for year in target_years:
        print(f"Generating Muhurtas for year {year}...")
        cal = Calendar()
        
        # Determine exact calendar year limits (automatically adjustments for leap years)
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year + 1, 1, 1)
        total_days = (end_date - start_date).days
        
        for day_offset in range(total_days):
            current_day = start_date + datetime.timedelta(days=day_offset)
            next_day = current_day + datetime.timedelta(days=1)
            
            try:
                s_current = sun(loc.observer, date=current_day, tzinfo=tz)
                s_next = sun(loc.observer, date=next_day, tzinfo=tz)
                
                sunrise_today = s_current['sunrise']
                sunset_today = s_current['sunset']
                sunrise_next = s_next['sunrise']
            except Exception:
                continue
                
            # Calculate dynamic lengths based on changing seasons
            day_duration = (sunset_today - sunrise_today).total_seconds()
            day_muhurta_len = day_duration / 15
            
            night_duration = (sunrise_next - sunset_today).total_seconds()
            night_muhurta_len = night_duration / 15
            
            # 1. Process Day Muhurtas (1 to 15)
            for idx, name in enumerate(DAY_MUHURTAS):
                start_time = sunrise_today + datetime.timedelta(seconds=idx * day_muhurta_len)
                end_time = start_time + datetime.timedelta(seconds=day_muhurta_len)
                
                e = Event(
                    name=f"Muhurta {idx + 1}: {name}",
                    begin=start_time,
                    end=end_time,
                    description=f"Daytime Muhurta ruled by deity {name}."
                )
                cal.events.add(e)
                
            # 2. Process Night Muhurtas (16 to 30)
            for idx, name in enumerate(NIGHT_MUHURTAS):
                start_time = sunset_today + datetime.timedelta(seconds=idx * night_muhurta_len)
                end_time = start_time + datetime.timedelta(seconds=night_muhurta_len)
                
                # Special note for the 14th night Muhurta (Brahma / Brahmamuhurta)
                desc = f"Nighttime Muhurta ruled by deity {name}."
                if name == "Brahma":
                    desc += " (Brahmamuhurta - Sacred window for spiritual focus and meditation)"
                    
                e = Event(
                    name=f"Muhurta {idx + 16}: {name}",
                    begin=start_time,
                    end=end_time,
                    description=desc
                )
                cal.events.add(e)
                
        # Write individual year files to ensure stability
        filename = f"muhurtas_{year}.ics"
        with open(filename, "w", encoding="utf-8") as f:
            f.writelines(cal.serialize_iter())
        print(f"Successfully compiled and saved {filename}")

if __name__ == "__main__":
    generate_full_muhurtas_calendar()
