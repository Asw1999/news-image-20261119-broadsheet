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
    "ASIA-PACIFIC": 9,
    "MIDDLE EAST": 7,
    "EUROPE": 8,
    "AFRICA": 4,
    "AMERICAS": 9,
    "GLOBAL & OCEANIA": 5,
}

MASTHEAD_DECK = (
    "3 nuclear leaders meet in Shenzhen · $81.3bn Anthropic record IPO ($83 ANT) · "
    "15.9m GTA VI pre-orders · $190.4m Van Gogh auction record · 730,000 Rohingya ICJ verdict · "
    "200,000 flee Cyclone Akvan"
)
DATE_CHECK_UTC = (
    "00:00 UTC GTA VI NZ unlock · 00:30 UTC ABS AU jobs · 01:15 UTC Van Gogh $190.4m NY hammer · "
    "01:42 UTC Riyadh alert · 04:05 UTC Suneung halt · 09:00 UTC ICJ sitting · 14:30 UTC ANT IPO."
)
DATE_CHECK_EXCLUDED = (
    "Voyager 1 light-day 10:16 GMT (18 Nov), EU €45bn Ukraine loan (18 Nov), Jeffries 251–11 vote (18 Nov), "
    "Kuwait/Bahrain drones (18 Nov), Peltola Alaska call & Pew 2035 report (18 Nov), Fed minutes & Nvidia Q3 (17–18 Nov)."
)
FOOTER_TEXT = (
    "Claims by warring sides are attributed. Original drawings. Every story happened or was first reported "
    "Thursday 19 November 2026. Sources: Reuters, AP, AFP, Bloomberg, Al Jazeera, Guardian, BBC, UN/ICJ, ABS."
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
            "Nuclear powers meet 1 hr on APEC sidelines in Shenzhen; "
            "arms control, Ukraine & Gulf war top agenda."
        ),
        "caption": "SHENZHEN · FIRST TRILATERAL SUMMIT AT APEC",
        "pastel": "blush",
        "true_lat": 22.54,
        "true_lon": 114.06,
        "pin_lat": 18.00,
        "pin_lon": 110.00,
    },
    {
        "num": 2,
        "region": "AMERICAS",
        "beat": "MARKETS",
        "city": "NEW YORK",
        "agency": "REUTERS / BLOOMBERG",
        "headline": "Anthropic Prices Record $81.3bn Nasdaq IPO",
        "subdeck": (
            "Claude AI maker sells 980m shares at $83 (~$1.5tn valuation) "
            "as ANT debuts Thursday, biggest IPO ever."
        ),
        "caption": "NEW YORK · NASDAQ: ANT RECORD AI IPO DEBUT",
        "pastel": "sky",
        "true_lat": 40.71,
        "true_lon": -74.01,
        "pin_lat": 50.00,
        "pin_lon": -54.00,
    },
    {
        "num": 3,
        "region": "GLOBAL & OCEANIA",
        "beat": "CULTURE",
        "city": "AUCKLAND",
        "agency": "AFP / AP",
        "headline": "GTA VI Arrives at Midnight After 13-Year Wait",
        "subdeck": (
            "15.9m pre-orders ($1.5bn) banked as New Zealand & Australia "
            "play first on PS5 & Xbox; leave requests jump 32%."
        ),
        "caption": "GLOBAL · VICE CITY UNLOCKS AT LOCAL MIDNIGHT",
        "pastel": "space",
        "true_lat": -36.85,
        "true_lon": 174.76,
        "pin_lat": -44.00,
        "pin_lon": 170.00,
    },
    {
        "num": 4,
        "region": "EUROPE",
        "beat": "JUSTICE",
        "city": "THE HAGUE",
        "agency": "UN / ICJ",
        "headline": "World Court Rules on Rohingya Case",
        "subdeck": (
            "ICJ reads 10:00 CET verdict in The Hague on Myanmar's "
            "2017 campaign (730k fled)."
        ),
        "caption": "THE HAGUE · PEACE PALACE GENOCIDE JUDGMENT",
        "pastel": "sky",
        "true_lat": 52.08,
        "true_lon": 4.30,
        "pin_lat": 58.00,
        "pin_lon": -18.00,
    },
    {
        "num": 5,
        "region": "ASIA-PACIFIC",
        "beat": "CYCLONE",
        "city": "ODISHA",
        "agency": "PTI / THE HINDU",
        "headline": "Cyclone Akvan Forces 200k Off Coast",
        "subdeck": (
            "11 districts on red alert and schools shut as 145 km/h "
            "storm nears Puri."
        ),
        "caption": "ODISHA · 200,000 EVACUATED AHEAD OF LANDFALL",
        "pastel": "sky",
        "true_lat": 19.81,
        "true_lon": 85.83,
        "pin_lat": -4.00,
        "pin_lon": 84.00,
    },
    {
        "num": 6,
        "region": "MIDDLE EAST",
        "beat": "WAR",
        "city": "GAZA",
        "agency": "REUTERS / BBC",
        "headline": "Israeli Tanks Cross Gaza Yellow Line",
        "subdeck": (
            "IDF says rare raid hit Gaza terror sites; Hamas calls "
            "move a truce breach."
        ),
        "caption": "CENTRAL GAZA · TANKS CROSS CEASEFIRE LINE",
        "pastel": "blush",
        "true_lat": 31.42,
        "true_lon": 34.37,
        "pin_lat": 11.00,
        "pin_lon": 14.00,
    },
    {
        "num": 7,
        "region": "MIDDLE EAST",
        "beat": "CLIMATE",
        "city": "ANTALYA",
        "agency": "UNFCCC / GUARDIAN",
        "headline": "COP31 Enters Final 48h Crunch Talks",
        "subdeck": (
            "Ministers tackle 18-page text with $120bn aid and "
            "fossil phase-out open."
        ),
        "caption": "ANTALYA · COP31 $120BN ADAPTATION CRUNCH",
        "pastel": "sage",
        "true_lat": 36.89,
        "true_lon": 30.71,
        "pin_lat": 44.00,
        "pin_lon": 12.00,
    },
    {
        "num": 8,
        "region": "ASIA-PACIFIC",
        "beat": "TRADE",
        "city": "SHENZHEN",
        "agency": "REUTERS / XINHUA",
        "headline": "APEC Leaders Adopt Shenzhen Pact",
        "subdeck": (
            "21 Pacific Rim economies back digital trade and "
            "supply-chain roadmap."
        ),
        "caption": "SHENZHEN · 21-ECONOMY APEC DECLARATION",
        "pastel": "cream",
        "true_lat": 22.54,
        "true_lon": 114.06,
        "pin_lat": 22.00,
        "pin_lon": 142.00,
    },
    {
        "num": 9,
        "region": "MIDDLE EAST",
        "beat": "SECURITY",
        "city": "RIYADH",
        "agency": "AFP / AL JAZEERA",
        "headline": "Riyadh Downs Missile; All-Clear",
        "subdeck": (
            "Saudi Civil Defense lifts Riyadh, Jazan & Najran alerts "
            "after intercept."
        ),
        "caption": "RIYADH & JAZAN · MISSILE INTERCEPT & ALL-CLEAR",
        "pastel": "blush",
        "true_lat": 24.71,
        "true_lon": 46.68,
        "pin_lat": -2.00,
        "pin_lon": 52.00,
    },
    {
        "num": 10,
        "region": "GLOBAL & OCEANIA",
        "beat": "ECONOMY",
        "city": "SYDNEY",
        "agency": "ABS / GUARDIAN",
        "headline": "Australian Jobless Rate Jumps to 4.9%",
        "subdeck": (
            "ABS logs 43,500 Oct jobs shed, highest since 2021, "
            "cooling hike bets."
        ),
        "caption": "AUSTRALIA · UNEMPLOYMENT HITS 4-YEAR HIGH",
        "pastel": "sky",
        "true_lat": -33.87,
        "true_lon": 151.21,
        "pin_lat": -30.00,
        "pin_lon": 138.00,
    },
    {
        "num": 11,
        "region": "AMERICAS",
        "beat": "CULTURE",
        "city": "NEW YORK",
        "agency": "BBC / AP",
        "headline": "Van Gogh Sells for Record $190.4m",
        "subdeck": (
            "Châtaigniers en fleurs sets 01:15 UTC auction record "
            "after Nazi-era restitution."
        ),
        "caption": "NEW YORK · RECORD $190.4M VAN GOGH AUCTION",
        "pastel": "cream",
        "true_lat": 40.76,
        "true_lon": -73.97,
        "pin_lat": 52.00,
        "pin_lon": -96.00,
    },
    {
        "num": 12,
        "region": "EUROPE",
        "beat": "WAR",
        "city": "CRIMEA",
        "agency": "BBC / GUARDIAN",
        "headline": "Kerch Bridge Halted as Kyiv Watches",
        "subdeck": (
            "Russian officials halt traffic after 3rd hit in week; "
            "Kyiv fears carve-up."
        ),
        "caption": "CRIMEA · KERCH BRIDGE TRAFFIC HALTED",
        "pastel": "sky",
        "true_lat": 45.30,
        "true_lon": 36.51,
        "pin_lat": 60.00,
        "pin_lon": 48.00,
    },
    {
        "num": 13,
        "region": "AMERICAS",
        "beat": "WEATHER",
        "city": "MIAMI",
        "agency": "AP / CBS MIAMI",
        "headline": "South Florida Deluge Shuts Schools",
        "subdeck": (
            "Up to 17 in rain spurs 300 Broward rescues, shutting "
            "South Florida schools."
        ),
        "caption": "SOUTH FLORIDA · 300 RESCUES & SCHOOL CLOSURES",
        "pastel": "sky",
        "true_lat": 25.76,
        "true_lon": -80.19,
        "pin_lat": 12.00,
        "pin_lon": -88.00,
    },
]

