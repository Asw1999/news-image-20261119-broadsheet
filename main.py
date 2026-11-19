"""Broadsheet generator for news-image-20261119 (Thursday, 19 November 2026)."""

import math
import os
import shutil
import sys
from pathlib import Path

CANVAS_W = 2048
CANVAS_H = 2048
OUT_W = 1024
OUT_H = 1024

PALETTE = {
    "paper": "#FAF7F0",
    "card_bg": "#FFFFFF",
    "ink": "#111827",
    "sub_ink": "#1E293B",
    "muted": "#475569",
    "rule": "#D6D0C4",
    "rule_light": "#E5E0D5",
    "crimson": "#B91C1C",
    "caption_bar": "#1F2937",
    "date_bg": "#FDECE7",
    "ocean": "#DCEBF7",
    "land": "#D9D2BF",
    "coast": "#9E9683",
}

ART_PASTELS = {
    "blush": "#F5E1DA",
    "cream": "#EFE6D5",
    "sky": "#DCEBF7",
    "sage": "#E2ECE4",
    "slate": "#E4E9F2",
    "space": "#0B1324",
}

REGION_ORDER = (
    "ASIA-PACIFIC",
    "MIDDLE EAST",
    "EUROPE",
    "AFRICA",
    "AMERICAS",
    "GLOBAL & OCEANIA",
)

REGION_COLORS = {
    "ASIA-PACIFIC": "#0F766E",
    "MIDDLE EAST": "#B45309",
    "EUROPE": "#1D4ED8",
    "AFRICA": "#C2410C",
    "AMERICAS": "#B91C1C",
    "GLOBAL & OCEANIA": "#6D28D9",
}

