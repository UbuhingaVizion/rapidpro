import os

import regex
import requests

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Download geojson files for OSM relation ids."

    def add_arguments(self, parser):
        parser.add_argument("relation_ids", nargs="+")
        parser.add_argument(
            "--oauth-token",
            dest="oauth_token",
            default=None,
            help="The OAuth token to use when authenticating to GitHub. Unauthenticated requests are "
            "rate limited to 60 per hour. Defaults to None",
        )
        parser.add_argument(
            "--repo",
            dest="repo",
            default="nyaruka/posm-extracts",
            help="The GitHub posm-extracts repo to use. Defaults to nyaruka/posm-extracts",
        )
        parser.add_argument(
            "--dir",
            dest="dir",
            default="geojson",
            help="The directory to write the geojson files to. Defaults to `geojson`",
        )

    def handle(self, *args, **options):

        destination_dir = options["dir"]
        relation_ids = options["relation_ids"]
        repo = options["repo"]
        oauth_token = options["oauth_token"]

        if oauth_token:  # pragma: needs cover
            headers = {"Authorization": f"token {oauth_token}"}
        else:
            headers = {}

        data = requests.get(f"https://api.github.com/repos/{repo}/git/trees/master", headers=headers).json()
        [geojson] = filter(lambda obj: obj["path"] == "geojson", data["tree"])
        geojson_sha = geojson["sha"]

        files = requests.get(
            f"https://api.github.com/repos/{repo}/git/trees/{geojson_sha}", headers=headers
        ).json()

        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        for relation_id in relation_ids:
            relation_files = filter(
                lambda obj: regex.match(rf"R{relation_id}.*_simplified.json", obj["path"]), files["tree"]
            )
            for relation_file in relation_files:
                destination = os.path.join(destination_dir, relation_file["path"])
                with open(destination, "wb") as fp:
                    response = requests.get(
                        f"https://raw.githubusercontent.com/{repo}/master/geojson/{relation_file['path']}",
                        headers=headers,
                    )
                    fp.write(response.content)