BRIEF_STORIES = [
    {"num": 14, "region": "ASIA-PACIFIC", "city": "Seoul", "summary": "Korea halts flights 35 mins and delays markets as 550,000 sit Suneung exam.", "true_lat": 37.57, "true_lon": 126.98},
    {"num": 15, "region": "ASIA-PACIFIC", "city": "Jakarta", "summary": "EU governments clear tariff-cutting trade pact with Indonesia to offset US duties.", "true_lat": -6.21, "true_lon": 106.85},
    {"num": 16, "region": "ASIA-PACIFIC", "city": "New Delhi", "summary": "India imposes 162.5% Scotch duty as Modi meets Prince & Princess of Wales.", "true_lat": 28.61, "true_lon": 77.21},
    {"num": 17, "region": "ASIA-PACIFIC", "city": "Bengaluru", "summary": "Amazon pledges $7bn for renewable energy expansion across India by 2030.", "true_lat": 12.97, "true_lon": 77.59},
    {"num": 18, "region": "ASIA-PACIFIC", "city": "Tokyo", "summary": "India–Japan \"2+2\" ministers expand defense tech and maritime ties.", "true_lat": 35.68, "true_lon": 139.77},
    {"num": 19, "region": "ASIA-PACIFIC", "city": "Hong Kong", "summary": "Hang Seng drops over 1.5% past 23,000; Kospi dips nearly 1%.", "true_lat": 22.32, "true_lon": 114.17},
    {"num": 20, "region": "MIDDLE EAST", "city": "Hormuz", "summary": "UKMTO reports projectile strike on tanker engine room off Khasab; crew safe.", "true_lat": 26.20, "true_lon": 56.25},
    {"num": 21, "region": "MIDDLE EAST", "city": "Manama", "summary": "Bapco refinery resumes runs after attacks; Gulf urges US restraint.", "true_lat": 26.22, "true_lon": 50.59},
    {"num": 22, "region": "MIDDLE EAST", "city": "Baghdad", "summary": "Iraqi court sentences six French ISIL members to life imprisonment.", "true_lat": 33.31, "true_lon": 44.36},
    {"num": 23, "region": "MIDDLE EAST", "city": "Doha", "summary": "Expanded 48-team FIFA U-17 World Cup kicks off across Aspire Zone.", "true_lat": 25.29, "true_lon": 51.53},
    {"num": 24, "region": "EUROPE", "city": "Paris", "summary": "Justice minister concedes hard-left Mélenchon could win 2027 presidency.", "true_lat": 48.86, "true_lon": 2.35},
    {"num": 25, "region": "EUROPE", "city": "Frankfurt", "summary": "FT reports Deutsche Bank handled $582m in Epstein-linked accounts.", "true_lat": 50.11, "true_lon": 8.68},
    {"num": 26, "region": "EUROPE", "city": "Berlin", "summary": "Merz, Macron, Burnham & Rutte meet on Ukraine security guarantees.", "true_lat": 52.52, "true_lon": 13.40},
    {"num": 27, "region": "EUROPE", "city": "Tatarstan", "summary": "Ukrainian drones set Russia's Kaleykino oil pumping hub ablaze.", "true_lat": 54.90, "true_lon": 52.30},
    {"num": 28, "region": "EUROPE", "city": "Brussels", "summary": "EU deal delays oil-and-gas import methane rules by two years.", "true_lat": 50.85, "true_lon": 4.35},
    {"num": 29, "region": "EUROPE", "city": "London", "summary": "Final Bayesian report cites unassessed wind flaw in 2024 sinking.", "true_lat": 51.51, "true_lon": -0.13},
    {"num": 30, "region": "AFRICA", "city": "Kinshasa", "summary": "Africa CDC warns DR Congo Ebola outbreak has passed 5,500 deaths.", "true_lat": -4.32, "true_lon": 15.31},
    {"num": 31, "region": "AFRICA", "city": "Benghazi", "summary": "Officials display huge east Libya haul of cocaine and narcotic pills.", "true_lat": 32.12, "true_lon": 20.07},
    {"num": 32, "region": "AFRICA", "city": "Mogadishu", "summary": "Somalia accuses UAE of operating secret military bases on its soil.", "true_lat": 2.05, "true_lon": 45.32},
    {"num": 33, "region": "AFRICA", "city": "Nairobi", "summary": "Kenya floods kill six as Ruto gives fourth State of the Nation address.", "true_lat": -1.29, "true_lon": 36.82},
    {"num": 34, "region": "AMERICAS", "city": "Ottawa", "summary": "PM Carney says Canada rethinks China ties while seeking right US deal.", "true_lat": 45.42, "true_lon": -75.70},
    {"num": 35, "region": "AMERICAS", "city": "Caracas", "summary": "US details $12bn in Venezuelan oil revenue and signs bilateral security pact.", "true_lat": 10.48, "true_lon": -66.90},
    {"num": 36, "region": "AMERICAS", "city": "La Paz", "summary": "Bolivia declares national El Niño emergency; 78,000 families hit.", "true_lat": -16.50, "true_lon": -68.15},
    {"num": 37, "region": "AMERICAS", "city": "Washington", "summary": "Senators warn on AI cyber threats; Liu Yunping wins Dem Caucus post.", "true_lat": 38.91, "true_lon": -77.04},
    {"num": 38, "region": "AMERICAS", "city": "Sacramento", "summary": "Northern California braces for atmospheric river; flood watches out.", "true_lat": 38.58, "true_lon": -121.49},
    {"num": 39, "region": "AMERICAS", "city": "Mexico City", "summary": "Banxico publishes 3–2 split minutes on rate cut to 6.25%.", "true_lat": 19.43, "true_lon": -99.13},
    {"num": 40, "region": "GLOBAL & OCEANIA", "city": "Canberra", "summary": "Australia sanctions West Bank settlers, three people and four groups.", "true_lat": -35.28, "true_lon": 149.13},
    {"num": 41, "region": "GLOBAL & OCEANIA", "city": "Sydney", "summary": "Ben Duckett's 133 puts England in charge of third ODI vs Australia.", "true_lat": -42.88, "true_lon": 147.33},
    {"num": 42, "region": "GLOBAL & OCEANIA", "city": "Nukuʻalofa", "summary": "Tonga declares 27-day emergency over El Niño drought crisis.", "true_lat": -21.14, "true_lon": -175.20},
]