FONT_CANDIDATES = {
    "serif_bold": (
        "/system/fonts/NotoSerif-Bold.ttf",
        "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
    ),
    "serif_regular": (
        "/system/fonts/NotoSerif-Regular.ttf",
        "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
    ),
    "serif_italic": (
        "/system/fonts/NotoSerif-Italic.ttf",
        "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSerif-Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
    ),
    "sans_bold": (
        "/system/fonts/SourceSansPro-Bold.ttf",
        "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ),
    "sans_semibold": (
        "/system/fonts/SourceSansPro-SemiBold.ttf",
        "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ),
    "sans_regular": (
        "/system/fonts/SourceSansPro-Regular.ttf",
        "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ),
    "sans_condensed_bold": (
        "/system/fonts/BarlowSemiCondensed-Bold.ttf",
        "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSansCondensed-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
    ),
    "sans_condensed_regular": (
        "/system/fonts/BarlowSemiCondensed-Regular.ttf",
        "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSansCondensed.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
    ),
}


class FontBank:
    """Discovers available system TTFs once and caches sized font instances."""

    def __init__(self, image_font_cls) -> None:
        self._image_font_cls = image_font_cls
        self._resolved = {}
        self._cache = {}
        for role, paths in FONT_CANDIDATES.items():
            for candidate in paths:
                if Path(candidate).is_file():
                    self._resolved[role] = candidate
                    break

    def get(self, role: str, size: int):
        key = (role, size)
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        path = self._resolved.get(role)
        if path:
            font = self._image_font_cls.truetype(path, size)
        else:
            font = self._image_font_cls.load_default(size=size)
        self._cache[key] = font
        return font


REGION_COUNTS = {
    "ASIA-PACIFIC": 8,
    "MIDDLE EAST": 6,
    "EUROPE": 7,
    "AFRICA": 4,
    "AMERICAS": 6,
    "GLOBAL & OCEANIA": 5,
}

MASTHEAD_DECK = (
    "Three nuclear leaders meet in Shenzhen · World Court rules on Myanmar · "
    "Anthropic debuts in record $81.3bn IPO · GTA VI unlocks at midnight"
)
DATE_CHECK_LINE1 = (
    "DATE CHECK — Every story on this page happened or was first reported on "
    "Thursday 19 November 2026 (00:00–24:00 UTC):"
)
DATE_CHECK_LINE2 = (
    "Verified Thu 19 Nov UTC: 00:00 UTC GTA VI NZ unlock · 00:30 UTC ABS AU jobs · "
    "01:42 UTC Riyadh all-clear · 04:05 UTC Suneung halt · 09:00 UTC ICJ sitting · 14:30 UTC ANT IPO."
)
DATE_CHECK_LINE3 = (
    "Left out on purpose as Wed 18 Nov / earlier news: Kerch Bridge strike, Van Gogh $190.4m sale, "
    "Voyager 1 light-day (10:16 GMT Wed), EU €45bn Ukraine loan, Jeffries 251–11 vote, "
    "Kuwait/Bahrain drones, Peltola Alaska win, Pew 2035 report."
)
FOOTER_TEXT = (
    "Claims by warring sides are attributed. Original drawings. Every story happened or was first reported "
    "Thursday 19 November 2026. Sources: Reuters, AP, AFP, Bloomberg, Al Jazeera, Guardian, BBC, Nature, UN/ICJ."
)

KPI_STRIP = (
    ("$81.3bn", "raised by Anthropic — largest", "IPO on record ($83 ANT)"),
    ("15.9m", "GTA VI pre-orders banked", "before midnight release"),
    ("200,000", "evacuated in Odisha ahead", "of Cyclone Akvan landfall"),
    ("$120bn", "annual adaptation finance", "unresolved at COP31 crunch"),
    ("730,000", "Rohingya who fled in 2017 —", "the ICJ genocide judgment"),
    ("17 in", "South Florida deluge triggers", "300 rescues & school closures"),
)

LEAD_STORIES = [
    {
        "num": 1,
        "region": "ASIA-PACIFIC",
        "beat": "SUMMIT",
        "city": "SHENZHEN",
        "agency": "REUTERS / AP",
        "headline": "Trump, Xi and Putin Hold First Three-Way Summit",
        "subdeck": (
            "The three nuclear powers meet on APEC sidelines in Shenzhen; "
            "arms control, Ukraine and Gulf tensions top the agenda."
        ),
        "caption": "SHENZHEN · HISTORIC TRILATERAL SUMMIT",
        "pastel": "blush",
        "true_lat": 22.54,
        "true_lon": 114.06,
        "pin_lat": 22.54,
        "pin_lon": 114.06,
    },
    {
        "num": 2,
        "region": "AMERICAS",
        "beat": "MARKETS",
        "city": "NEW YORK",
        "agency": "REUTERS / BLOOMBERG",
        "headline": "Anthropic Debuts in Record $81.3bn Nasdaq IPO",
        "subdeck": (
            "Priced at $83 above its range (~$1.5tn valuation), Claude AI "
            "maker sells 980m shares as ANT trades Thursday."
        ),
        "caption": "NEW YORK · NASDAQ: ANT RECORD AI IPO DEBUT",
        "pastel": "sky",
        "true_lat": 40.71,
        "true_lon": -74.01,
        "pin_lat": 40.71,
        "pin_lon": -74.01,
    },
    {
        "num": 3,
        "region": "GLOBAL & OCEANIA",
        "beat": "GAMES",
        "city": "AUCKLAND",
        "agency": "AFP / AP",
        "headline": "GTA VI Arrives at Midnight After 13-Year Wait",
        "subdeck": (
            "Rockstar's sequel unlocks at local midnight led by New Zealand & "
            "Australia; 15.9m pre-orders ($1.5bn) banked on PS5 & Xbox."
        ),
        "caption": "GLOBAL · VICE CITY UNLOCKS AT LOCAL MIDNIGHT",
        "pastel": "space",
        "true_lat": -36.85,
        "true_lon": 174.76,
        "pin_lat": -36.85,
        "pin_lon": 174.76,
    },
    {
        "num": 4,
        "region": "EUROPE",
        "beat": "JUSTICE",
        "city": "THE HAGUE",
        "agency": "UN / ICJ",
        "headline": "World Court Rules on Rohingya Genocide Case",
        "subdeck": (
            "The ICJ reads its 10:00 CET judgment in The Hague in "
            "The Gambia's case over Myanmar's 2017 campaign."
        ),
        "caption": "THE HAGUE · PEACE PALACE GENOCIDE JUDGMENT",
        "pastel": "sky",
        "true_lat": 52.08,
        "true_lon": 4.30,
        "pin_lat": 63.00,
        "pin_lon": -18.00,
    },
    {
        "num": 5,
        "region": "MIDDLE EAST",
        "beat": "CLIMATE",
        "city": "ANTALYA",
        "agency": "UNFCCC / GUARDIAN",
        "headline": "COP31 Enters Final 48h Crunch in Antalya",
        "subdeck": (
            "Ministers take over the 18-page text as fossil phase-out "
            "and the $120bn adaptation fund remain open."
        ),
        "caption": "ANTALYA · COP31 $120BN ADAPTATION CRUNCH",
        "pastel": "sage",
        "true_lat": 36.89,
        "true_lon": 30.71,
        "pin_lat": 45.00,
        "pin_lon": 15.00,
    },
    {
        "num": 6,
        "region": "ASIA-PACIFIC",
        "beat": "CYCLONE",
        "city": "ODISHA",
        "agency": "PTI / THE HINDU",
        "headline": "Cyclone Akvan Forces 200k Off Odisha Coast",
        "subdeck": (
            "11 districts on red alert and schools shut as 145 km/h "
            "storm nears Friday landfall near Puri."
        ),
        "caption": "ODISHA · 200,000 EVACUATED AHEAD OF LANDFALL",
        "pastel": "sky",
        "true_lat": 19.81,
        "true_lon": 85.83,
        "pin_lat": 19.81,
        "pin_lon": 85.83,
    },
    {
        "num": 7,
        "region": "EUROPE",
        "beat": "DIPLOMACY",
        "city": "KYIV",
        "agency": "REUTERS / BBC",
        "headline": "Left Off Agenda, Ukraine Watches Shenzhen",
        "subdeck": (
            "White House says war will not be raised at summit as "
            "Kyiv and allies warn against a carve-up."
        ),
        "caption": "KYIV & BERLIN · UKRAINE WATCHES SHENZHEN",
        "pastel": "slate",
        "true_lat": 50.45,
        "true_lon": 30.52,
        "pin_lat": 61.00,
        "pin_lon": 40.00,
    },
    {
        "num": 8,
        "region": "MIDDLE EAST",
        "beat": "WAR",
        "city": "GAZA",
        "agency": "REUTERS / BBC",
        "headline": "Israeli Tanks Cross Gaza Ceasefire Line",
        "subdeck": (
            "IDF says rare ground raid hit militant sites in central Gaza; "
            "Hamas calls the advance a truce breach."
        ),
        "caption": "CENTRAL GAZA · TANKS CROSS CEASEFIRE LINE",
        "pastel": "blush",
        "true_lat": 31.42,
        "true_lon": 34.37,
        "pin_lat": 22.00,
        "pin_lon": 32.00,
    },
    {
        "num": 9,
        "region": "AMERICAS",
        "beat": "WEATHER",
        "city": "FLORIDA",
        "agency": "AP / CBS MIAMI",
        "headline": "Flooded South Florida Braces for More Rain",
        "subdeck": (
            "Up to 17 inches of rain trigger 300 overnight rescue calls "
            "in Broward, closing major schools Thursday."
        ),
        "caption": "SOUTH FLORIDA · 300 RESCUES & SCHOOL CLOSURES",
        "pastel": "sky",
        "true_lat": 25.76,
        "true_lon": -80.19,
        "pin_lat": 16.00,
        "pin_lon": -84.00,
    },
    {
        "num": 10,
        "region": "GLOBAL & OCEANIA",
        "beat": "SCIENCE",
        "city": "COLORADO",
        "agency": "NATURE / REUTERS",
        "headline": "Earth's Missing Billion Years Explained",
        "subdeck": (
            "A Nature study blames ancient mantle currents and ice sheets "
            "for erasing a billion-year rock record."
        ),
        "caption": "SCIENCE · NATURE GREAT UNCONFORMITY STUDY",
        "pastel": "cream",
        "true_lat": 38.80,
        "true_lon": -104.90,
        "pin_lat": 38.80,
        "pin_lon": -104.90,
    },
    {
        "num": 11,
        "region": "EUROPE",
        "beat": "POLITICS",
        "city": "PARIS",
        "agency": "AFP / LE MONDE",
        "headline": "Mélenchon Could Win, Says Justice Minister",
        "subdeck": (
            "French Justice Minister concedes hard-left leader "
            "Jean-Luc Mélenchon is a plausible 2027 winner."
        ),
        "caption": "PARIS · FRENCH 2027 PRESIDENTIAL WARNING",
        "pastel": "slate",
        "true_lat": 48.86,
        "true_lon": 2.35,
        "pin_lat": 41.00,
        "pin_lon": -16.00,
    },
    {
        "num": 12,
        "region": "MIDDLE EAST",
        "beat": "GULF",
        "city": "RIYADH",
        "agency": "AFP / AL JAZEERA",
        "headline": "Saudi Arabia Says Danger Passed in South",
        "subdeck": (
            "Civil Defense lifts alerts in Riyadh, Jazan and Najran "
            "after intercepting a Houthi ballistic missile."
        ),
        "caption": "RIYADH & JAZAN · MISSILE INTERCEPT ALL-CLEAR",
        "pastel": "cream",
        "true_lat": 24.71,
        "true_lon": 46.68,
        "pin_lat": 11.00,
        "pin_lon": 56.00,
    },
    {
        "num": 13,
        "region": "AFRICA",
        "beat": "CRIME",
        "city": "BENGHAZI",
        "agency": "AFP / REUTERS",
        "headline": "Cocaine and Millions of Pills Seized in Libya",
        "subdeck": (
            "Benghazi authorities display one of Libya's largest "
            "narcotic hauls seized in a sweeping eastern raid."
        ),
        "caption": "BENGHAZI · EASTERN LIBYA NARCOTICS SEIZURE",
        "pastel": "blush",
        "true_lat": 32.12,
        "true_lon": 20.07,
        "pin_lat": 10.00,
        "pin_lon": 10.00,
    },
]

BRIEF_STORIES = [
    {"num": 14, "region": "ASIA-PACIFIC", "city": "Seoul", "summary": "Korea halts flights 35 mins and delays markets as 550,000 sit Suneung exam.", "true_lat": 37.57, "true_lon": 126.98},
    {"num": 15, "region": "ASIA-PACIFIC", "city": "Shenzhen", "summary": "APEC leaders adopt 21-economy Declaration backing digital trade roadmap.", "true_lat": 22.54, "true_lon": 114.06},
    {"num": 16, "region": "ASIA-PACIFIC", "city": "Tokyo", "summary": "India and Japan ministers hold 2+2 talks to expand maritime defence ties.", "true_lat": 35.68, "true_lon": 139.77},
    {"num": 17, "region": "ASIA-PACIFIC", "city": "New Delhi", "summary": "PM Modi meets Prince and Princess of Wales to advance UK–India trade ties.", "true_lat": 28.61, "true_lon": 77.21},
    {"num": 18, "region": "ASIA-PACIFIC", "city": "Bengaluru", "summary": "Amazon pledges $7bn for renewable energy expansion across India by 2030.", "true_lat": 12.97, "true_lon": 77.59},
    {"num": 19, "region": "ASIA-PACIFIC", "city": "Jakarta", "summary": "EU governments clear tariff-cutting trade pact with Indonesia.", "true_lat": -6.21, "true_lon": 106.85},
    {"num": 20, "region": "GLOBAL & OCEANIA", "city": "Canberra", "summary": "Australia sanctions West Bank settlers, naming three people and four groups.", "true_lat": -35.28, "true_lon": 149.13},
    {"num": 21, "region": "GLOBAL & OCEANIA", "city": "Sydney", "summary": "Australian jobless rate jumps to 4.9% in October as 43,500 jobs are shed.", "true_lat": -33.87, "true_lon": 151.21},
    {"num": 22, "region": "GLOBAL & OCEANIA", "city": "Nuku'alofa", "summary": "Tonga declares 27-day national emergency over worsening El Niño drought.", "true_lat": -21.14, "true_lon": -175.20},
    {"num": 23, "region": "MIDDLE EAST", "city": "Manama", "summary": "Bahrain's Bapco refinery resumes operations following Gulf attacks.", "true_lat": 26.22, "true_lon": 50.59},
    {"num": 24, "region": "MIDDLE EAST", "city": "Baghdad", "summary": "Iraqi court sentences six French ISIL members to life imprisonment.", "true_lat": 33.31, "true_lon": 44.36},
    {"num": 25, "region": "MIDDLE EAST", "city": "Hormuz", "summary": "UKMTO reports projectile strike on tanker engine room off Khasab; crew safe.", "true_lat": 26.20, "true_lon": 56.25},
    {"num": 26, "region": "EUROPE", "city": "Frankfurt", "summary": "Financial Times reports Deutsche Bank handled $582m in Epstein-linked deals.", "true_lat": 50.11, "true_lon": 8.68},
    {"num": 27, "region": "EUROPE", "city": "Brussels", "summary": "EU negotiators agree to delay oil-and-gas import methane rules by two years.", "true_lat": 50.85, "true_lon": 4.35},
    {"num": 28, "region": "EUROPE", "city": "London", "summary": "Final UK marine report on Bayesian sinking cites unassessed wind risk.", "true_lat": 51.51, "true_lon": -0.13},
    {"num": 29, "region": "EUROPE", "city": "Helsinki", "summary": "Nokia, Nscale and Telia form consortium for Nordic–Baltic AI Gigafactory.", "true_lat": 60.17, "true_lon": 24.94},
    {"num": 30, "region": "AFRICA", "city": "Mogadishu", "summary": "Somalia formally accuses the UAE of operating secret military bases.", "true_lat": 2.05, "true_lon": 45.32},
    {"num": 31, "region": "AFRICA", "city": "Nairobi", "summary": "Kenya flash floods kill six as President Ruto delivers State of the Nation.", "true_lat": -1.29, "true_lon": 36.82},
    {"num": 32, "region": "AFRICA", "city": "Kinshasa", "summary": "Africa CDC warns DR Congo Ebola outbreak has passed 5,500 deaths.", "true_lat": -4.32, "true_lon": 15.31},
    {"num": 33, "region": "AMERICAS", "city": "Ottawa", "summary": "PM Carney says Canada is adjusting China ties while seeking a US deal.", "true_lat": 45.42, "true_lon": -75.70},
    {"num": 34, "region": "AMERICAS", "city": "Mexico City", "summary": "Banxico publishes 3–2 split minutes on rate cut to 6.25% amid inflation.", "true_lat": 19.43, "true_lon": -99.13},
    {"num": 35, "region": "AMERICAS", "city": "Washington", "summary": "US senators warn AI cyber threats are outpacing national defences.", "true_lat": 38.91, "true_lon": -77.04},
    {"num": 36, "region": "AMERICAS", "city": "La Paz", "summary": "Bolivia declares national El Niño emergency after floods hit 78,000 families.", "true_lat": -16.50, "true_lon": -68.15},
]

MAP_BOX = (28, 1388, 700, 1924)
MAP_VIEW = (42, 1428, 686, 1782)
MAP_LON_MIN, MAP_LON_MAX = -180.0, 180.0
MAP_LAT_MIN, MAP_LAT_MAX = -60.0, 82.0

CONTINENT_POLYGONS = [
    # North & Central America
    [
        (68, -166), (71, -156), (70, -130), (69, -105), (64, -90),
        (58, -94), (52, -81), (58, -77), (62, -77), (60, -65),
        (52, -56), (47, -53), (45, -61), (42, -70), (40, -74),
        (35, -75), (30, -81), (25, -80), (26, -82), (29, -84),
        (30, -89), (28, -96), (22, -97), (19, -96), (21, -90),
        (21, -87), (16, -88), (15, -83), (10, -83), (8, -78),
        (9, -84), (14, -92), (17, -101), (23, -106), (31, -114),
        (24, -110), (32, -117), (38, -123), (48, -125), (54, -132),
        (59, -140), (60, -151), (56, -160), (60, -166), (65, -168),
    ],
    # Greenland
    [
        (60, -44), (65, -40), (70, -22), (77, -18), (82, -28),
        (82, -50), (77, -70), (72, -56), (66, -53),
    ],
    # Cuba / Hispaniola
    [(22, -84), (23, -80), (20, -74), (19, -77)],
    [(20, -74), (19, -69), (18, -71), (18, -74)],
    # South America
    [
        (11, -74), (11, -63), (7, -55), (1, -49), (-5, -35),
        (-12, -38), (-22, -41), (-33, -52), (-38, -57), (-46, -66),
        (-54, -68), (-55, -71), (-46, -75), (-35, -72), (-20, -70),
        (-14, -76), (-5, -81), (2, -79), (8, -77),
    ],
    # Great Britain & Ireland
    [(50, -5), (51, 1), (53, 0), (56, -3), (58, -3), (58, -6), (55, -5), (52, -5)],
    [(52, -10), (55, -8), (54, -6), (52, -6)],
    # Iceland
    [(64, -23), (66, -22), (66, -14), (64, -15)],
    # Eurasia (Europe, Arabia, Asia)
    [
        (36, -6), (37, -9), (43, -9), (43, -2), (47, -4), (50, 1),
        (53, 6), (57, 8), (57, 10.5), (54, 10), (54, 14), (55, 19),
        (59, 23), (60, 29), (65, 24), (60, 18), (56, 13), (59, 11),
        (59, 5), (65, 12), (70, 20), (71, 28), (69, 34), (68, 45),
        (69, 60), (72, 72), (76, 104), (72, 135), (69, 165), (66, 178),
        (61, 172), (56, 162), (52, 157), (59, 150), (55, 137), (46, 138),
        (40, 129), (35, 129), (35, 126), (38, 124), (39, 119), (35, 120),
        (31, 122), (24, 118), (21, 110), (17, 108), (10, 106), (13, 101),
        (6, 103), (1.5, 104), (4, 100), (10, 98), (16, 96), (22, 91),
        (19, 85), (12, 80), (8, 77), (15, 74), (21, 72), (24, 67),
        (25, 61), (26, 56), (30, 49), (26, 51), (24, 55), (22, 59),
        (16, 53), (12, 44), (20, 40), (28, 35), (31, 32.5), (33, 35),
        (36, 36), (36, 29), (40, 27), (41, 32), (42, 41), (46, 35),
        (45, 31), (41, 28), (40, 25), (38, 24), (37, 22), (40, 20),
        (45, 14), (42, 16), (40, 18), (38, 16), (41, 13), (44, 9),
        (43, 5), (41, 2), (37, -1),
    ],
    # Africa & Madagascar
    [
        (35, -6), (37, 10), (32, 15), (32, 32.5), (22, 37), (12, 44),
        (11, 51), (2, 45), (-10, 40), (-25, 33), (-34, 25), (-34, 18),
        (-22, 14), (-10, 13), (4, 9), (5, -4), (10, -15), (21, -17),
        (30, -10),
    ],
    [(-12, 49), (-16, 50), (-25, 47), (-25, 44), (-16, 44)],
    # Sri Lanka, Taiwan, Japan, Philippines, Indonesia, New Guinea
    [(9.5, 80), (7.5, 82), (6, 80.5), (7.5, 79.5)],
    [(25, 121.5), (22, 121), (23, 120)],
    [(31, 130.5), (34, 131), (36, 137), (41, 140), (45, 142), (43.5, 145), (41, 141.5), (36, 140.5), (33.5, 135.5), (31, 131.5)],
    [(18, 121), (14, 122), (10, 126), (6, 125), (9, 122), (14, 120)],
    [(5, 95), (1, 103), (-6, 106), (-4, 102), (2, 97)],
    [(6, 116), (2, 118), (-3, 115), (-3, 110), (2, 109)],
    [(-6, 106), (-7, 114), (-8.5, 114), (-8.5, 106)],
    [(-1, 132), (-4, 142), (-9, 148), (-10, 145), (-6, 135), (-3, 131)],
    # Australia, Tasmania, New Zealand
    [
        (-12, 131), (-12, 136), (-15, 136), (-11, 142), (-19, 147),
        (-26, 153), (-35, 151), (-38, 144), (-35, 137), (-32, 130),
        (-34, 122), (-34, 115), (-22, 114), (-16, 123), (-14, 129),
    ],
    [(-41, 145), (-41, 148), (-43.5, 147), (-43.5, 145)],
    [(-34.5, 172.5), (-37.5, 178.5), (-41.5, 175.5), (-38.5, 173.5)],
    [(-41, 173), (-44.5, 172), (-46.5, 167), (-44, 166.5)],
]


def _wrap_text(text: str, font, max_width: float, max_lines: int) -> list[str]:
    """Wrap words cleanly to fit max_width within max_lines without mid-word breaks."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip() if current else word
        if font.getlength(candidate) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
            if len(lines) >= max_lines:
                break
    if current and len(lines) < max_lines:
        lines.append(current)
    elif current and len(lines) == max_lines:
        last_try = f"{lines[-1]} {current}".strip()
        if font.getlength(last_try) <= max_width:
            lines[-1] = last_try
    return lines


def _draw_centered_text(draw, cx: float, cy: float, text: str, font, fill: str) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cx - tw / 2.0 - bbox[0], cy - th / 2.0 - bbox[1]), text, font=font, fill=fill)


def _geo_to_px(lat: float, lon: float) -> tuple[float, float]:
    vx0, vy0, vx1, vy1 = MAP_VIEW
    x = vx0 + (lon - MAP_LON_MIN) / (MAP_LON_MAX - MAP_LON_MIN) * (vx1 - vx0)
    y = vy0 + (MAP_LAT_MAX - lat) / (MAP_LAT_MAX - MAP_LAT_MIN) * (vy1 - vy0)
    return x, y


def _draw_star(draw, cx: float, cy: float, r_outer: float, r_inner: float, points: int, fill: str, outline: str | None = None) -> None:
    verts = []
    for i in range(points * 2):
        angle = -math.pi / 2.0 + i * math.pi / points
        r = r_outer if i % 2 == 0 else r_inner
        verts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(verts, fill=fill, outline=outline)


def _draw_palm(draw, bx: float, by: float, h: float, lean: float, color: str) -> None:
    tx, ty = bx + lean, by - h
    draw.line([(bx, by), (bx + lean * 0.55, by - h * 0.55), (tx, ty)], fill=color, width=max(3, int(h * 0.08)))
    for ang_deg in (-150, -110, -55, -20, 15):
        ang = math.radians(ang_deg)
        fx = tx + math.cos(ang) * (h * 0.42)
        fy = ty + math.sin(ang) * (h * 0.34) + h * 0.08
        mx = (tx + fx) / 2.0
        my = (ty + fy) / 2.0 - h * 0.07
        draw.polygon([(tx, ty), (mx, my), (fx, fy), (mx, my + h * 0.06)], fill=color)


def _draw_scene_1(art_canvas, draw, fonts: FontBank) -> None:
    """#1 Shenzhen Trilateral Summit: lakeside Kylin Villa, flags, 3 leaders."""
    _ = fonts
    w, h = art_canvas.size
    for band_y, col in ((0, "#FAF0EC"), (24, "#F5E1DA"), (48, "#EED5CB")):
        draw.rectangle([0, band_y, w, band_y + 26], fill=col)
    for cx, cy, r in ((86, 26, 14), (104, 22, 16), (518, 24, 14), (538, 28, 12)):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#FDF8F6")
    draw.rectangle([0, 72, w, h], fill="#D6E4EC")
    draw.line([(0, 72), (w, 72)], fill="#94A3B8", width=2)
    for ry in (84, 96, 108):
        draw.line([(48, ry), (212, ry)], fill="#B0C4D4", width=2)
        draw.line([(416, ry), (580, ry)], fill="#B0C4D4", width=2)

    # Kylin Villa tiered pavilion roof silhouette
    draw.rectangle([210, 46, 418, 72], fill="#CBD5E1", outline="#64748B", width=2)
    for px in (228, 264, 300, 336, 372, 400):
        draw.rectangle([px - 4, 48, px + 4, 72], fill="#64748B")
    draw.polygon([(186, 48), (314, 24), (442, 48)], fill="#334155")
    draw.polygon([(228, 28), (314, 10), (400, 28)], fill="#1E293B")

    # Three leader silhouettes behind curved table
    for lx, col in ((170, "#1E293B"), (314, "#0F172A"), (458, "#334155")):
        draw.ellipse([lx - 15, 52, lx + 15, 82], fill=col)
        draw.pieslice([lx - 36, 82, lx + 36, 126], 180, 360, fill=col)

    # Curved diplomatic walnut table
    draw.pieslice([76, 94, w - 76, 196], 180, 360, fill="#78350F", outline="#451A03", width=3)
    draw.pieslice([126, 110, w - 126, 186], 180, 360, fill="#92400E")

    # Stylized miniature flags (US, China, Russia)
    fx, fy = 148, 78
    draw.line([(fx, fy), (fx, 110)], fill="#111827", width=3)
    draw.rectangle([fx + 2, fy, fx + 44, fy + 26], fill="#FFFFFF", outline="#475569", width=1)
    for sy in range(0, 26, 6):
        draw.rectangle([fx + 2, fy + sy, fx + 44, fy + sy + 3], fill="#B91C1C")
    draw.rectangle([fx + 2, fy, fx + 20, fy + 14], fill="#1D4ED8")

    fx, fy = 292, 72
    draw.line([(fx, fy), (fx, 104)], fill="#111827", width=3)
    draw.rectangle([fx + 2, fy, fx + 44, fy + 26], fill="#DC2626", outline="#991B1B", width=1)
    _draw_star(draw, fx + 12, fy + 9, 5.5, 2.3, 5, "#FACC15")

    fx, fy = 436, 78
    draw.line([(fx, fy), (fx, 110)], fill="#111827", width=3)
    draw.rectangle([fx + 2, fy, fx + 44, fy + 8], fill="#FFFFFF", outline="#64748B", width=1)
    draw.rectangle([fx + 2, fy + 8, fx + 44, fy + 17], fill="#1D4ED8")
    draw.rectangle([fx + 2, fy + 17, fx + 44, fy + 26], fill="#DC2626")

    draw.arc([280, 112, 348, 140], 190, 350, fill="#D97706", width=3)


def _draw_scene_2(art_canvas, draw, fonts: FontBank) -> None:
    """#2 Anthropic Record $81.3bn Nasdaq IPO: Manhattan tower, neural nodes, rising chart."""
    w, h = art_canvas.size
    draw.text((18, 8), "$81.3bn", font=fonts.get("serif_bold", 46), fill="#0F172A")

    skyline = [(22, h, 72, 74, "#94A3B8"), (78, h, 132, 66, "#64748B"), (138, h, 186, 82, "#94A3B8")]
    for x0, y1, x1, y0, col in skyline:
        draw.rectangle([x0, y0, x1, y1], fill=col)
        for wy in range(y0 + 10, y1 - 8, 12):
            draw.line([(x0 + 6, wy), (x1 - 6, wy)], fill="#E2E8F0", width=2)

    for gy in (32, 62, 92, 122):
        draw.line([(338, gy), (596, gy)], fill="#CBDCEB", width=1)

    # Curved Nasdaq tower positioned cleanly right of $81.3bn hero figure
    draw.rectangle([198, 42, 268, h], fill="#1E3A8A", outline="#0F172A", width=2)
    draw.pieslice([198, 30, 268, 54], 180, 360, fill="#3B82F6", outline="#0F172A", width=2)
    for gy in (64, 86, 108, 130):
        draw.line([(200, gy), (266, gy)], fill="#60A5FA", width=2)
    for gx in (216, 233, 250):
        draw.line([(gx, 42), (gx, h)], fill="#1D4ED8", width=2)

    nodes = [(284, 34), (314, 18), (336, 46), (296, 62), (326, 72)]
    for i, p1 in enumerate(nodes):
        for p2 in nodes[i + 1:]:
            draw.line([p1, p2], fill="#0F766E", width=2)
    for nx, ny in nodes:
        draw.ellipse([nx - 4.5, ny - 4.5, nx + 4.5, ny + 4.5], fill="#14B8A6", outline="#0F172A", width=1)

    bar_heights = [26, 38, 52, 68, 86, 106, 126]
    bx = 348
    for idx, bh in enumerate(bar_heights):
        col = "#0F766E" if idx < 5 else ("#059669" if idx == 5 else "#10B981")
        draw.rectangle([bx, h - bh, bx + 28, h], fill=col, outline="#064E3B", width=1)
        bx += 35
    draw.line([(342, 114), (468, 72), (576, 20)], fill="#B91C1C", width=5)
    draw.polygon([(588, 12), (562, 14), (578, 34)], fill="#B91C1C")


def _draw_scene_3(art_canvas, draw, fonts: FontBank) -> None:
    """#3 GTA VI Midnight Unlock on #0B1324: neon sunset, Vice City skyline, palms, gamepad."""
    w, h = art_canvas.size
    for sx, sy in ((184, 18), (236, 12), (412, 16), (478, 24), (544, 14), (586, 30)):
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill="#E2E8F0")

    draw.rectangle([0, 78, w, 94], fill="#831843")
    draw.rectangle([0, 94, w, 108], fill="#BE185D")
    draw.rectangle([0, 108, w, h], fill="#1E1B4B")
    sun_cx, sun_cy, sr = 314, 82, 52
    draw.pieslice([sun_cx - sr, sun_cy - sr, sun_cx + sr, sun_cy + sr], 180, 360, fill="#F97316")
    draw.pieslice([sun_cx - sr, sun_cy - sr, sun_cx + sr, sun_cy + sr], 200, 340, fill="#FACC15")
    for sy in (54, 66, 76):
        draw.rectangle([sun_cx - sr, sy, sun_cx + sr, sy + 3], fill="#0B1324")

    buildings = [
        (164, 64, 202, 108, "#1E1B4B", "#EC4899"),
        (206, 44, 248, 108, "#312E81", "#38BDF8"),
        (252, 58, 286, 108, "#1E1B4B", "#FACC15"),
        (340, 52, 378, 108, "#312E81", "#EC4899"),
        (384, 38, 426, 108, "#1E1B4B", "#38BDF8"),
        (430, 66, 466, 108, "#312E81", "#F97316"),
    ]
    for x0, y0, x1, y1, bcol, wcol in buildings:
        draw.rectangle([x0, y0, x1, y1], fill=bcol)
        for wy in range(y0 + 8, y1 - 6, 10):
            draw.line([(x0 + 6, wy), (x1 - 6, wy)], fill=wcol, width=2)

    for ry, rcol in ((116, "#EC4899"), (126, "#F97316"), (136, "#38BDF8")):
        draw.line([(170, ry), (460, ry)], fill=rcol, width=2)

    _draw_palm(draw, 54, 140, 88, 14, "#090D16")
    _draw_palm(draw, 118, 142, 66, -12, "#0F172A")
    _draw_palm(draw, 566, 140, 86, -14, "#090D16")
    _draw_palm(draw, 506, 142, 64, 12, "#0F172A")

    draw.text((20, 8), "15.9M", font=fonts.get("serif_bold", 48), fill="#FDE047")

    gx, gy = 398, 106
    draw.rounded_rectangle([gx - 58, gy - 22, gx + 58, gy + 20], radius=20, fill="#0F172A", outline="#EC4899", width=3)
    draw.ellipse([gx - 68, gy - 4, gx - 28, gy + 32], fill="#0F172A", outline="#EC4899", width=2)
    draw.ellipse([gx + 28, gy - 4, gx + 68, gy + 32], fill="#0F172A", outline="#EC4899", width=2)
    draw.ellipse([gx - 36, gy - 8, gx - 18, gy + 10], fill="#38BDF8")
    for dx, dy, c in ((28, -10, "#EC4899"), (40, -1, "#FACC15"), (28, 8, "#38BDF8"), (16, -1, "#34D399")):
        draw.ellipse([gx + dx - 4, gy + dy - 4, gx + dx + 4, gy + dy + 4], fill=c)


def _draw_scene_4(art_canvas, draw, fonts: FontBank) -> None:
    """#4 ICJ Rohingya Verdict: Peace Palace, scales of justice, UN disc."""
    _ = fonts
    w, h = art_canvas.size
    draw.rectangle([22, 44, 174, h], fill="#B45309", outline="#78350F", width=2)
    draw.polygon([(14, 44), (98, 28), (182, 44)], fill="#334155")
    draw.rectangle([46, 16, 74, 44], fill="#9A3412", outline="#78350F", width=1)
    draw.polygon([(42, 16), (60, 4), (78, 16)], fill="#1E293B")
    for wx in (38, 74, 110, 146):
        draw.rectangle([wx, 54, wx + 16, 82], fill="#E2E8F0")

    cx, cy = 266, 46
    draw.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill="#1D4ED8", outline="#93C5FD", width=3)
    draw.line([(cx, 12), (cx, 78)], fill="#FACC15", width=4)
    draw.line([(cx - 30, 26), (cx + 30, 26)], fill="#FACC15", width=4)
    for sx in (cx - 28, cx + 28):
        draw.line([(sx, 26), (sx - 10, 52)], fill="#FDE68A", width=2)
        draw.line([(sx, 26), (sx + 10, 52)], fill="#FDE68A", width=2)
        draw.chord([sx - 12, 46, sx + 12, 60], 0, 180, fill="#FACC15")
    draw.rectangle([cx - 20, 76, cx + 20, 84], fill="#78350F")


def _draw_scene_5(art_canvas, draw, fonts: FontBank) -> None:
    """#5 Antalya COP31 Crunch Day: Mediterranean wave, balance scale of green vs fossil."""
    _ = fonts
    w, h = art_canvas.size
    draw.rectangle([0, 74, w, h], fill="#0284C7")
    draw.polygon([(18, 74), (56, 48), (94, 74)], fill="#FFFFFF", outline="#94A3B8", width=2)
    draw.polygon([(76, 74), (112, 52), (148, 74)], fill="#F1F5F9", outline="#94A3B8", width=2)

    cx = 246
    draw.line([(cx, 14), (cx, 84)], fill="#1E293B", width=4)
    draw.rectangle([cx - 26, 80, cx + 26, 88], fill="#1E293B")
    draw.line([(cx - 60, 24), (cx + 60, 16)], fill="#1E293B", width=4)

    lx, ly = cx - 60, 24
    draw.line([(lx, ly), (lx, 54)], fill="#64748B", width=2)
    draw.ellipse([lx - 18, 42, lx + 4, 62], fill="#059669")
    draw.line([(lx + 10, 56), (lx + 10, 32)], fill="#065F46", width=3)
    for b_deg in (0, 120, 240):
        ba = math.radians(b_deg)
        draw.line([(lx + 10, 32), (lx + 10 + 12 * math.cos(ba), 32 + 12 * math.sin(ba))], fill="#0F766E", width=3)

    rx, ry = cx + 60, 16
    draw.line([(rx, ry), (rx, 50)], fill="#64748B", width=2)
    draw.rectangle([rx - 14, 36, rx - 4, 54], fill="#475569")
    draw.ellipse([rx - 16, 22, rx + 2, 36], fill="#64748B")
    draw.rectangle([rx + 4, 38, rx + 24, 54], fill="#FEF3C7", outline="#B91C1C", width=2)


def _draw_scene_6(art_canvas, draw, fonts: FontBank) -> None:
    """#6 Cyclone Akvan Odisha: swirling storm vortex, coastline, alert & tents."""
    _ = fonts
    w, h = art_canvas.size
    draw.polygon([(0, 62), (170, 72), (220, h), (0, h)], fill="#F5D0A9")
    draw.polygon([(170, 72), (w, 52), (w, h), (220, h)], fill="#0284C7")

    cx, cy = 274, 44
    for r, col, sa in ((38, "#0F766E", 20), (28, "#1E293B", 80), (18, "#0F766E", 160)):
        draw.arc([cx - r, cy - r, cx + r, cy + r], sa, sa + 210, fill=col, width=5)
        draw.arc([cx - r, cy - r, cx + r, cy + r], sa + 180, sa + 350, fill=col, width=4)
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill="#B91C1C")

    _draw_palm(draw, 44, 86, 48, 18, "#166534")
    draw.polygon([(94, 42), (124, 42), (109, 16)], fill="#B91C1C")
    draw.line([(109, 23), (109, 33)], fill="#FEF08A", width=3)
    draw.ellipse([107, 36, 111, 39], fill="#FEF08A")
    for tx in (92, 142):
        draw.polygon([(tx, 86), (tx + 18, 64), (tx + 36, 86)], fill="#EA580C", outline="#9A3412", width=2)


