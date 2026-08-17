import os

import requests
from dotenv import load_dotenv


load_dotenv()


class BiwengerClient:
    BASE_URL = "https://biwenger.as.com/api/v2"

    def __init__(self, league_id=None):
        self.token = os.getenv("BIWENGER_TOKEN")

        self.league_id = (
            str(league_id)
            if league_id is not None
            else os.getenv("BIWENGER_LEAGUE_ID")
        )

        self.user_id = os.getenv("BIWENGER_USER_ID")

        if league_id is not None:
            self.user_id = self._get_user_id_for_league()

    def _get_user_id_for_league(self):
        data = self.get_account()

        for league in data["data"]["leagues"]:
            if str(league["id"]) == str(self.league_id):
                return str(league["user"]["id"])

        raise ValueError(
            f"User not found for Biwenger league {self.league_id}"
        )

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "X-League": self.league_id,
            "X-User": self.user_id,
        }

    def get_board(self, offset=0, limit=8):
        url = (
            f"{self.BASE_URL}/league/"
            f"{self.league_id}/board"
            f"?offset={offset}&limit={limit}"
        )

        response = requests.get(
            url,
            headers=self._get_headers(),
        )

        response.raise_for_status()

        return response.json()

    def get_competition_data(
        self,
        competition: str = "la-liga",
        score_id: int = 2,
    ):
        url = (
            "https://cf.biwenger.com/api/v2/competitions/"
            f"{competition}/data"
            f"?lang=es&score={score_id}"
        )

        headers = {
            "Accept": "application/json",
            "Origin": "https://biwenger.as.com",
            "Referer": "https://biwenger.as.com/",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            ),
        }

        response = requests.get(
            url,
            headers=headers,
        )

        response.raise_for_status()

        return response.json()

    def get_league(self):
        url = (
            f"{self.BASE_URL}/league"
            "?include=all%2C-lastAccess"
            "&fields=*%2Cstandings%2Ctournaments%2Cgroup%2Csettings(description)"
        )

        response = requests.get(
            url,
            headers=self._get_headers(),
        )

        response.raise_for_status()

        return response.json()

    def get_account(self):
        url = f"{self.BASE_URL}/account"

        headers = {
            "Authorization": f"Bearer {self.token}",
        }

        response = requests.get(
            url,
            headers=headers,
        )

        response.raise_for_status()

        return response.json()