MAP_BOX = (28, 1512, 700, 1936)
MAP_VIEW = (42, 1540, 686, 1776)
MAP_LON_MIN, MAP_LON_MAX = -180.0, 180.0
MAP_LAT_MIN, MAP_LAT_MAX = -60.0, 82.0

KPI_ITEMS = (
    ("$81.3bn", "Anthropic record IPO ($83)", True),
    ("15.9m", "GTA VI pre-orders ($1.5bn)", False),
    ("$190.4m", "Record Van Gogh NY sale", True),
    ("200,000", "Evacuated for Cyclone Akvan", False),
    ("$120bn", "COP31 adaptation finance", False),
    ("730,000", "Rohingya in ICJ judgment", True),
)

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


def _draw_pill_badge(draw, x0: float, y0: float, text: str, font, bg: str, fg: str = "#FFFFFF", pad_x: int = 12, pad_y: int = 5) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    bw, bh = tw + pad_x * 2, th + pad_y * 2
    draw.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=8, fill=bg)
    _draw_centered_text(draw, x0 + bw / 2.0, y0 + bh / 2.0, text, font, fg)


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
    w, h = art_canvas.size
    for band_y, col in ((0, "#FAF0EC"), (32, "#F5E1DA"), (64, "#EED5CB")):
        draw.rectangle([0, band_y, w, band_y + 34], fill=col)
    for cx, cy, r in ((86, 40, 16), (106, 36, 18), (518, 38, 16), (538, 42, 14)):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#FDF8F6")
    draw.rectangle([0, 96, w, h], fill="#D6E4EC")
    draw.line([(0, 96), (w, 96)], fill="#94A3B8", width=2)
    for ry in (110, 124, 138):
        draw.line([(48, ry), (218, ry)], fill="#B0C4D4", width=2)
        draw.line([(406, ry), (576, ry)], fill="#B0C4D4", width=2)

    # Kylin Villa tiered pavilion roof silhouette
    draw.rectangle([206, 62, 418, 96], fill="#CBD5E1", outline="#64748B", width=2)
    for px in (224, 260, 296, 332, 368, 400):
        draw.rectangle([px - 4, 66, px + 4, 96], fill="#64748B")
    draw.polygon([(182, 64), (312, 36), (442, 64)], fill="#334155")
    draw.polygon([(224, 42), (312, 22), (400, 42)], fill="#1E293B")
    _draw_pill_badge(draw, w / 2.0 - 54, 10, "3 LEADERS", fonts.get("sans_bold", 16), "#991B1B")

    # Three leader silhouettes behind curved table
    for lx, col in ((170, "#1E293B"), (312, "#0F172A"), (454, "#334155")):
        draw.ellipse([lx - 18, 78, lx + 18, 114], fill=col)
        draw.pieslice([lx - 42, 114, lx + 42, 168], 180, 360, fill=col)

    # Curved diplomatic walnut table
    draw.pieslice([76, 128, w - 76, 250], 180, 360, fill="#78350F", outline="#451A03", width=3)
    draw.pieslice([126, 148, w - 126, 240], 180, 360, fill="#92400E")

    # Stylized miniature flags (US, China, Russia)
    fx, fy = 148, 110
    draw.line([(fx, fy), (fx, 145)], fill="#111827", width=3)
    draw.rectangle([fx + 2, fy, fx + 46, fy + 28], fill="#FFFFFF", outline="#475569", width=1)
    for sy in range(0, 28, 6):
        draw.rectangle([fx + 2, fy + sy, fx + 46, fy + sy + 3], fill="#B91C1C")
    draw.rectangle([fx + 2, fy, fx + 22, fy + 15], fill="#1D4ED8")

    fx, fy = 290, 104
    draw.line([(fx, fy), (fx, 140)], fill="#111827", width=3)
    draw.rectangle([fx + 2, fy, fx + 46, fy + 28], fill="#DC2626", outline="#991B1B", width=1)
    _draw_star(draw, fx + 12, fy + 10, 6, 2.5, 5, "#FACC15")

    fx, fy = 432, 110
    draw.line([(fx, fy), (fx, 145)], fill="#111827", width=3)
    draw.rectangle([fx + 2, fy, fx + 46, fy + 9], fill="#FFFFFF", outline="#64748B", width=1)
    draw.rectangle([fx + 2, fy + 9, fx + 46, fy + 19], fill="#1D4ED8")
    draw.rectangle([fx + 2, fy + 19, fx + 46, fy + 28], fill="#DC2626")

    draw.arc([278, 152, 346, 184], 190, 350, fill="#D97706", width=3)