def _draw_scene_7(art_canvas, draw, fonts: FontBank) -> None:
    """#7 Kyiv & Berlin Diplomacy: Ukrainian horizon, classical columns, shield & EU stars."""
    _ = fonts
    w, h = art_canvas.size
    draw.rectangle([0, 0, w, 46], fill="#93C5FD")
    draw.rectangle([0, 46, w, h], fill="#FDE047")
    draw.rectangle([0, 74, w, h], fill="#D6D0C4")

    # Brandenburg / classical diplomatic columns left
    draw.rectangle([22, 22, 152, 32], fill="#94A3B8")
    draw.polygon([(18, 22), (87, 6), (156, 22)], fill="#475569")
    for cx in (30, 56, 82, 108, 134):
        draw.rectangle([cx, 32, cx + 10, 82], fill="#F1F5F9", outline="#64748B", width=1)

    # Ukraine shield emblem + EU star arc right
    sx, sy = 264, 52
    draw.polygon([(sx - 22, sy - 18), (sx + 22, sy - 18), (sx + 18, sy + 6), (sx, sy + 22), (sx - 18, sy + 6)], fill="#1D4ED8")
    draw.polygon([(sx - 19, sy + 2), (sx + 19, sy + 2), (sx + 16, sy + 6), (sx, sy + 20), (sx - 16, sy + 6)], fill="#FACC15")
    for ang_deg in range(-75, 80, 25):
        ang = math.radians(ang_deg - 90)
        ex = sx + math.cos(ang) * 44
        ey = sy + math.sin(ang) * 38
        _draw_star(draw, ex, ey, 5, 2.2, 5, "#B45309")


