from apscheduler.schedulers.background import BackgroundScheduler
from app.utils.sensor_data import fetch_thingspeak_data ,ingest_and_save


def start_sensor_scheduler():
    scheduler = BackgroundScheduler()

    #scheduler.add_job(ingest_and_save,'interval', seconds=5, )
    scheduler.start()

 