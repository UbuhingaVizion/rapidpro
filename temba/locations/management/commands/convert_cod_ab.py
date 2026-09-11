import json
import os
import struct
import zipfile
import zlib

import requests
from django.core.management.base import BaseCommand, CommandError

HDX_API = "https://data.humdata.org/api/3/action/package_show"

# central directory / end of central directory signatures
EOCD_SIG = b"PK\x05\x06"
CD_SIG = b"PK\x01\x02"


class RemoteZip:
    """
    Minimal reader for a remote zip file using HTTP range requests. Only fetches the central directory and the
    specific entries requested, so we can pull individual level files out of very large HDX archives.
    """

    def __init__(self, url):
        self.url = url
        self.headers = {"User-Agent": "rapidpro-convert-cod-ab/1.0"}
        self.size = self._get_size()
        self.entries = self._read_central_directory()

    def _get(self, start, end):
        response = requests.get(self.url, headers={**self.headers, "Range": f"bytes={start}-{end}"}, timeout=120)
        response.raise_for_status()
        if response.status_code != 206:
            raise CommandError(f"Server did not honour range request for {self.url}")
        return response.content

    def _get_size(self):
        response = requests.get(self.url, headers={**self.headers, "Range": "bytes=0-0"}, timeout=60)
        response.raise_for_status()
        content_range = response.headers.get("Content-Range")
        if content_range:
            return int(content_range.split("/")[-1])
        return int(response.headers["Content-Length"])

    def _read_central_directory(self):
        tail = self._get(max(0, self.size - 131072), self.size - 1)
        offset = tail.rfind(EOCD_SIG)
        if offset < 0:
            raise CommandError(f"Could not find end of central directory in {self.url}")

        _, _, _, _, _, cd_size, cd_offset, _ = struct.unpack("<4s4H2LH", tail[offset : offset + 22])
        if cd_size == 0xFFFFFFFF or cd_offset == 0xFFFFFFFF:
            raise CommandError("ZIP64 archives are not supported")

        cd = self._get(cd_offset, cd_offset + cd_size - 1)
        entries = {}
        pos = 0
        while pos < len(cd) and cd[pos : pos + 4] == CD_SIG:
            method = struct.unpack("<H", cd[pos + 10 : pos + 12])[0]
            comp_size = struct.unpack("<I", cd[pos + 20 : pos + 24])[0]
            fn_len = struct.unpack("<H", cd[pos + 28 : pos + 30])[0]
            extra_len = struct.unpack("<H", cd[pos + 30 : pos + 32])[0]
            comment_len = struct.unpack("<H", cd[pos + 32 : pos + 34])[0]
            local_offset = struct.unpack("<I", cd[pos + 42 : pos + 46])[0]
            name = cd[pos + 46 : pos + 46 + fn_len].decode("utf-8")
            entries[name] = (method, comp_size, local_offset)
            pos += 46 + fn_len + extra_len + comment_len

        return entries

    def read(self, name):
        if name not in self.entries:
            raise CommandError(f"Entry '{name}' not found in {self.url}")

        method, comp_size, local_offset = self.entries[name]
        local = self._get(local_offset, local_offset + 29)
        fn_len = struct.unpack("<H", local[26:28])[0]
        extra_len = struct.unpack("<H", local[28:30])[0]
        data_start = local_offset + 30 + fn_len + extra_len
        raw = self._get(data_start, data_start + comp_size - 1)

        if method == 0:
            return raw
        elif method == 8:
            return zlib.decompress(raw, -15)
        else:
            raise CommandError(f"Unsupported compression method {method} for entry '{name}'")