def _draw_scene_8(art_canvas, draw, fonts: FontBank) -> None:
    """#8 Central Gaza Ceasefire Line: tanks crossing dashed yellow line & watchtower."""
    _ = fonts
    w, h = art_canvas.size
    draw.rectangle([0, 54, w, h], fill="#E7C8A0")
    draw.polygon([(0, 60), (94, 44), (168, 62), (0, 68)], fill="#D4AF7A")

    draw.line([(312, 22), (304, 64)], fill="#475569", width=3)
    draw.line([(334, 22), (342, 64)], fill="#475569", width=3)
    draw.rectangle([304, 12, 342, 26], fill="#334155", outline="#1E293B", width=1)

    for dy in range(32, h - 2, 12):
        x_off = (dy - 32) * 0.55
        draw.line([(168 + x_off, dy), (175 + x_off, dy + 6)], fill="#EAB308", width=6)

    for tx, ty, scale in ((68, 60, 0.8), (182, 64, 0.95)):
        tw, th = int(76 * scale), int(20 * scale)
        draw.rounded_rectangle([tx, ty, tx + tw, ty + th], radius=5, fill="#1E293B")
        for wx in range(tx + 8, tx + tw - 8, int(14 * scale)):
            draw.ellipse([wx, ty + th - int(9 * scale), wx + int(9 * scale), ty + th], fill="#475569")
        draw.polygon([
            (tx + int(10 * scale), ty),
            (tx + int(22 * scale), ty - int(14 * scale)),
            (tx + int(56 * scale), ty - int(14 * scale)),
            (tx + int(64 * scale), ty),
        ], fill="#334155", outline="#0F172A", width=1)
        draw.line([
            (tx + int(54 * scale), ty - int(9 * scale)),
            (tx + int(92 * scale), ty - int(11 * scale)),
        ], fill="#1E293B", width=max(3, int(4 * scale)))


