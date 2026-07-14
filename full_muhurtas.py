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
DAYS_AHEAD = 1826  # 5-year rolling window

def generate_brahmamuhurta_calendar():
    loc = LocationInfo(LOCATION_NAME, "", TIMEZONE, LATITUDE, LONGITUDE)
    tz = pytz.timezone(TIMEZONE)
    cal = Calendar()
    
    today = datetime.date.today()
    print(f"Generating 5-year Brahmamuhurta calendar for {LOCATION_NAME}...")
    
    for i in range(DAYS_AHEAD):
        current_day = today + datetime.timedelta(days=i)
        yesterday = current_day - datetime.timedelta(days=1)
        
        try:
            # Brahmamuhurta depends on the night preceding the morning sunrise.
            # We need yesterday's sunset and today's sunrise.
            s_yesterday = sun(loc.observer, date=yesterday, tzinfo=tz)
            s_today = sun(loc.observer, date=current_day, tzinfo=tz)
            
            sunset_yesterday = s_yesterday['sunset']
            sunrise_today = s_today['sunrise']
            
            # Calculate dynamic night length and the duration of 1 night muhurta (1/15th of the night)
            night_duration = (sunrise_today - sunset_yesterday).total_seconds()
            muhurta_duration = night_duration / 15
            
            # Brahmamuhurta starts 2 muhurtas before sunrise and ends 1 muhurta before sunrise
            brahma_start = sunrise_today - datetime.timedelta(seconds=2 * muhurta_duration)
            brahma_end = sunrise_today - datetime.timedelta(seconds=1 * muhurta_duration)
            
        except Exception:
            # Skip any seasonal calculations errors if edge cases occur
            continue
            
        # Create the Calendar Event
        e = Event(
            name="🧘 Brahmamuhurta",
            begin=brahma_start,
            end=brahma_end,
            description=(
                f"Auspicious spiritual hour.\n"
                f"Start: {brahma_start.strftime('%I:%M %p')}\n"
                f"End: {brahma_end.strftime('%I:%M %p')}\n"
                f"Dynamic Muhurta Length: {round(muhurta_duration / 60, 1)} minutes."
            )
        )
        cal.events.add(e)
        
    filename = "brahmamuhurta.ics"
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(cal.serialize_iter())
    print(f"Successfully saved {filename} with 5 years of data.")

if __name__ == "__main__":
    generate_brahmamuhurta_calendar()