class Command(BaseCommand):
    help = (
        "Convert an HDX COD-AB (Common Operational Datasets - Administrative Boundaries) dataset into geojson "
        "files that can be imported with the `import_geojson` command."
    )

    def add_arguments(self, parser):
        parser.add_argument("iso3", help="The ISO3 country code, e.g. KEN or BDI")
        parser.add_argument(
            "--levels", nargs="+", type=int, default=[0, 1, 2], help="The admin levels to convert (default 0 1 2)"
        )
        parser.add_argument("--out", default=".", help="The directory to write the geojson files to (default .)")
        parser.add_argument(
            "--zip", dest="zip_path", default=None, help="Optional path of a zip to write the files to"
        )
        parser.add_argument(
            "--source",
            default=None,
            help="A local COD-AB geojson zip to read instead of downloading from HDX (useful for offline runs)",
        )
        parser.add_argument(
            "--simplify-tolerance",
            type=float,
            default=0.001,
            help="The GEOS simplification tolerance in degrees (default 0.001)",
        )
        parser.add_argument("--no-simplify", action="store_true", help="Don't simplify the geometries")

    def handle(self, *args, **options):
        iso3 = options["iso3"].lower()
        levels = sorted(options["levels"])
        out_dir = options["out"]
        tolerance = options["simplify_tolerance"]
        simplify = not options["no_simplify"]

        names = [f"{iso3}_admin{level}.geojson" for level in levels]

        if options["source"]:
            contents = self._read_local_zip(options["source"], names)
        else:
            url = self._resolve_hdx_url(iso3)
            self.stdout.write(f"Reading {url}")
            remote = RemoteZip(url)
            contents = {name: remote.read(name) for name in names if name in remote.entries}

        os.makedirs(out_dir, exist_ok=True)
        written = []
        for level in levels:
            name = f"{iso3}_admin{level}.geojson"
            if name not in contents:
                self.stdout.write(self.style.WARNING(f"Skipping admin{level}, '{name}' not found"))
                continue

            geojson = self._convert_level(level, contents[name], tolerance, simplify)
            filename = f"admin_level_{level}_simplified.json"
            filepath = os.path.join(out_dir, filename)
            with open(filepath, "w") as fp:
                json.dump(geojson, fp)
            written.append(filepath)
            self.stdout.write(self.style.SUCCESS(f"Wrote {filepath} ({len(geojson['features'])} features)"))

        if options["zip_path"]:
            with zipfile.ZipFile(options["zip_path"], "w", zipfile.ZIP_DEFLATED) as zf:
                for filepath in written:
                    zf.write(filepath, os.path.basename(filepath))
            self.stdout.write(self.style.SUCCESS(f"Wrote {options['zip_path']}"))

    def _resolve_hdx_url(self, iso3):
        response = requests.get(
            HDX_API,
            params={"id": f"cod-ab-{iso3}"},
            headers={"User-Agent": "rapidpro-convert-cod-ab/1.0"},
            timeout=60,
        )
        response.raise_for_status()
        result = response.json().get("result")
        if not result:
            raise CommandError(f"No HDX dataset found for 'cod-ab-{iso3}'")

        for resource in result.get("resources", []):
            if resource.get("format", "").lower() == "geojson":
                return resource["url"]

        raise CommandError(f"No GeoJSON resource found for 'cod-ab-{iso3}'")

    def _read_local_zip(self, path, names):
        with zipfile.ZipFile(path, "r") as zf:
            available = set(zf.namelist())
            return {name: zf.read(name) for name in names if name in available}

    def _convert_level(self, level, data, tolerance, simplify):
        source = json.loads(data)
        features = []

        for feature in source.get("features", []):
            props = feature.get("properties", {})
            parent = str(props.get(f"adm{level - 1}_pcode") or "") if level >= 1 else None
            name = props.get(f"adm{level}_name") or props.get(f"adm{level}_name1") or ""

            # the importer uses name_en for countries, so set both to keep names unambiguous
            new_props = {"osm_id": str(props.get(f"adm{level}_pcode") or ""), "name": name, "name_en": name}
            if level >= 1:
                new_props["parent_id"] = parent
                if level == 1:
                    new_props["is_in_country"] = parent
                elif level == 2:
                    new_props["is_in_state"] = parent

            geometry = feature.get("geometry")
            if simplify and geometry:
                geometry = self._simplify(geometry, tolerance)

            features.append({"type": "Feature", "properties": new_props, "geometry": geometry})

        return {"type": "FeatureCollection", "features": features}

    def _simplify(self, geometry, tolerance):
        from django.contrib.gis.geos import GEOSGeometry

        geom = GEOSGeometry(json.dumps(geometry))
        return json.loads(geom.simplify(tolerance, preserve_topology=True).geojson)