def _draw_scene_9(art_canvas, draw, fonts: FontBank) -> None:
    """#9 South Florida School Floods: storm cloud, rain, yellow school bus in floodwater."""
    _ = fonts
    w, h = art_canvas.size
    for cx, cy, r in ((54, 24, 18), (82, 18, 22), (114, 22, 18), (140, 28, 15), (272, 22, 18), (304, 18, 20), (332, 24, 16)):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#475569")
    for rx in range(28, 344, 24):
        draw.line([(rx, 40), (rx - 8, 64)], fill="#2563EB", width=2)

    _draw_palm(draw, 36, 76, 40, -8, "#166534")
    draw.rectangle([0, 70, w, h], fill="#0284C7")

    bx, by = 112, 36
    draw.rounded_rectangle([bx, by, bx + 144, by + 40], radius=7, fill="#EAB308", outline="#92400E", width=2)
    draw.rectangle([bx + 118, by + 8, bx + 142, by + 23], fill="#1E293B")
    for wx in range(bx + 12, bx + 110, 22):
        draw.rectangle([wx, by + 8, wx + 16, by + 22], fill="#1E293B")
    for whx in (bx + 28, bx + 114):
        draw.ellipse([whx - 10, by + 30, whx + 10, by + 50], fill="#111827")
    draw.arc([bx + 130, 60, bx + 170, 86], 180, 340, fill="#E0F2FE", width=3)
    for wx in (20, 96, 188, 278):
        draw.line([(wx, 82), (wx + 44, 82)], fill="#7DD3FC", width=2)


