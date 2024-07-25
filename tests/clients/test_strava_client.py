import pytest

from strava_facade_api.clients.strava_client.strava_client import StravaClient
from strava_facade_api.clients.strava_client.token_manager import TokenManager
from strava_facade_api.utils import datetime_utils


class TestCreateActivity:
    def setup_method(self):
        access_token = TokenManager.get_access_token()
        self.client = StravaClient(access_token)

    @pytest.mark.skip(
        reason="Not stubbed yet, so it will create an actual activity in Strava"
    )
    def test_happy_flow(self):
        # NOTE: it will actually create the activity in Strava. Not stubbed yet.
        response = self.client.create_activity(
            name="Test1 Paolo",
            sport_type="WeightTraining",
            # start_date=datetime_utils.now(), # "2024-07-25T15:42:55Z".
            start_date="2024-07-25T15:42:55Z",
            duration_seconds=60 * 60 + 5,
            description="test from Python",
        )
        assert response

    @pytest.mark.skip(
        reason="Not stubbed yet, so it will create an actual activity in Strava"
    )
    def test_duplicate(self):
        # NOTE: it will actually create the activity in Strava. Not stubbed yet.
        response = self.client.create_activity(
            name="Test1 Paolo",
            sport_type="WeightTraining",
            start_date=datetime_utils.now(),
            duration_seconds=60 * 60 + 5,
            description="test from Python",
            do_detect_duplicates=True,
        )
        assert response
