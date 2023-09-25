import io
import zipfile
from pathlib import Path

from garminconnect import Garmin
from rich.progress import track


def download_and_save_activity(client, activity_id, dl_fmt, output_file):
    try:
        data = client.download_activity(activity_id, dl_fmt=dl_fmt)

        if dl_fmt == client.ActivityDownloadFormat.ORIGINAL:
            with zipfile.ZipFile(io.BytesIO(data), "r") as zip_file:
                zip_file.extractall(Path(output_file) / "..")
        else:
            with open(output_file, "wb") as fb:
                fb.write(data)
    except Exception as e:
        print(f"Error downloading activity {activity_id}: {str(e)}")


def main():
    cwd = Path.cwd()

    client = Garmin("ju.roulle@gmail.com", "Julien35830")
    client.login()
    activities = client.get_activities(0, 10000)
    """
    Download an Activity
    """
    activities_to_download = []
    for activity in activities:
        activity_id = activity["activityId"]
        activity_dir = cwd / f"data/raw/{activity_id}"
        if not activity_dir.exists() and activity["activityType"]["typeKey"] in [
            "trail_running",
            "running",
            "swimming",
            "cycling",
        ]:
            activities_to_download.append(activity_id)

    for value in track(range(len(activities_to_download)), description="Processing..."):
        activity_id = activities_to_download[value]
        print("client.download_activities", activity_id)
        print(
            "---------------------------------------------------------------------------"
        )
        activity_dir = cwd / f"data/raw/{activity_id}"

        activity_dir.mkdir(parents=True, exist_ok=True)

        download_formats = {
            client.ActivityDownloadFormat.GPX: "gpx",
            client.ActivityDownloadFormat.TCX: "tcx",
            client.ActivityDownloadFormat.ORIGINAL: "zip",
            client.ActivityDownloadFormat.CSV: "csv",
        }

        for dl_fmt, ext in download_formats.items():
            output_file = f"{cwd}/data/raw/{activity_id}/{str(activity_id)}.{ext}"
            download_and_save_activity(client, activity_id, dl_fmt, output_file)


if __name__ == "__main__":
    main()