def _draw_scene_10(art_canvas, draw, fonts: FontBank) -> None:
    """#10 Earth's Missing Billion Years: rock strata cross-section, unconformity gap & glacier."""
    _ = fonts
    w, h = art_canvas.size
    # Upper sedimentary layers
    draw.rectangle([0, 12, w, 28], fill="#D97706")
    draw.rectangle([0, 28, w, 44], fill="#F59E0B")

    # Jagged Great Unconformity erosion boundary gap (cream/slate void + wavy contact)
    unconf = [(0, 44), (48, 52), (96, 40), (144, 54), (192, 42), (240, 52), (288, 40), (336, 50), (w, 44)]
    draw.polygon(unconf + [(w, 64), (0, 64)], fill="#FEF3C7")
    draw.line(unconf, fill="#78350F", width=3)

    # Ancient deep basement rock & mantle convection arrows
    draw.polygon([(0, 62), (64, 56), (128, 66), (192, 58), (256, 66), (320, 58), (w, 64), (w, h), (0, h)], fill="#7C2D12")
    draw.arc([44, 68, 118, 108], 180, 360, fill="#FB923C", width=3)
    draw.arc([148, 68, 222, 108], 180, 360, fill="#FB923C", width=3)

    # Ancient Snowball-Earth ice sheet lobe top-right
    draw.polygon([(232, 0), (w, 0), (w, 42), (296, 40), (262, 26)], fill="#E0F2FE", outline="#0284C7", width=2)


def _draw_scene_11(art_canvas, draw, fonts: FontBank) -> None:
    """#11 French Politics: crisp Tricolore, National Assembly facade & speaker podium."""
    _ = fonts
    w, h = art_canvas.size
    # Tricolore left panel
    draw.rectangle([18, 12, 66, 82], fill="#1D4ED8")
    draw.rectangle([66, 12, 114, 82], fill="#FFFFFF")
    draw.rectangle([114, 12, 162, 82], fill="#DC2626")
    draw.rectangle([18, 12, 162, 82], outline="#64748B", width=2)

    # National Assembly pediment & columns right
    draw.polygon([(192, 32), (272, 8), (352, 32)], fill="#334155")
    draw.rectangle([198, 32, 346, 38], fill="#CBD5E1")
    for cx in (206, 232, 258, 284, 310, 334):
        draw.rectangle([cx, 38, cx + 8, 86], fill="#FFFFFF", outline="#94A3B8", width=1)

    # Parliamentary podium foreground
    draw.polygon([(242, 66), (302, 66), (294, h), (250, h)], fill="#78350F")
    draw.rectangle([234, 60, 310, 68], fill="#92400E")
    draw.line([(260, 60), (266, 46)], fill="#1E293B", width=3)
    draw.ellipse([264, 42, 272, 48], fill="#0F172A")


def _draw_scene_12(art_canvas, draw, fonts: FontBank) -> None:
    """#12 Riyadh Dawn Missile Intercept & All-Clear: Kingdom Centre, Patriot arc."""
    _ = fonts
    w, h = art_canvas.size
    draw.rectangle([0, 66, w, h], fill="#FDE68A")
    draw.rectangle([0, 80, w, h], fill="#FDBA74")

    draw.rectangle([28, 66, 54, h], fill="#475569")
    draw.polygon([(66, h), (84, 32), (102, h)], fill="#334155")
    draw.ellipse([79, 40, 89, 50], fill="#F59E0B")
    draw.polygon([(142, h), (150, 16), (194, 16), (202, h)], fill="#1E293B")
    draw.chord([156, 20, 188, 52], 0, 180, fill="#EFE6D5")
    draw.rectangle([222, 62, 254, h], fill="#475569")

    for i in range(7):
        t = i / 6.0
        px = 24 + t * 246
        py = 76 - math.sin(t * math.pi * 0.56) * 52
        draw.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5], fill="#B91C1C")
    draw.line([(326, 86), (272, 26)], fill="#0F766E", width=4)
    ix, iy = 270, 26
    draw.ellipse([ix - 18, iy - 18, ix + 18, iy + 18], outline="#D97706", width=2)
    _draw_star(draw, ix, iy, 13, 5.5, 8, "#F59E0B", "#B91C1C")
    _draw_star(draw, ix, iy, 6.5, 3, 6, "#FEF3C7")


def _draw_scene_13(art_canvas, draw, fonts: FontBank) -> None:
    """#13 Benghazi Narcotics Seizure: evidence table with contraband bricks & pill capsules."""
    _ = fonts
    w, h = art_canvas.size
    draw.rectangle([0, 56, w, h], fill="#451A03")
    draw.line([(0, 56), (w, 56)], fill="#92400E", width=3)

    # Taped contraband blocks left
    for bx, by in ((24, 36), (78, 36), (48, 22)):
        draw.rounded_rectangle([bx, by, bx + 48, by + 26], radius=4, fill="#F8FAFC", outline="#64748B", width=2)
        draw.line([(bx + 14, by), (bx + 14, by + 26)], fill="#CBD5E1", width=3)
        draw.line([(bx + 34, by), (bx + 34, by + 26)], fill="#CBD5E1", width=3)

    # Large red-white and green-white capsules on evidence table
    for cx, cy, col in ((198, 42, "#DC2626"), (286, 44, "#059669"), (242, 68, "#DC2626")):
        draw.rounded_rectangle([cx - 32, cy - 12, cx + 32, cy + 12], radius=12, fill="#FFFFFF", outline="#334155", width=2)
        draw.pieslice([cx - 32, cy - 12, cx + 10, cy + 12], 90, 270, fill=col)
        draw.rectangle([cx - 12, cy - 12, cx + 2, cy + 12], fill=col)


SCENE_RENDERERS = {
    1: _draw_scene_1,
    2: _draw_scene_2,
    3: _draw_scene_3,
    4: _draw_scene_4,
    5: _draw_scene_5,
    6: _draw_scene_6,
    7: _draw_scene_7,
    8: _draw_scene_8,
    9: _draw_scene_9,
    10: _draw_scene_10,
    11: _draw_scene_11,
    12: _draw_scene_12,
    13: _draw_scene_13,
}


def _draw_scene(story: dict, art_canvas, art_draw, fonts: FontBank) -> None:
    renderer = SCENE_RENDERERS.get(story["num"])
    if renderer is not None:
        renderer(art_canvas, art_draw, fonts)


