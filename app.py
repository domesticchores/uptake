from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from flask import Flask, render_template, request, jsonify
from vonage import Vonage, Auth, HttpClientOptions
from vonage_sms import SmsMessage
from datetime import datetime, timedelta
import pytz
import threading

# import configs
from config import *

# Initialize Vonage API
auth = Auth(api_key=VONAGE_API_KEY, api_secret=VONAGE_SECRET)
options = HttpClientOptions(api_host=VONAGE_API_HOST, timeout=30)
client = Vonage(auth=auth, http_client_options=options)

scheduler = BackgroundScheduler()
scheduler.start()

app = Flask(__name__)

# TO-DO: allow dynamic timezone based on device TZ
TIMEZONE = pytz.timezone("America/New_York")
temp_event = []

def sendMessage(event_data):
    print(f"sent {event_data[0]} @ time {event_data[1]}")
    message = SmsMessage(to=VONAGE_DEST_NUMBER, from_=VONAGE_HOST_NUMBER, text=f"REMINDER: {event_data[0]} is scheduled for {event_data[1]}")
    response = client.sms.send(message)
    print(response.model_dump_json(exclude_unset=True))


def DEV_process(user_input):
    global phase, temp_event
    try:
        assert len(user_input.split(" ")) == 4
        month, day, time, event = user_input.split(" ")

        now = datetime.now()

        dt_string = "%Y-%B-%d-%I%p"
        # If its not a full hour, use different string w/ minutes
        if len(time[:-2].split(":")) == 2:
            dt_string = "%Y-%B-%d-%I:%M%p"
        target = datetime.strptime(f"{now.year}-{month}-{day}-{time}", dt_string)
    except (ValueError, AssertionError):
        return "Sorry, I couldn't understand that. Make sure you're using this template: <pre>MONTH DAY TIME EVENT</pre> \n If you need help, use the <code>HELP</code> command."
    else:
        # ensure that the year is next year if the month has already occured
        if (now.month > target.month) or (now.month == target.month and now.day > target.day):
            target += timedelta(days=365)
        event_date = TIMEZONE.localize(target)
        temp_event = [event, event_date]
        phase = add_to_scheduler
        return f"Ok! Just to make sure, you want to schedule this event? <pre><strong>{event.capitalize()}</strong> \n {event_date.strftime("%A, %B %d %Y @ %I:%M%p %Z")}</pre> Reply with [Y]es or [N]o!"
    
def add_to_scheduler(user_input):
    global phase
    if user_input.lower() in ['y','yes']:
        phase = DEV_process
        scheduler.add_job(sendMessage, 'date', run_date=temp_event[1], args=[temp_event])
        return "Ok! I have added your event. You'll get reminders 2 days, 1 day, 2 hours, and 1 hour before the event. If you would like to make another event, I can do that now!"
    elif user_input.lower() in ['n','no']:
        phase = DEV_process
        return "Cancelling this event. If you would like to make another event, I can do that now!"
    else:
        return "Sorry, I didn't understand. Reply with [Y]es or [N]o."

phase = DEV_process

def process_user_input(user_input):
    message = SmsMessage(to=VONAGE_DEST_NUMBER, from_=VONAGE_HOST_NUMBER, text=user_input)
    response = client.sms.send(message)
    print(response.model_dump_json(exclude_unset=True))
    return f"You said: {user_input}"

# ======================== Flask Routes ======================== #

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    user_input = request.json.get('text')
    if user_input == 'clear':
        return jsonify({'response': "clear"})
    response = phase(user_input)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
