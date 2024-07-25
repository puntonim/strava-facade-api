from typing import Optional, Union

import requests


class StravaClient:
    def __init__(self, access_token: str) -> None:
        self.access_token = access_token

    def list_activities(
        self,
        after_ts: int | float | None = None,
        before_ts: int | float | None = None,
        activity_type: str | None = None,
        n_results_per_page: int | None = None,
    ) -> list[Optional[dict]]:
        """
        List all my activities and filter by date, as supported by Strava API.
        Also, filter by activity_type, but this is just a Python filtering (NOT supported by Strava API).

        Docs:
            - Authentication: https://developers.strava.com/docs/authentication/
            - List Athlete Activities API: https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities
        """
        print(f"Listing my activities...")
        url = "https://www.strava.com/api/v3/athlete/activities"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        payload = {}
        if before_ts:
            payload["before"] = int(before_ts)
        if after_ts:
            payload["after"] = int(after_ts)
        if n_results_per_page:
            payload["per_page"] = n_results_per_page
        response = requests.get(url, headers=headers, params=payload)
        response.raise_for_status()

        data = response.json()
        if activity_type:
            data = []
            for activity in response.json():
                if activity.get("type") == activity_type:
                    data.append(activity)
        # A single `activity` is a dict like:
        # {
        #     "resource_state": 2,
        #     "athlete": {
        #         "id": 115890775,
        #         "resource_state": 1
        #     },
        #     "name": "Weight training: broken finger, abs, triceps, legs",
        #     "distance": 0.0,
        #     "moving_time": 7157,
        #     "elapsed_time": 7157,
        #     "total_elevation_gain": 0,
        #     "type": "WeightTraining",
        #     "sport_type": "WeightTraining",
        #     "id": 10709853894,
        #     "start_date": "2024-02-06T17:20:32Z",
        #     "start_date_local": "2024-02-06T18:20:32Z",
        #     "timezone": "(GMT+01:00) Africa/Algiers",
        #     "utc_offset": 3600.0,
        #     "location_city": null,
        #     "location_state": null,
        #     "location_country": "Italy",
        #     "achievement_count": 0,
        #     "kudos_count": 0,
        #     "comment_count": 0,
        #     "athlete_count": 1,
        #     "photo_count": 0,
        #     "map": {
        #         "id": "a10709853894",
        #         "summary_polyline": "",
        #         "resource_state": 2
        #     },
        #     "trainer": true,
        #     "commute": false,
        #     "manual": false,
        #     "private": false,
        #     "visibility": "followers_only",
        #     "flagged": false,
        #     "gear_id": null,
        #     "start_latlng": [],
        #     "end_latlng": [],
        #     "average_speed": 0.0,
        #     "max_speed": 0.0,
        #     "average_temp": 24,
        #     "has_heartrate": true,
        #     "average_heartrate": 77.0,
        #     "max_heartrate": 148.0,
        #     "heartrate_opt_out": false,
        #     "display_hide_heartrate_option": true,
        #     "elev_high": 0.0,
        #     "elev_low": 0.0,
        #     "upload_id": 11453524654,
        #     "upload_id_str": "11453524654",
        #     "external_id": "garmin_ping_319619866387",
        #     "from_accepted_tag": false,
        #     "pr_count": 0,
        #     "total_photo_count": 0,
        #     "has_kudoed": false
        # }
        return data

    def get_activity_details(self, activity_id: int) -> dict:
        """
        Get details for the given activity id.

        Docs:
            - Authentication: https://developers.strava.com/docs/authentication/
            - Get Activity API: https://developers.strava.com/docs/reference/#api-Activities-getActivityById
        """
        print(f"Getting activity details for id={activity_id}...")
        url = f"https://www.strava.com/api/v3/activities/{activity_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        details = response.json()
        # `details` is a dict like:
        # {
        #     "resource_state": 3,
        #     "athlete": {
        #         "id": 115890775,
        #         "resource_state": 1
        #     },
        #     "name": "Weight training: broken finger, abs, triceps, legs",
        #     "distance": 0.0,
        #     "moving_time": 7157,
        #     "elapsed_time": 7157,
        #     "total_elevation_gain": 0,
        #     "type": "WeightTraining",
        #     "sport_type": "WeightTraining",
        #     "id": 10709853894,
        #     "start_date": "2024-02-06T17:20:32Z",
        #     "start_date_local": "2024-02-06T18:20:32Z",
        #     "timezone": "(GMT+01:00) Africa/Algiers",
        #     "utc_offset": 3600.0,
        #     "location_city": null,
        #     "location_state": null,
        #     "location_country": "Italy",
        #     "achievement_count": 0,
        #     "kudos_count": 0,
        #     "comment_count": 0,
        #     "athlete_count": 1,
        #     "photo_count": 0,
        #     "map": {
        #         "id": "a10709853894",
        #         "polyline": "",
        #         "resource_state": 3,
        #         "summary_polyline": ""
        #     },
        #     "trainer": true,
        #     "commute": false,
        #     "manual": false,
        #     "private": false,
        #     "visibility": "followers_only",
        #     "flagged": false,
        #     "gear_id": null,
        #     "start_latlng": [],
        #     "end_latlng": [],
        #     "average_speed": 0.0,
        #     "max_speed": 0.0,
        #     "average_temp": 24,
        #     "has_heartrate": true,
        #     "average_heartrate": 77.0,
        #     "max_heartrate": 148.0,
        #     "heartrate_opt_out": false,
        #     "display_hide_heartrate_option": true,
        #     "elev_high": 0.0,
        #     "elev_low": 0.0,
        #     "upload_id": 11453524654,
        #     "upload_id_str": "11453524654",
        #     "external_id": "garmin_ping_319619866387",
        #     "from_accepted_tag": false,
        #     "pr_count": 0,
        #     "total_photo_count": 0,
        #     "has_kudoed": false,
        #     "description": "Finger rehab: 15 reps x 20 sets\nDecline crunch: bodyweight x 15 reps x 5 sets\nRussian twist: 40 reps x 5 sets\nV-hold: 30s reps x 5 sets\nResistance band tricep pull-down: red band (25kg) x 15 reps x 5 sets\nBulgarian split squat: bodyweight+16kg x 10 reps x 5 sets\nSplit soleus raise: bodyweight x 20 reps x 4 sets\n",
        #     "calories": 404.0,
        #     "perceived_exertion": null,
        #     "prefer_perceived_exertion": null,
        #     "segment_efforts": [],
        #     "laps": [
        #         {
        #             "id": 37068060147,
        #             "resource_state": 2,
        #             "name": "Lap 1",
        #             "activity": {
        #                 "id": 10709853894,
        #                 "visibility": "followers_only",
        #                 "resource_state": 1
        #             },
        #             "athlete": {
        #                 "id": 115890775,
        #                 "resource_state": 1
        #             },
        #             "elapsed_time": 7157,
        #             "moving_time": 7157,
        #             "start_date": "2024-02-06T17:20:32Z",
        #             "start_date_local": "2024-02-06T18:20:32Z",
        #             "distance": 0.0,
        #             "average_speed": 0.0,
        #             "max_speed": 0.0,
        #             "lap_index": 1,
        #             "split": 1,
        #             "start_index": 0,
        #             "end_index": 4321,
        #             "total_elevation_gain": 0,
        #             "device_watts": false,
        #             "average_heartrate": 77.0,
        #             "max_heartrate": 148.0
        #         }
        #     ],
        #     "photos": {
        #         "primary": null,
        #         "count": 0
        #     },
        #     "stats_visibility": [
        #         {
        #             "type": "heart_rate",
        #             "visibility": "everyone"
        #         },
        #         {
        #             "type": "pace",
        #             "visibility": "everyone"
        #         },
        #         {
        #             "type": "power",
        #             "visibility": "everyone"
        #         },
        #         {
        #             "type": "speed",
        #             "visibility": "everyone"
        #         },
        #         {
        #             "type": "calories",
        #             "visibility": "everyone"
        #         }
        #     ],
        #     "hide_from_home": false,
        #     "device_name": "Garmin Forerunner 965",
        #     "embed_token": "33f24624d0d69cfd987523970ae102065eb6b101",
        #     "private_note": "",
        #     "available_zones": []
        # }
        return details

    def update_activity(self, activity_id: int, data: dict) -> int:
        """
        Update an activity by its id.

        Docs:
            - Authentication: https://developers.strava.com/docs/authentication/
            - Update Activity API: https://developers.strava.com/docs/reference/#api-Activities-updateActivityById
        """
        print(f"Updating activity id={activity_id}...")
        url = f"https://www.strava.com/api/v3/activities/{activity_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.put(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