def _draw_masthead(draw, fonts: FontBank) -> None:
    x0, x1 = 28, 2020
    kicker_font = fonts.get("sans_bold", 20)
    draw.text((x0, 10), "THE DAY IN WORLD NEWS", font=kicker_font, fill=PALETTE["crimson"])

    right_tag = "36 STORIES · 6 REGIONS · ONE DAY"
    rw = kicker_font.getlength(right_tag)
    draw.text((x1 - rw, 10), right_tag, font=kicker_font, fill=PALETTE["sub_ink"])

    draw.line([(x0, 38), (x1, 38)], fill=PALETTE["ink"], width=3)

    title = "Thursday 19 November 2026"
    title_font = fonts.get("serif_bold", 96)
    tb = draw.textbbox((0, 0), title, font=title_font)
    tw = tb[2] - tb[0]
    draw.text(((CANVAS_W - tw) / 2.0 - tb[0], 44 - tb[1]), title, font=title_font, fill=PALETTE["ink"])

    deck_font = fonts.get("serif_italic", 22)
    _draw_centered_text(draw, CANVAS_W / 2.0, 158, MASTHEAD_DECK, deck_font, PALETTE["crimson"])
    draw.line([(x0, 174), (x1, 174)], fill=PALETTE["rule"], width=1)

    total = sum(REGION_COUNTS.values()) or 1
    ry0, ry1 = 180, 212
    gap = 4
    usable_w = (x1 - x0) - gap * (len(REGION_ORDER) - 1)
    cx = float(x0)
    seg_font = fonts.get("sans_condensed_bold", 18)

    for idx, region in enumerate(REGION_ORDER):
        count = REGION_COUNTS.get(region, 0)
        if idx == len(REGION_ORDER) - 1:
            seg_w = float(x1) - cx
        else:
            seg_w = round(usable_w * count / total)
        sx0, sx1 = int(round(cx)), int(round(cx + seg_w))
        draw.rectangle([sx0, ry0, sx1, ry1], fill=REGION_COLORS[region])

        short_region = "GLOBAL/OCEA." if region == "GLOBAL & OCEANIA" and seg_w < 210 else region
        label = f"{short_region} {count}"
        if seg_font.getlength(label) + 12 > (sx1 - sx0):
            label = f"{region.split()[0]} {count}"
        _draw_centered_text(draw, (sx0 + sx1) / 2.0, (ry0 + ry1) / 2.0, label, seg_font, "#FFFFFF")
        cx += seg_w + gap


def _draw_kpi_strip(draw, fonts: FontBank) -> None:
    x0, y0, x1, y1 = 28, 216, 2020, 284
    draw.rectangle([x0, y0, x1, y1], fill="#F5EFE4")
    draw.line([(x0, y0), (x1, y0)], fill="#C8C0B0", width=2)
    draw.line([(x0, y1), (x1, y1)], fill="#C8C0B0", width=2)

    col_w = (x1 - x0) / 6.0
    val_font = fonts.get("serif_bold", 34)
    cap_font = fonts.get("sans_regular", 15)

    for idx, (val, line1, line2) in enumerate(KPI_STRIP):
        cx = x0 + (idx + 0.5) * col_w
        if idx > 0:
            sx = int(round(x0 + idx * col_w))
            draw.line([(sx, y0 + 6), (sx, y1 - 6)], fill="#D6D0C4", width=1)
        _draw_centered_text(draw, cx, y0 + 16, val, val_font, PALETTE["crimson"])
        _draw_centered_text(draw, cx, y0 + 42, line1, cap_font, PALETTE["sub_ink"])
        _draw_centered_text(draw, cx, y0 + 58, line2, cap_font, PALETTE["sub_ink"])


def _draw_card(canvas, draw, fonts: FontBank, story: dict, box: tuple[int, int, int, int], is_lead: bool) -> None:
    x0, y0, x1, y1 = box
    region = story["region"]
    reg_color = REGION_COLORS[region]

    draw.rectangle([x0, y0, x1, y1], fill=PALETTE["card_bg"], outline=PALETTE["rule"], width=2)
    draw.rectangle([x0, y0, x1, y0 + 4], fill=reg_color)

    pad = 12 if is_lead else 11
    art_x = x0 + pad
    art_y = y0 + (10 if is_lead else 8)
    art_w = (x1 - x0) - 2 * pad
    art_h = 175 if is_lead else 125
    cap_h = 32
    scene_h = art_h - cap_h

    from PIL import Image, ImageDraw

    bg_hex = ART_PASTELS[story["pastel"]]
    art_canvas = Image.new("RGB", (art_w, scene_h), bg_hex)
    art_draw = ImageDraw.Draw(art_canvas, "RGBA")
    _draw_scene(story, art_canvas, art_draw, fonts)
    canvas.paste(art_canvas, (art_x, art_y))

    cap_y0 = art_y + scene_h
    cap_y1 = art_y + art_h
    draw.rectangle([art_x, cap_y0, art_x + art_w, cap_y1], fill=PALETTE["caption_bar"])
    cap_font = fonts.get("sans_bold", 16 if is_lead else 14)
    _draw_centered_text(draw, art_x + art_w / 2.0, (cap_y0 + cap_y1) / 2.0, story["caption"], cap_font, "#FFFFFF")
    draw.rectangle([art_x, art_y, art_x + art_w, cap_y1], outline=PALETTE["rule"], width=1)

    meta_y = cap_y1 + (7 if is_lead else 6)
    badge_r = 12 if is_lead else 11
    bx, by = art_x + badge_r, meta_y + badge_r
    draw.ellipse([bx - badge_r, by - badge_r, bx + badge_r, by + badge_r], fill=reg_color)
    badge_font = fonts.get("sans_bold", 15 if is_lead else 14)
    _draw_centered_text(draw, bx, by, str(story["num"]), badge_font, "#FFFFFF")

    kicker_font = fonts.get("sans_condensed_bold", 17 if is_lead else 14)
    agency_font = fonts.get("sans_condensed_bold", 16 if is_lead else 14)
    kicker = f"{region} · {story['beat']}"
    agency = story["agency"]
    aw = agency_font.getlength(agency)
    kx = bx + badge_r + 8
    max_kw = (art_x + art_w - aw - 10) - kx
    if kicker_font.getlength(kicker) > max_kw:
        short_reg = region.replace("GLOBAL & OCEANIA", "GLOBAL")
        kicker = f"{short_reg} · {story['beat']}"
    draw.text((kx, meta_y + (2 if is_lead else 2)), kicker, font=kicker_font, fill=reg_color)
    draw.text((art_x + art_w - aw, meta_y + (3 if is_lead else 2)), agency, font=agency_font, fill=PALETTE["muted"])

    hl_y = meta_y + badge_r * 2 + (5 if is_lead else 4)
    hl_size = 37 if is_lead else 29
    hl_font = fonts.get("serif_bold", hl_size)
    hl_lines = _wrap_text(story["headline"], hl_font, art_w, 2)
    hl_step = 40 if is_lead else 32
    for idx, line in enumerate(hl_lines):
        draw.text((art_x, hl_y + idx * hl_step), line, font=hl_font, fill=PALETTE["ink"])

    sub_y = hl_y + max(len(hl_lines), 1) * hl_step + (5 if is_lead else 5)
    sub_size = 20
    sub_role = "sans_regular" if is_lead else "sans_condensed_regular"
    sub_font = fonts.get(sub_role, sub_size)
    sub_lines = _wrap_text(story["subdeck"], sub_font, art_w, 3)
    sub_step = 23 if is_lead else 23
    for idx, line in enumerate(sub_lines):
        if sub_y + idx * sub_step + sub_size <= y1 - 6:
            draw.text((art_x, sub_y + idx * sub_step), line, font=sub_font, fill=PALETTE["sub_ink"])


