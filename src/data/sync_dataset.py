from garminconnect import Garmin

import zipfile, io, os

cwd = os.getcwd()

client = Garmin("ju.roulle@gmail.com", "Julien35830")
client.login()
activities = client.get_activities(0, 10000)

"""
Download an Activity
"""
import zipfile, io, os

for activity in activities:
    activity_id = activity["activityId"]
    if os.path.exists(f"{cwd}/data/raw/{activity_id}") or activity["activityType"]["typeKey"] not in ["trail_running", "running"]:
        continue
    print("client.download_activities(%s)", activity_id)
    print("----------------------------------------------------------------------------------------")
    
    os.makedirs(f'{cwd}/data/raw/{activity_id}', exist_ok=True)

    gpx_data = client.download_activity(activity_id, dl_fmt=client.ActivityDownloadFormat.GPX)
    output_file = f"{cwd}/data/raw/{activity_id}/{str(activity_id)}.gpx"
    with open(output_file, "wb") as fb:
        fb.write(gpx_data)

    tcx_data = client.download_activity(activity_id, dl_fmt=client.ActivityDownloadFormat.TCX)
    output_file = f"{cwd}/data/raw/{activity_id}/{str(activity_id)}.tcx"
    with open(output_file, "wb") as fb:
        fb.write(tcx_data)

    zip_data = client.download_activity(activity_id, dl_fmt=client.ActivityDownloadFormat.ORIGINAL)
    with zipfile.ZipFile(io.BytesIO(zip_data), "r") as fb:
        fb.extractall(f'{cwd}/data/raw/{activity_id}/')

    csv_data = client.download_activity(activity_id, dl_fmt=client.ActivityDownloadFormat.CSV)
    output_file = f"{cwd}/data/raw/{activity_id}/{str(activity_id)}.csv"
    with open(output_file, "wb") as fb:
        fb.write(csv_data)