def _draw_scene_2(art_canvas, draw, fonts: FontBank) -> None:
    """#2 Anthropic Record $81.3bn Nasdaq IPO: Manhattan tower, neural nodes, rising chart."""
    w, h = art_canvas.size
    draw.text((22, 14), "$81.3BN", font=fonts.get("sans_bold", 42), fill="#0F172A")

    skyline = [(28, 198, 72, 116, "#94A3B8"), (78, 198, 128, 86, "#64748B"), (214, 198, 258, 106, "#94A3B8")]
    for x0, y1, x1, y0, col in skyline:
        draw.rectangle([x0, y0, x1, y1], fill=col)
        for wy in range(y0 + 10, y1 - 8, 14):
            draw.line([(x0 + 6, wy), (x1 - 6, wy)], fill="#E2E8F0", width=2)

    for gy in (44, 82, 120, 158):
        draw.line([(332, gy), (596, gy)], fill="#CBDCEB", width=1)

    draw.rectangle([134, 62, 208, 198], fill="#1E3A8A", outline="#0F172A", width=2)
    draw.pieslice([134, 48, 208, 76], 180, 360, fill="#3B82F6", outline="#0F172A", width=2)
    for gy in (88, 114, 140, 166):
        draw.line([(136, gy), (206, gy)], fill="#60A5FA", width=2)
    for gx in (152, 171, 190):
        draw.line([(gx, 62), (gx, 198)], fill="#1D4ED8", width=2)

    nodes = [(252, 42), (288, 28), (316, 54), (274, 72), (308, 86)]
    for i, p1 in enumerate(nodes):
        for p2 in nodes[i + 1:]:
            draw.line([p1, p2], fill="#0F766E", width=2)
    for nx, ny in nodes:
        draw.ellipse([nx - 5, ny - 5, nx + 5, ny + 5], fill="#14B8A6", outline="#0F172A", width=1)

    bar_heights = [36, 52, 68, 88, 112, 138, 162]
    bx = 342
    for idx, bh in enumerate(bar_heights):
        col = "#0F766E" if idx < 5 else ("#059669" if idx == 5 else "#10B981")
        draw.rectangle([bx, h - bh, bx + 28, h], fill=col, outline="#064E3B", width=1)
        bx += 36
    draw.line([(336, 152), (464, 96), (576, 30)], fill="#B91C1C", width=5)
    draw.polygon([(588, 22), (562, 24), (578, 46)], fill="#B91C1C")


def _draw_scene_3(art_canvas, draw, fonts: FontBank) -> None:
    """#3 GTA VI Midnight Unlock on #0B1324: neon sunset, Vice City skyline, palms, gamepad."""
    w, h = art_canvas.size
    # Subtle stars in midnight sky
    for sx, sy in ((184, 24), (236, 16), (412, 22), (478, 34), (544, 18), (586, 44)):
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill="#E2E8F0")

    # Glowing pink/orange neon horizon bands & retro sun disc
    draw.rectangle([0, 108, w, 126], fill="#831843")
    draw.rectangle([0, 126, w, 144], fill="#BE185D")
    draw.rectangle([0, 144, w, h], fill="#1E1B4B")
    sun_cx, sun_cy, sr = 312, 112, 64
    draw.pieslice([sun_cx - sr, sun_cy - sr, sun_cx + sr, sun_cy + sr], 180, 360, fill="#F97316")
    draw.pieslice([sun_cx - sr, sun_cy - sr, sun_cx + sr, sun_cy + sr], 200, 340, fill="#FACC15")
    for sy in (78, 92, 106):
        draw.rectangle([sun_cx - sr, sy, sun_cx + sr, sy + 4], fill="#0B1324")

    # Vice City art-deco coastal skyline with neon window highlights
    buildings = [
        (164, 88, 202, 144, "#1E1B4B", "#EC4899"),
        (206, 62, 248, 144, "#312E81", "#38BDF8"),
        (252, 78, 286, 144, "#1E1B4B", "#FACC15"),
        (338, 72, 376, 144, "#312E81", "#EC4899"),
        (382, 54, 424, 144, "#1E1B4B", "#38BDF8"),
        (428, 92, 464, 144, "#312E81", "#F97316"),
    ]
    for x0, y0, x1, y1, bcol, wcol in buildings:
        draw.rectangle([x0, y0, x1, y1], fill=bcol)
        for wy in range(y0 + 10, y1 - 8, 12):
            draw.line([(x0 + 6, wy), (x1 - 6, wy)], fill=wcol, width=2)

    # Ocean neon reflections
    for ry, rcol in ((154, "#EC4899"), (168, "#F97316"), (182, "#38BDF8")):
        draw.line([(170, ry), (460, ry)], fill=rcol, width=2)

    # Tall palms flanking boulevard
    _draw_palm(draw, 54, 192, 114, 16, "#090D16")
    _draw_palm(draw, 118, 194, 88, -14, "#0F172A")
    _draw_palm(draw, 566, 192, 112, -16, "#090D16")
    _draw_palm(draw, 506, 194, 84, 14, "#0F172A")

    # Bold hero metric top-left
    draw.text((22, 12), "15.9M", font=fonts.get("sans_bold", 42), fill="#FDE047")

    # Sleek modern console gamepad foreground center-right
    gx, gy = 398, 146
    draw.rounded_rectangle([gx - 68, gy - 28, gx + 68, gy + 24], radius=24, fill="#0F172A", outline="#EC4899", width=3)
    draw.ellipse([gx - 78, gy - 6, gx - 34, gy + 40], fill="#0F172A", outline="#EC4899", width=2)
    draw.ellipse([gx + 34, gy - 6, gx + 78, gy + 40], fill="#0F172A", outline="#EC4899", width=2)
    draw.ellipse([gx - 42, gy - 10, gx - 20, gy + 12], fill="#38BDF8")
    for dx, dy, c in ((32, -12, "#EC4899"), (46, -2, "#FACC15"), (32, 8, "#38BDF8"), (18, -2, "#34D399")):
        draw.ellipse([gx + dx - 5, gy + dy - 5, gx + dx + 5, gy + dy + 5], fill=c)


def _draw_scene_4(art_canvas, draw, fonts: FontBank) -> None:
    """#4 ICJ Rohingya Verdict: Peace Palace, scales of justice, UN wreath."""
    w, h = art_canvas.size
    _draw_pill_badge(draw, w - 78, 10, "730K", fonts.get("sans_bold", 15), "#1E3A8A")

    draw.rectangle([20, 62, 176, h], fill="#B45309", outline="#78350F", width=2)
    draw.polygon([(14, 62), (98, 42), (182, 62)], fill="#334155")
    draw.rectangle([44, 22, 74, 62], fill="#9A3412", outline="#78350F", width=1)
    draw.polygon([(40, 22), (59, 6), (78, 22)], fill="#1E293B")
    for wx in (36, 72, 108, 144):
        draw.rectangle([wx, 76, wx + 18, 108], fill="#E2E8F0")

    cx, cy = 266, 68
    draw.ellipse([cx - 42, cy - 42, cx + 42, cy + 42], fill="#1D4ED8", outline="#93C5FD", width=3)
    draw.line([(cx, 26), (cx, 102)], fill="#FACC15", width=4)
    draw.line([(cx - 34, 42), (cx + 34, 42)], fill="#FACC15", width=4)
    for sx in (cx - 32, cx + 32):
        draw.line([(sx, 42), (sx - 12, 72)], fill="#FDE68A", width=2)
        draw.line([(sx, 42), (sx + 12, 72)], fill="#FDE68A", width=2)
        draw.chord([sx - 14, 66, sx + 14, 82], 0, 180, fill="#FACC15")
    draw.rectangle([cx - 22, 100, cx + 22, 108], fill="#78350F")


