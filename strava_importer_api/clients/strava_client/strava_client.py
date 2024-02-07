from typing import Optional, Union

import requests


class StravaClient:
    def __init__(self, access_token: str) -> None:
        self.access_token = access_token

    def list_activities(
        self,
        after_ts: Optional[Union[int, float]] = None,
        before_ts: Optional[Union[int, float]] = None,
        activity_type: Optional[str] = None,
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
        response = requests.get(url, headers=headers, params=payload)
        response.raise_for_status()

        data = response.json()
        if activity_type:
            data = []
            for activity in response.json():
                if activity.get("type") == activity_type:
                    data.append(activity)
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
        return response.json()

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