def _draw_world_map(draw, fonts: FontBank) -> None:
    mx0, my0, mx1, my1 = MAP_BOX
    draw.rectangle([mx0, my0, mx1, my1], fill=PALETTE["card_bg"], outline=PALETTE["rule"], width=2)

    title_font = fonts.get("sans_bold", 19)
    draw.text((mx0 + 14, my0 + 8), "WHERE IT HAPPENED", font=title_font, fill=PALETTE["ink"])

    vx0, vy0, vx1, vy1 = MAP_VIEW
    draw.rectangle([vx0, vy0, vx1, vy1], fill=PALETTE["ocean"], outline=PALETTE["rule"], width=1)

    for lat in (-45, -30, -15, 0, 15, 30, 45, 60, 75):
        _, gy = _geo_to_px(lat, 0)
        draw.line([(vx0, gy), (vx1, gy)], fill="#CBE0F0", width=1)
    for lon in (-150, -120, -90, -60, -30, 0, 30, 60, 90, 120, 150):
        gx, _ = _geo_to_px(0, lon)
        draw.line([(gx, vy0), (gx, vy1)], fill="#CBE0F0", width=1)

    for poly in CONTINENT_POLYGONS:
        pts = [_geo_to_px(lat, lon) for lat, lon in poly]
        draw.polygon(pts, fill=PALETTE["land"], outline=PALETTE["coast"])

    for story in BRIEF_STORIES:
        dx, dy = _geo_to_px(story["true_lat"], story["true_lon"])
        dx = max(vx0 + 6, min(vx1 - 6, dx))
        dy = max(vy0 + 6, min(vy1 - 6, dy))
        col = REGION_COLORS[story["region"]]
        draw.ellipse([dx - 5, dy - 5, dx + 5, dy + 5], fill=col, outline="#FFFFFF", width=1)

    pin_coords = []
    for story in LEAD_STORIES:
        tx, ty = _geo_to_px(story["true_lat"], story["true_lon"])
        px, py = _geo_to_px(story["pin_lat"], story["pin_lon"])
        px = max(vx0 + 18, min(vx1 - 18, px))
        py = max(vy0 + 18, min(vy1 - 18, py))
        pin_coords.append((story, tx, ty, px, py))

    for story, tx, ty, px, py in pin_coords:
        if math.hypot(px - tx, py - ty) > 6.0:
            draw.line([(tx, ty), (px, py)], fill=PALETTE["ink"], width=2)
        draw.ellipse([tx - 3.5, ty - 3.5, tx + 3.5, ty + 3.5], fill=PALETTE["ink"])

    pin_font = fonts.get("sans_bold", 16)
    for story, _tx, _ty, px, py in pin_coords:
        col = REGION_COLORS[story["region"]]
        r = 15
        draw.ellipse([px - r, py - r, px + r, py + r], fill=col, outline="#FFFFFF", width=2)
        _draw_centered_text(draw, px, py, str(story["num"]), pin_font, "#FFFFFF")

    leg_font = fonts.get("sans_condensed_bold", 18)
    leg_y0 = vy1 + 12
    col_w = 215
    for idx, region in enumerate(REGION_ORDER):
        col_i = idx % 3
        row_i = idx // 3
        lx = vx0 + col_i * col_w
        ly = leg_y0 + row_i * 28
        draw.rectangle([lx, ly + 3, lx + 14, ly + 17], fill=REGION_COLORS[region])
        label = f"{region} ({REGION_COUNTS[region]})"
        draw.text((lx + 20, ly), label, font=leg_font, fill=PALETTE["sub_ink"])

    cap_y = leg_y0 + 64
    cap_font = fonts.get("sans_regular", 18)
    draw.ellipse([vx0, cap_y + 2, vx0 + 16, cap_y + 18], fill=PALETTE["crimson"])
    _draw_centered_text(draw, vx0 + 8, cap_y + 10, "1", fonts.get("sans_bold", 11), "#FFFFFF")
    part1 = "numbered pin: stories 1–13 · "
    draw.text((vx0 + 22, cap_y), part1, font=cap_font, fill=PALETTE["muted"])
    dot_x = vx0 + 22 + cap_font.getlength(part1) + 6
    draw.ellipse([dot_x - 5, cap_y + 5, dot_x + 5, cap_y + 15], fill=PALETTE["muted"])
    part2 = "dot: briefs 14–36"
    draw.text((dot_x + 11, cap_y), part2, font=cap_font, fill=PALETTE["muted"])
    draw.text((vx0, cap_y + 24), "Hairlines lead from crowded spots to true place.", font=cap_font, fill=PALETTE["muted"])


def _draw_briefs_panel(draw, fonts: FontBank) -> None:
    bx0, by0, bx1, by1 = 720, 1388, 2020, 1924
    header_font = fonts.get("sans_bold", 20)
    header = "ALSO ON THURSDAY 19 NOVEMBER — 23 MORE VERIFIED STORIES (#14–#36)"
    draw.text((bx0, by0 + 2), header, font=header_font, fill=PALETTE["ink"])
    draw.line([(bx0, by0 + 30), (bx1, by0 + 30)], fill=PALETTE["ink"], width=2)

    col_w = 638
    gutter = 24
    start_y = by0 + 40
    row_h = 41
    badge_font = fonts.get("sans_bold", 14)
    city_font = fonts.get("sans_bold", 19)
    body_font = fonts.get("sans_regular", 19)
    max_text_w = col_w - 32

    for idx, story in enumerate(BRIEF_STORIES):
        col = 0 if idx < 12 else 1
        row = idx if idx < 12 else idx - 12
        rx = bx0 + col * (col_w + gutter)
        ry = start_y + row * row_h
        col_hex = REGION_COLORS[story["region"]]

        draw.rectangle([rx, ry + 3, rx + 24, ry + 27], fill=col_hex)
        _draw_centered_text(draw, rx + 12, ry + 15, str(story["num"]), badge_font, "#FFFFFF")

        city_prefix = f"{story['city']}: "
        pw = city_font.getlength(city_prefix)
        l1_words: list[str] = []
        l2_words: list[str] = []
        on_l1 = True
        for word in story["summary"].split():
            if on_l1:
                cand = " ".join(l1_words + [word])
                if pw + body_font.getlength(cand) <= max_text_w or not l1_words:
                    l1_words.append(word)
                else:
                    on_l1 = False
                    l2_words.append(word)
            else:
                l2_words.append(word)

        tx = rx + 32
        draw.text((tx, ry), city_prefix, font=city_font, fill=PALETTE["ink"])
        draw.text((tx + pw, ry), " ".join(l1_words), font=body_font, fill=PALETTE["sub_ink"])
        if l2_words:
            draw.text((tx, ry + 20), " ".join(l2_words), font=body_font, fill=PALETTE["sub_ink"])


def _draw_date_check(draw, fonts: FontBank) -> None:
    dx0, dy0, dx1, dy1 = 28, 1932, 2020, 2008
    draw.rectangle([dx0, dy0, dx1, dy1], fill=PALETTE["date_bg"], outline="#F0C6BA", width=1)
    draw.rectangle([dx0, dy0, dx0 + 6, dy1], fill=PALETTE["crimson"])

    bold_font = fonts.get("sans_bold", 19)
    reg_font = fonts.get("sans_regular", 19)

    draw.text((dx0 + 18, dy0 + 7), DATE_CHECK_LINE1, font=bold_font, fill=PALETTE["crimson"])
    draw.text((dx0 + 18, dy0 + 29), DATE_CHECK_LINE2, font=reg_font, fill=PALETTE["ink"])
    draw.text((dx0 + 18, dy0 + 51), DATE_CHECK_LINE3, font=reg_font, fill=PALETTE["sub_ink"])


def _draw_footer(draw, fonts: FontBank) -> None:
    foot_font = fonts.get("sans_semibold", 16)
    draw.text((28, 2016), FOOTER_TEXT, font=foot_font, fill=PALETTE["muted"])


def _draw_broadsheet(canvas, draw, fonts: FontBank) -> None:
    _draw_masthead(draw, fonts)
    _draw_kpi_strip(draw, fonts)

    r1_w = 652
    r1_gap = 18
    for idx in range(3):
        cx0 = 28 + idx * (r1_w + r1_gap)
        _draw_card(canvas, draw, fonts, LEAD_STORIES[idx], (cx0, 292, cx0 + r1_w, 672), is_lead=True)

    r23_w = 388
    r23_gap = 13
    for ry0, ry1, offset in ((684, 1024, 3), (1036, 1376, 8)):
        for col_idx in range(5):
            cx0 = 28 + col_idx * (r23_w + r23_gap)
            _draw_card(
                canvas,
                draw,
                fonts,
                LEAD_STORIES[offset + col_idx],
                (cx0, ry0, cx0 + r23_w, ry1),
                is_lead=False,
            )

    _draw_world_map(draw, fonts)
    _draw_briefs_panel(draw, fonts)
    _draw_date_check(draw, fonts)
    _draw_footer(draw, fonts)


def render_infographic(output_path: Path) -> None:
    """Render the 2048x2048 broadsheet and export 1024x1024 quantized PNG."""
    from PIL import Image, ImageDraw, ImageFont

    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), PALETTE["paper"])
    draw = ImageDraw.Draw(canvas, "RGBA")
    fonts = FontBank(ImageFont)

    _draw_broadsheet(canvas, draw, fonts)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    downsampled = canvas.resize((OUT_W, OUT_H), Image.Resampling.LANCZOS)
    quantized = downsampled.quantize(
        colors=256,
        method=Image.Quantize.FASTOCTREE,
        dither=Image.Dither.NONE,
    )
    quantized.save(output_path, format="PNG", optimize=True)


def main() -> int:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / "entry.png"

    render_flag = os.environ.get("MAKEFUN_RENDER", "").strip().lower()
    if render_flag in {"1", "true", "yes"}:
        render_infographic(dst)
        return 0

    src = Path(__file__).resolve().parent / "entry.png"
    if not src.is_file():
        sys.stderr.write(f"Missing pre-rendered asset: {src}\n")
        return 1
    if src.resolve() != dst.resolve():
        shutil.copyfile(src, dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
