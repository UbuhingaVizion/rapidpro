import pycountry

# As iso639-1 languages can be broad, not all iso639-2 languages have direct translations to iso639-3. This table
# maps country and iso639-1 codes to a specific iso639-3 language code. It isn't inclusive but covers the cases
# we know about at the time of our 639-1 -> 639-3 migration.
MIGRATION_OVERRIDES = {
    "NG:cpe": "pcm",
    "LR:cpe": "lir",
    "NI:cpe": "bzk",
    "XX:mkh": "khm",
    "XX:cpe": "pcm",
    "XX:art": "epo",
    "XX:cpf": "gcr",
    "XX:phi": "fil",
    "XX:smi": "smj",
    "XX:afa": "ara",
    "XX:aus": "rop",
    "XX:cpp": "kea",
    "XX:him": "xnr",
    "XX:kar": "blk",
    "XX:esp": "spa",
}

migration_lang_cache = {}


def iso6391_to_iso6393(iso_code, country_code=None):
    """
    Given an iso639-1 code and an optional country code, returns the appropriate 639-3 code to use.
    """

    if iso_code is None:
        return None

    iso_code = iso_code.lower().strip()

    if iso_code == "":
        raise ValueError("iso_code must not be empty")

    cache_key = f"{'XX' if country_code is None else country_code}:{iso_code}"

    if cache_key not in migration_lang_cache:
        # build our key
        override_key = f"{country_code}:{iso_code}" if country_code else f"XX:{iso_code}"
        override = MIGRATION_OVERRIDES.get(override_key)

        if not override and country_code:
            override_key = f"XX:{iso_code}"
            override = MIGRATION_OVERRIDES.get(override_key)

        if override:
            return override

        else:
            # first try looking up by part 2 bibliographic (which is what we use when available)
            try:
                lang = pycountry.languages.get(bibliographic=iso_code)
            except (KeyError, LookupError):
                lang = None

            # if not found, back down to terminological / part 3
            if lang is None:
                try:
                    lang = pycountry.languages.get(alpha_3=iso_code)
                except (KeyError, LookupError):
                    pass

            if lang and getattr(lang, "alpha_3", None):
                migration_lang_cache[cache_key] = lang.alpha_3
                return lang.alpha_3
    else:
        return migration_lang_cache[cache_key]

    raise ValueError(f"unable to determine iso639-3 code: {iso_code} ({country_code})")