def _draw_scene_5(art_canvas, draw, fonts: FontBank) -> None:
    """#5 Cyclone Akvan Odisha: swirling storm vortex, coastline, alert & tents."""
    w, h = art_canvas.size
    draw.polygon([(0, 86), (170, 96), (220, h), (0, h)], fill="#F5D0A9")
    draw.polygon([(170, 96), (w, 72), (w, h), (220, h)], fill="#0284C7")

    cx, cy = 266, 56
    for r, col, sa in ((48, "#0F766E", 20), (36, "#1E293B", 80), (24, "#0F766E", 160)):
        draw.arc([cx - r, cy - r, cx + r, cy + r], sa, sa + 210, fill=col, width=6)
        draw.arc([cx - r, cy - r, cx + r, cy + r], sa + 180, sa + 350, fill=col, width=5)
    draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill="#B91C1C")

    _draw_palm(draw, 44, 114, 58, 22, "#166534")
    draw.polygon([(92, 56), (124, 56), (108, 26)], fill="#B91C1C")
    draw.line([(108, 34), (108, 46)], fill="#FEF08A", width=3)
    draw.ellipse([106, 49, 110, 53], fill="#FEF08A")
    for tx in (86, 134):
        draw.polygon([(tx, 114), (tx + 20, 88), (tx + 40, 114)], fill="#EA580C", outline="#9A3412", width=2)

    draw.rounded_rectangle([w - 86, h - 38, w - 10, h - 6], radius=6, fill="#FFFFFF")
    _draw_centered_text(draw, w - 48, h - 22, "200K", fonts.get("sans_bold", 21), "#0F172A")


def _draw_scene_6(art_canvas, draw, fonts: FontBank) -> None:
    """#6 Central Gaza Ceasefire Line: tanks crossing dashed yellow line & watchtower."""
    w, h = art_canvas.size
    _draw_pill_badge(draw, 14, 10, "RAID", fonts.get("sans_bold", 15), "#991B1B")

    # Desert horizon & berm
    draw.rectangle([0, 74, w, h], fill="#E7C8A0")
    draw.polygon([(0, 80), (94, 62), (168, 82), (0, 88)], fill="#D4AF7A")

    # Watchtower silhouette right-back
    draw.line([(312, 34), (304, 84)], fill="#475569", width=3)
    draw.line([(334, 34), (342, 84)], fill="#475569", width=3)
    draw.rectangle([304, 22, 342, 38], fill="#334155", outline="#1E293B", width=1)

    # Dashed yellow ceasefire line across mid-ground
    for dy in range(52, h - 4, 14):
        x_off = (dy - 52) * 0.55
        draw.line([(168 + x_off, dy), (176 + x_off, dy + 8)], fill="#EAB308", width=6)

    # Two armored tank silhouettes advancing across the yellow line
    for tx, ty, scale in ((78, 86, 0.85), (178, 92, 1.05)):
        tw, th = int(76 * scale), int(22 * scale)
        draw.rounded_rectangle([tx, ty, tx + tw, ty + th], radius=6, fill="#1E293B")
        for wx in range(tx + 8, tx + tw - 8, int(14 * scale)):
            draw.ellipse([wx, ty + th - int(10 * scale), wx + int(10 * scale), ty + th], fill="#475569")
        draw.polygon([
            (tx + int(10 * scale), ty),
            (tx + int(22 * scale), ty - int(16 * scale)),
            (tx + int(56 * scale), ty - int(16 * scale)),
            (tx + int(64 * scale), ty),
        ], fill="#334155", outline="#0F172A", width=1)
        draw.line([
            (tx + int(54 * scale), ty - int(10 * scale)),
            (tx + int(92 * scale), ty - int(12 * scale)),
        ], fill="#1E293B", width=max(3, int(4 * scale)))


def _draw_scene_7(art_canvas, draw, fonts: FontBank) -> None:
    """#7 Antalya COP31 Crunch Day: Mediterranean wave, balance scale of green vs fossil."""
    w, h = art_canvas.size
    _draw_pill_badge(draw, 14, 10, "$120BN", fonts.get("sans_bold", 15), "#065F46")
    draw.rectangle([0, 100, w, h], fill="#0284C7")
    draw.polygon([(20, 100), (62, 68), (104, 100)], fill="#FFFFFF", outline="#94A3B8", width=2)
    draw.polygon([(82, 100), (118, 74), (154, 100)], fill="#F1F5F9", outline="#94A3B8", width=2)

    cx = 252
    draw.line([(cx, 24), (cx, 114)], fill="#1E293B", width=4)
    draw.rectangle([cx - 28, 110, cx + 28, 118], fill="#1E293B")
    draw.line([(cx - 64, 38), (cx + 64, 28)], fill="#1E293B", width=4)

    lx, ly = cx - 64, 38
    draw.line([(lx, ly), (lx, 74)], fill="#64748B", width=2)
    draw.ellipse([lx - 20, 58, lx + 4, 82], fill="#059669")
    draw.line([(lx + 10, 76), (lx + 10, 48)], fill="#065F46", width=3)
    for b_deg in (0, 120, 240):
        ba = math.radians(b_deg)
        draw.line([(lx + 10, 48), (lx + 10 + 14 * math.cos(ba), 48 + 14 * math.sin(ba))], fill="#0F766E", width=3)

    rx, ry = cx + 64, 28
    draw.line([(rx, ry), (rx, 70)], fill="#64748B", width=2)
    draw.rectangle([rx - 14, 52, rx - 4, 72], fill="#475569")
    draw.ellipse([rx - 16, 36, rx + 2, 52], fill="#64748B")
    draw.rectangle([rx + 4, 54, rx + 24, 72], fill="#FEF3C7", outline="#B91C1C", width=2)


def _draw_scene_8(art_canvas, draw, fonts: FontBank) -> None:
    """#8 APEC 21-Economy Declaration: Pacific globe arcs & 21 radial economy nodes."""
    w, h = art_canvas.size
    _draw_pill_badge(draw, 14, 10, "21 STATES", fonts.get("sans_bold", 14), "#0F766E")

    # Pacific Ocean basin & trade arcs
    cx, cy = 228, 66
    draw.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], fill="#DCEBF7", outline="#0F766E", width=3)
    draw.arc([cx - 48, cy - 36, cx + 48, cy + 36], 180, 360, fill="#0284C7", width=2)
    draw.arc([cx - 48, cy - 20, cx + 48, cy + 50], 0, 180, fill="#D97706", width=2)
    draw.arc([cx - 26, cy - 50, cx + 26, cy + 50], 0, 360, fill="#94A3B8", width=1)

    # 21 distinct radial APEC economy nodes around outer emblem ring
    for i in range(21):
        ang = -math.pi / 2.0 + (2.0 * math.pi * i) / 21.0
        nx = cx + 46 * math.cos(ang)
        ny = cy + 46 * math.sin(ang)
        ix = cx + 20 * math.cos(ang)
        iy = cy + 20 * math.sin(ang)
        if i % 3 == 0:
            draw.line([(ix, iy), (nx, ny)], fill="#B45309", width=1)
        node_col = "#0F766E" if i % 2 == 0 else "#D97706"
        draw.ellipse([nx - 4, ny - 4, nx + 4, ny + 4], fill=node_col, outline="#FFFFFF", width=1)

    # Stylized Shenzhen bay container ship / trade bars left-bottom
    draw.polygon([(24, 108), (126, 108), (114, 122), (34, 122)], fill="#1E293B")
    for sx, scol in ((42, "#B91C1C"), (64, "#0F766E"), (86, "#D97706")):
        draw.rectangle([sx, 94, sx + 18, 108], fill=scol, outline="#FFFFFF", width=1)


def _draw_scene_9(art_canvas, draw, fonts: FontBank) -> None:
    """#9 Riyadh Dawn Missile Intercept & All-Clear: Kingdom Centre, Patriot arc, 04:42."""
    w, h = art_canvas.size
    _draw_pill_badge(draw, 14, 10, "04:42", fonts.get("sans_bold", 15), "#0F766E")
    draw.rectangle([0, 92, w, h], fill="#FDE68A")
    draw.rectangle([0, 108, w, h], fill="#FDBA74")

    # Scaled Riyadh skyline: Faisaliah spire + Kingdom Centre notch
    draw.rectangle([28, 92, 54, h], fill="#475569")
    draw.polygon([(66, h), (84, 46), (102, h)], fill="#334155")
    draw.ellipse([79, 56, 89, 66], fill="#F59E0B")
    draw.polygon([(142, h), (150, 28), (194, 28), (202, h)], fill="#1E293B")
    draw.chord([156, 32, 188, 68], 0, 180, fill="#F5E1DA")
    draw.rectangle([222, 86, 254, h], fill="#475569")

    # Incoming dotted crimson arc + teal Patriot interceptor arc & burst
    for i in range(7):
        t = i / 6.0
        px = 26 + t * 244
        py = 104 - math.sin(t * math.pi * 0.56) * 70
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill="#B91C1C")
    draw.line([(326, 114), (272, 38)], fill="#0F766E", width=4)
    ix, iy = 270, 38
    draw.ellipse([ix - 24, iy - 24, ix + 24, iy + 24], outline="#D97706", width=2)
    _draw_star(draw, ix, iy, 16, 7, 8, "#F59E0B", "#B91C1C")
    _draw_star(draw, ix, iy, 8, 3.5, 6, "#FEF3C7")


def _draw_scene_10(art_canvas, draw, fonts: FontBank) -> None:
    """#10 Australia 4.9% Jobless: Sydney Opera House shells + rising crimson bar spike."""
    w, h = art_canvas.size
    draw.rectangle([0, 102, w, h], fill="#0284C7")
    draw.rectangle([16, 94, 166, 104], fill="#CBD5E1")

    for sx0, sx1, sy0 in ((24, 72, 40), (58, 108, 30), (94, 138, 48), (124, 158, 62)):
        draw.polygon([(sx0, 94), (sx0 + 12, sy0), (sx1, 94)], fill="#FFFFFF", outline="#64748B", width=2)

    draw.text((180, 10), "4.9%", font=fonts.get("sans_bold", 30), fill="#B91C1C")
    bars = [(194, 28, "#475569"), (224, 36, "#475569"), (254, 44, "#64748B"), (284, 58, "#DC2626"), (314, 78, "#B91C1C")]
    for bx, bh, col in bars:
        draw.rectangle([bx, 114 - bh, bx + 22, 114], fill=col)
    draw.line([(194, 80), (258, 64), (294, 48), (325, 28)], fill="#B91C1C", width=4)
    draw.polygon([(334, 22), (316, 24), (326, 38)], fill="#B91C1C")


def _draw_scene_11(art_canvas, draw, fonts: FontBank) -> None:
    """#11 Van Gogh Record $190.4m Auction: ornate frame, chestnut blossoms, auction gavel."""
    w, h = art_canvas.size
    _draw_pill_badge(draw, w - 102, 10, "$190.4M", fonts.get("sans_bold", 15), "#991B1B")

    # Ornate gold/bronze picture frame
    draw.rectangle([20, 10, 186, 114], fill="#B45309", outline="#78350F", width=3)
    draw.rectangle([26, 16, 180, 108], fill="#F59E0B", outline="#92400E", width=1)
    # Impasto sky & green hillside inside canvas
    draw.rectangle([32, 22, 174, 72], fill="#2563EB")
    for sy, scol in ((28, "#60A5FA"), (38, "#3B82F6"), (48, "#93C5FD")):
        draw.arc([34, sy, 124, sy + 24], 180, 350, fill=scol, width=4)
        draw.arc([104, sy - 4, 174, sy + 20], 190, 350, fill=scol, width=4)
    draw.polygon([(32, 102), (32, 74), (98, 66), (174, 76), (174, 102)], fill="#65A30D")
    draw.polygon([(32, 102), (32, 86), (112, 80), (174, 88), (174, 102)], fill="#15803D")

    # Chestnut tree trunk & blooming brushwork canopy
    draw.rectangle([95, 58, 109, 96], fill="#78350F")
    draw.line([(102, 66), (82, 52)], fill="#78350F", width=4)
    draw.line([(102, 64), (122, 50)], fill="#78350F", width=4)
    for cx, cy, r, col in (
        (82, 48, 18, "#15803D"), (102, 38, 20, "#16A34A"), (124, 48, 18, "#15803D"),
        (72, 44, 9, "#FEF9C3"), (96, 32, 10, "#FEF08A"), (118, 38, 9, "#FEF9C3"),
        (134, 48, 8, "#FACC15"), (88, 50, 7, "#FACC15"), (108, 48, 8, "#FEF08A"),
    ):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

    # Auction podium, sound block & gavel right
    draw.rectangle([226, 86, 336, 98], fill="#78350F", outline="#451A03", width=1)
    draw.rectangle([238, 98, 324, h], fill="#92400E")
    draw.rectangle([244, 76, 286, 86], fill="#D97706", outline="#78350F", width=1)
    draw.line([(268, 62), (326, 44)], fill="#78350F", width=5)
    draw.rounded_rectangle([252, 48, 282, 70], radius=4, fill="#451A03", outline="#F59E0B", width=1)


def _draw_scene_12(art_canvas, draw, fonts: FontBank) -> None:
    """#12 Kerch Bridge Struck: twin-chord arch bridge, blast plume, roadblock."""
    w, h = art_canvas.size
    _draw_pill_badge(draw, 12, 10, "3RD HIT", fonts.get("sans_bold", 14), "#991B1B")
    draw.rectangle([0, 92, w, h], fill="#0369A1")
    for wx in (20, 120, 230, 300):
        draw.line([(wx, 108), (wx + 40, 108)], fill="#7DD3FC", width=2)

    for px in (72, 148, 224, 300):
        draw.rectangle([px - 6, 74, px + 6, 112], fill="#64748B")
    draw.arc([138, 28, 234, 116], 180, 360, fill="#64748B", width=6)
    draw.arc([142, 34, 230, 116], 180, 360, fill="#334155", width=3)
    draw.rectangle([0, 72, w, 82], fill="#334155")

    draw.ellipse([162, 16, 206, 54], fill="#475569")
    _draw_star(draw, 186, 58, 22, 9, 8, "#B91C1C")
    _draw_star(draw, 186, 60, 12, 5, 6, "#F59E0B")

    draw.rectangle([14, 62, 22, 82], fill="#1E293B")
    for bx in range(22, 82, 12):
        col = "#DC2626" if (bx // 12) % 2 == 0 else "#FFFFFF"
        draw.rectangle([bx, 60, bx + 12, 68], fill=col)


def _draw_scene_13(art_canvas, draw, fonts: FontBank) -> None:
    """#13 South Florida School Floods: storm cloud, rain, yellow school bus in floodwater."""
    w, h = art_canvas.size
    draw.text((w - 86, 10), "17 IN", font=fonts.get("sans_bold", 26), fill="#1E3A8A")

    # Storm cloud & rain streaks
    for cx, cy, r in ((48, 32, 22), (78, 24, 26), (112, 30, 22), (138, 36, 18)):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#475569")
    for rx in range(26, 160, 18):
        draw.line([(rx, 54), (rx - 10, 82)], fill="#2563EB", width=3)

    _draw_palm(draw, 34, 102, 48, -10, "#166534")
    draw.rectangle([0, 96, w, h], fill="#0284C7")

    # Classic yellow school bus splashing through floodwater
    bx, by = 114, 54
    draw.rounded_rectangle([bx, by, bx + 148, by + 48], radius=8, fill="#EAB308", outline="#92400E", width=2)
    draw.rectangle([bx + 122, by + 10, bx + 146, by + 28], fill="#1E293B")
    for wx in range(bx + 12, bx + 114, 24):
        draw.rectangle([wx, by + 10, wx + 18, by + 26], fill="#1E293B")
    for whx in (bx + 30, bx + 118):
        draw.ellipse([whx - 12, by + 38, whx + 12, by + 62], fill="#111827")
    draw.arc([bx + 132, 86, bx + 174, 114], 180, 340, fill="#E0F2FE", width=4)
    for wx in (20, 96, 188, 278):
        draw.line([(wx, 112), (wx + 44, 112)], fill="#7DD3FC", width=3)


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
    kicker_font = fonts.get("sans_bold", 22)
    draw.text((x0, 14), "THE DAY IN WORLD NEWS", font=kicker_font, fill=PALETTE["crimson"])

    right_tag = "42 STORIES · 6 REGIONS · ONE DAY"
    rw = kicker_font.getlength(right_tag)
    draw.text((x1 - rw, 14), right_tag, font=kicker_font, fill=PALETTE["sub_ink"])

    draw.line([(x0, 46), (x1, 46)], fill=PALETTE["ink"], width=3)

    title = "Thursday 19 November 2026"
    title_font = fonts.get("serif_bold", 104)
    tb = draw.textbbox((0, 0), title, font=title_font)
    tw = tb[2] - tb[0]
    draw.text(((CANVAS_W - tw) / 2.0 - tb[0], 54 - tb[1]), title, font=title_font, fill=PALETTE["ink"])

    deck_font = fonts.get("serif_italic", 19)
    _draw_centered_text(draw, CANVAS_W / 2.0, 178, MASTHEAD_DECK, deck_font, PALETTE["crimson"])
    draw.line([(x0, 198), (x1, 198)], fill=PALETTE["rule"], width=2)

    total = sum(REGION_COUNTS.values()) or 1
    ry0, ry1 = 206, 238
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


def _draw_card(canvas, draw, fonts: FontBank, story: dict, box: tuple[int, int, int, int], is_lead: bool) -> None:
    x0, y0, x1, y1 = box
    region = story["region"]
    reg_color = REGION_COLORS[region]

    draw.rectangle([x0, y0, x1, y1], fill=PALETTE["card_bg"], outline=PALETTE["rule"], width=2)
    draw.rectangle([x0, y0, x1, y0 + 5], fill=reg_color)

    pad = 14 if is_lead else 12
    art_x = x0 + pad
    art_y = y0 + (14 if is_lead else 12)
    art_w = (x1 - x0) - 2 * pad
    art_h = 230 if is_lead else 160
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
    cap_font = fonts.get("sans_bold", 17 if is_lead else 15)
    _draw_centered_text(draw, art_x + art_w / 2.0, (cap_y0 + cap_y1) / 2.0, story["caption"], cap_font, "#FFFFFF")
    draw.rectangle([art_x, art_y, art_x + art_w, cap_y1], outline=PALETTE["rule"], width=1)

    meta_y = cap_y1 + (10 if is_lead else 8)
    badge_r = 14 if is_lead else 13
    bx, by = art_x + badge_r, meta_y + badge_r
    draw.ellipse([bx - badge_r, by - badge_r, bx + badge_r, by + badge_r], fill=reg_color)
    badge_font = fonts.get("sans_bold", 16 if is_lead else 15)
    _draw_centered_text(draw, bx, by, str(story["num"]), badge_font, "#FFFFFF")

    kicker_font = fonts.get("sans_condensed_bold", 18 if is_lead else 15)
    agency_font = fonts.get("sans_condensed_bold", 17 if is_lead else 14)
    kicker = f"{region} · {story['beat']}"
    agency = story["agency"]
    aw = agency_font.getlength(agency)
    kx = bx + badge_r + 8
    max_kw = (art_x + art_w - aw - 10) - kx
    if kicker_font.getlength(kicker) > max_kw:
        short_reg = region.replace("GLOBAL & OCEANIA", "GLOBAL")
        kicker = f"{short_reg} · {story['beat']}"
    draw.text((kx, meta_y + (3 if is_lead else 4)), kicker, font=kicker_font, fill=reg_color)
    draw.text((art_x + art_w - aw, meta_y + (4 if is_lead else 5)), agency, font=agency_font, fill=PALETTE["muted"])

    hl_y = meta_y + badge_r * 2 + (8 if is_lead else 6)
    hl_size = 40 if is_lead else 32
    hl_font = fonts.get("serif_bold", hl_size)
    hl_lines = _wrap_text(story["headline"], hl_font, art_w, 2)
    hl_step = 44 if is_lead else 36
    for idx, line in enumerate(hl_lines):
        draw.text((art_x, hl_y + idx * hl_step), line, font=hl_font, fill=PALETTE["ink"])

    sub_y = hl_y + max(len(hl_lines), 1) * hl_step + (6 if is_lead else 5)
    sub_size = 22 if is_lead else 21
    sub_role = "sans_regular" if is_lead else "sans_condensed_regular"
    sub_font = fonts.get(sub_role, sub_size)
    sub_lines = _wrap_text(story["subdeck"], sub_font, art_w, 2)
    sub_step = 27 if is_lead else 25
    for idx, line in enumerate(sub_lines):
        if sub_y + idx * sub_step + sub_size <= y1 - 8:
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

    leg_font = fonts.get("sans_condensed_bold", 13)
    leg_y0 = vy1 + 4
    col_w = 215
    for idx, region in enumerate(REGION_ORDER):
        col_i = idx % 3
        row_i = idx // 3
        lx = vx0 + col_i * col_w
        ly = leg_y0 + row_i * 16
        draw.rectangle([lx, ly + 2, lx + 11, ly + 13], fill=REGION_COLORS[region])
        label = f"{region} ({REGION_COUNTS[region]})"
        draw.text((lx + 16, ly), label, font=leg_font, fill=PALETTE["sub_ink"])

    cap_y = leg_y0 + 34
    cap_font = fonts.get("sans_regular", 12)
    draw.ellipse([vx0, cap_y + 1, vx0 + 12, cap_y + 13], fill=PALETTE["crimson"])
    _draw_centered_text(draw, vx0 + 6, cap_y + 7, "1", fonts.get("sans_bold", 9), "#FFFFFF")
    part1 = "pin: stories 1–13 · "
    draw.text((vx0 + 16, cap_y), part1, font=cap_font, fill=PALETTE["muted"])
    dot_x = vx0 + 16 + cap_font.getlength(part1) + 4
    draw.ellipse([dot_x - 3.5, cap_y + 4, dot_x + 3.5, cap_y + 11], fill=PALETTE["muted"])
    part2 = "dot: briefs 14–42 · Hairlines lead to true place."
    draw.text((dot_x + 8, cap_y), part2, font=cap_font, fill=PALETTE["muted"])

    # Under-map 3x2 Big-Number KPI Callout Block (y=1827..1932)
    kpi_y0 = 1827
    draw.line([(vx0, kpi_y0), (vx1, kpi_y0)], fill=PALETTE["rule"], width=2)
    draw.text((vx0, kpi_y0 + 3), "THE DAY IN NUMBERS", font=fonts.get("sans_bold", 12), fill=PALETTE["crimson"])

    grid_y0 = kpi_y0 + 19
    cell_w = (vx1 - vx0) / 3.0
    cell_h = 43
    val_font = fonts.get("serif_bold", 22)
    lbl_font = fonts.get("sans_condensed_regular", 14)

    draw.line([(vx0, grid_y0 + cell_h), (vx1, grid_y0 + cell_h)], fill=PALETTE["rule_light"], width=1)
    for col_sep in (1, 2):
        sx = int(round(vx0 + col_sep * cell_w))
        draw.line([(sx, grid_y0 + 2), (sx, grid_y0 + cell_h * 2 - 2)], fill=PALETTE["rule_light"], width=1)

    for idx, (val, desc, accent) in enumerate(KPI_ITEMS):
        col_i = idx % 3
        row_i = idx // 3
        cx = vx0 + col_i * cell_w + (6 if col_i > 0 else 0)
        cy = grid_y0 + row_i * cell_h + 2
        val_col = PALETTE["crimson"] if accent else PALETTE["ink"]
        draw.text((cx, cy), val, font=val_font, fill=val_col)
        draw.text((cx, cy + 23), desc, font=lbl_font, fill=PALETTE["sub_ink"])


def _draw_briefs_panel(draw, fonts: FontBank) -> None:
    bx0, by0, bx1, by1 = 720, 1512, 2020, 1936
    header_font = fonts.get("sans_bold", 20)
    header = "ALSO ON THURSDAY 19 NOVEMBER — 29 MORE VERIFIED STORIES (#14–#42)"
    draw.text((bx0, by0 + 2), header, font=header_font, fill=PALETTE["ink"])
    draw.line([(bx0, by0 + 30), (bx1, by0 + 30)], fill=PALETTE["ink"], width=2)

    col_w = 638
    gutter = 24
    start_y = by0 + 40
    row_h = 25
    badge_font = fonts.get("sans_bold", 13)
    city_font = fonts.get("sans_bold", 16)
    body_font = fonts.get("sans_regular", 16)

    for idx, story in enumerate(BRIEF_STORIES):
        col = 0 if idx < 15 else 1
        row = idx if idx < 15 else idx - 15
        rx = bx0 + col * (col_w + gutter)
        ry = start_y + row * row_h
        col_hex = REGION_COLORS[story["region"]]

        draw.rectangle([rx, ry + 2, rx + 22, ry + 22], fill=col_hex)
        _draw_centered_text(draw, rx + 11, ry + 12, str(story["num"]), badge_font, "#FFFFFF")

        city_prefix = f"{story['city']}: "
        tx = rx + 28
        draw.text((tx, ry + 3), city_prefix, font=city_font, fill=PALETTE["ink"])
        cx = tx + city_font.getlength(city_prefix)
        draw.text((cx, ry + 3), story["summary"], font=body_font, fill=PALETTE["sub_ink"])


def _draw_date_check(draw, fonts: FontBank) -> None:
    dx0, dy0, dx1, dy1 = 28, 1945, 2020, 2009
    draw.rectangle([dx0, dy0, dx1, dy1], fill=PALETTE["date_bg"], outline="#F0C6BA", width=1)
    draw.rectangle([dx0, dy0, dx0 + 6, dy1], fill=PALETTE["crimson"])

    bold_font = fonts.get("sans_bold", 14)
    reg_font = fonts.get("sans_regular", 14)

    lbl1 = "DATE CHECK — Verified Thu 19 Nov UTC: "
    draw.text((dx0 + 18, dy0 + 10), lbl1, font=bold_font, fill=PALETTE["crimson"])
    draw.text((dx0 + 18 + bold_font.getlength(lbl1), dy0 + 10), DATE_CHECK_UTC, font=reg_font, fill=PALETTE["ink"])

    lbl2 = "Left out on purpose as Wed 18 Nov / earlier news: "
    draw.text((dx0 + 18, dy0 + 36), lbl2, font=bold_font, fill=PALETTE["sub_ink"])
    draw.text((dx0 + 18 + bold_font.getlength(lbl2), dy0 + 36), DATE_CHECK_EXCLUDED, font=reg_font, fill=PALETTE["sub_ink"])


def _draw_footer(draw, fonts: FontBank) -> None:
    foot_font = fonts.get("sans_semibold", 15)
    draw.text((28, 2020), FOOTER_TEXT, font=foot_font, fill=PALETTE["muted"])


def _draw_broadsheet(canvas, draw, fonts: FontBank) -> None:
    _draw_masthead(draw, fonts)

    r1_w = 652
    r1_gap = 18
    for idx in range(3):
        cx0 = 28 + idx * (r1_w + r1_gap)
        _draw_card(canvas, draw, fonts, LEAD_STORIES[idx], (cx0, 250, cx0 + r1_w, 700), is_lead=True)

    r23_w = 388
    r23_gap = 13
    for row_idx, (ry0, ry1, offset) in enumerate(((714, 1100, 3), (1114, 1500, 8))):
        _ = row_idx
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
