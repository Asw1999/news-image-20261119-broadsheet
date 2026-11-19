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
    "MIDDLE EAST": 5,
    "EUROPE": 9,
    "AFRICA": 6,
    "AMERICAS": 7,
    "GLOBAL & OCEANIA": 6,
}

MASTHEAD_DECK = (
    "Trump, Xi & Putin hold historic Shenzhen talks · Anthropic prices $81.3bn IPO · "
    "Riyadh intercepts missile · ICJ Rohingya judgment day · GTA VI drops"
)
DATE_CHECK_UTC = (
    "ABS AU jobs 00:30 UTC · Riyadh alert 01:42 UTC · "
    "Suneung halt 04:05–04:40 UTC · ICJ sitting 09:00 UTC."
)
DATE_CHECK_EXCLUDED = (
    "Van Gogh NY $190.4m (18 Nov), Voyager 1 light-day (18 Nov), EU €45bn loan (18 Nov), "
    "Jeffries 251–11 vote (18 Nov), Hobart ODI (18 Nov), Carney–Xi (17 Nov), Nature study (4 Nov)."
)
FOOTER_TEXT = (
    "Claims by warring sides are attributed. Original drawings. Every story happened or was first reported "
    "Thursday 19 November 2026. Sources: Reuters, AP, AFP, Al Jazeera, Guardian, Xinhua, UN/ICJ, UNFCCC, ABS."
)

LEAD_STORIES = [
    {
        "num": 1,
        "region": "ASIA-PACIFIC",
        "beat": "SUMMIT",
        "city": "SHENZHEN",
        "agency": "REUTERS / AP",
        "headline": "Trump, Xi and Putin Hold Historic Shenzhen Summit",
        "subdeck": (
            "First US–China–Russia leaders' trilateral meets on APEC sidelines; "
            "nuclear stability, Ukraine and Iran top agenda."
        ),
        "caption": "SHENZHEN · HISTORIC TRILATERAL SUMMIT",
        "pastel": "cream",
        "true_lat": 22.54,
        "true_lon": 114.06,
        "pin_lat": 17.50,
        "pin_lon": 110.50,
    },
    {
        "num": 2,
        "region": "AMERICAS",
        "beat": "MARKETS",
        "city": "NEW YORK",
        "agency": "REUTERS / AL JAZEERA",
        "headline": "Anthropic Prices Record $81.3bn Nasdaq IPO",
        "subdeck": (
            "AI firm sells 980m shares at $83 (~$1.5tn valuation) ahead of "
            "Thursday ANT debut, topping SpaceX's record."
        ),
        "caption": "NEW YORK · RECORD AI IPO DEBUT",
        "pastel": "sky",
        "true_lat": 40.71,
        "true_lon": -74.01,
        "pin_lat": 41.50,
        "pin_lon": -72.00,
    },
    {
        "num": 3,
        "region": "MIDDLE EAST",
        "beat": "SECURITY",
        "city": "RIYADH",
        "agency": "AFP / MEE",
        "headline": "Blast Shakes Riyadh as Defences Intercept Missile",
        "subdeck": (
            "Civil Defense issues 04:42 alert before coalition intercepts Houthi "
            "missile over capital; debris causes minor damage."
        ),
        "caption": "RIYADH · DAWN MISSILE INTERCEPT",
        "pastel": "blush",
        "true_lat": 24.71,
        "true_lon": 46.68,
        "pin_lat": 19.50,
        "pin_lon": 53.50,
    },
    {
        "num": 4,
        "region": "EUROPE",
        "beat": "JUSTICE",
        "city": "THE HAGUE",
        "agency": "UN / ICJ",
        "headline": "ICJ Sits for Rohingya Genocide Verdict",
        "subdeck": (
            "UN court holds 10:00 CET sitting in The Gambia's landmark "
            "case vs Myanmar."
        ),
        "caption": "THE HAGUE · GENOCIDE CASE VERDICT DAY",
        "pastel": "slate",
        "true_lat": 52.08,
        "true_lon": 4.30,
        "pin_lat": 56.50,
        "pin_lon": -9.50,
    },
    {
        "num": 5,
        "region": "ASIA-PACIFIC",
        "beat": "CYCLONE",
        "city": "ODISHA",
        "agency": "PTI / THE HINDU",
        "headline": "Cyclone Akvan Forces 50k Off Odisha Coast",
        "subdeck": (
            "11 districts on red alert; schools shut Thu–Sat ahead of "
            "Friday landfall."
        ),
        "caption": "ODISHA · CYCLONE AKVAN EVACUATIONS",
        "pastel": "sky",
        "true_lat": 19.81,
        "true_lon": 85.83,
        "pin_lat": 18.00,
        "pin_lon": 83.00,
    },
    {
        "num": 6,
        "region": "EUROPE",
        "beat": "DIPLOMACY",
        "city": "BERLIN",
        "agency": "NATO / UKRINFORM",
        "headline": "Allies Meet in Berlin on Ukraine Security",
        "subdeck": (
            "Merz, Macron, Burnham, Rutte & US envoys meet on Ukraine "
            "security pact."
        ),
        "caption": "BERLIN · COALITION OF THE WILLING",
        "pastel": "slate",
        "true_lat": 52.52,
        "true_lon": 13.40,
        "pin_lat": 64.50,
        "pin_lon": 15.50,
    },
    {
        "num": 7,
        "region": "MIDDLE EAST",
        "beat": "CLIMATE",
        "city": "ANTALYA",
        "agency": "UNFCCC / GUARDIAN",
        "headline": "COP31 Enters Crunch Aid & Draft Talks",
        "subdeck": (
            "Ministers narrow 18-page fossil and aid text as Germany "
            "starts SF6 Pledge."
        ),
        "caption": "ANTALYA · COP31 PENULTIMATE DAY",
        "pastel": "sage",
        "true_lat": 36.89,
        "true_lon": 30.71,
        "pin_lat": 34.00,
        "pin_lon": 21.00,
    },
    {
        "num": 8,
        "region": "GLOBAL & OCEANIA",
        "beat": "CULTURE",
        "city": "AUCKLAND",
        "agency": "AFP / BERNAMA",
        "headline": "Grand Theft Auto VI Launches at Midnight",
        "subdeck": (
            "NZ and Australia lead PS5 & Xbox rollout, ending 13-year wait "
            "since GTA V."
        ),
        "caption": "GLOBAL · GTA VI RELEASE DAY",
        "pastel": "blush",
        "true_lat": -36.85,
        "true_lon": 174.76,
        "pin_lat": -42.00,
        "pin_lon": 171.00,
    },
    {
        "num": 9,
        "region": "AFRICA",
        "beat": "CONFLICT",
        "city": "AFRICA",
        "agency": "RELIEFWEB",
        "headline": "44% of War-Zone Kids Live in Africa",
        "subdeck": (
            "Save the Children logs 260m African children near conflict "
            "of 589m globally."
        ),
        "caption": "AFRICA · CHILDREN IN CONFLICT REPORT",
        "pastel": "cream",
        "true_lat": 5.00,
        "true_lon": 21.00,
        "pin_lat": 2.50,
        "pin_lon": 21.50,
    },
    {
        "num": 10,
        "region": "GLOBAL & OCEANIA",
        "beat": "ECONOMY",
        "city": "SYDNEY",
        "agency": "ABS / GUARDIAN",
        "headline": "Australian Jobless Jumps to 4.9%",
        "subdeck": (
            "ABS reports 43,500 Oct jobs shed, highest rate since 2021, "
            "cooling hike bets."
        ),
        "caption": "AUSTRALIA · UNEMPLOYMENT JUMPS",
        "pastel": "sky",
        "true_lat": -33.87,
        "true_lon": 151.21,
        "pin_lat": -30.50,
        "pin_lon": 140.50,
    },
    {
        "num": 11,
        "region": "ASIA-PACIFIC",
        "beat": "SOCIETY",
        "city": "SEOUL",
        "agency": "KOREA HERALD",
        "headline": "Korea Grounds Flights for Suneung Exam",
        "subdeck": (
            "Over 550k sit college test amid 35-min airspace halt and "
            "Wi-Fi jamming."
        ),
        "caption": "SEOUL · SUNEUNG EXAM FLIGHT HALT",
        "pastel": "slate",
        "true_lat": 37.57,
        "true_lon": 126.98,
        "pin_lat": 41.50,
        "pin_lon": 134.50,
    },
    {
        "num": 12,
        "region": "EUROPE",
        "beat": "WAR",
        "city": "CRIMEA",
        "agency": "GUARDIAN / AA",
        "headline": "Third Strike in Week Halts Kerch Bridge",
        "subdeck": (
            "Russian-installed Crimea governor halts traffic Thu for "
            "bridge inspections."
        ),
        "caption": "CRIMEA · KERCH BRIDGE STRUCK AGAIN",
        "pastel": "blush",
        "true_lat": 45.30,
        "true_lon": 36.51,
        "pin_lat": 50.00,
        "pin_lon": 44.50,
    },
    {
        "num": 13,
        "region": "AMERICAS",
        "beat": "WEATHER",
        "city": "MIAMI",
        "agency": "CBS MIAMI",
        "headline": "South Florida Floods Shut Major Schools",
        "subdeck": (
            "Up to 17 inches of rain swamps streets, closing Broward and "
            "Miami schools."
        ),
        "caption": "SOUTH FLORIDA · SCHOOL FLOODS",
        "pastel": "sky",
        "true_lat": 25.76,
        "true_lon": -80.19,
        "pin_lat": 19.00,
        "pin_lon": -84.00,
    },
]

BRIEF_STORIES = [
    {"num": 14, "region": "ASIA-PACIFIC", "city": "Kumamoto", "summary": "M5.7 quake shakes Kyushu, halting bullet trains; no tsunami.", "true_lat": 32.20, "true_lon": 130.50},
    {"num": 15, "region": "ASIA-PACIFIC", "city": "Taiyuan", "summary": "Long March-2D launches Shijian-24 satellite in 678th flight.", "true_lat": 38.85, "true_lon": 111.60},
    {"num": 16, "region": "ASIA-PACIFIC", "city": "Dhaka", "summary": "Paramilitary troops patrol Bangladesh amid Awami League lockdown.", "true_lat": 23.81, "true_lon": 90.41},
    {"num": 17, "region": "ASIA-PACIFIC", "city": "Tokyo", "summary": "India–Japan \"2+2\" ministers expand defense tech and maritime ties.", "true_lat": 35.68, "true_lon": 139.77},
    {"num": 18, "region": "ASIA-PACIFIC", "city": "Bangkok", "summary": "Farm ministry reviews US pork access safeguards to shield growers.", "true_lat": 13.76, "true_lon": 100.50},
    {"num": 19, "region": "ASIA-PACIFIC", "city": "Hong Kong", "summary": "Hang Seng falls over 1.5% past 23,000; Kospi dips nearly 1%.", "true_lat": 22.32, "true_lon": 114.17},
    {"num": 20, "region": "MIDDLE EAST", "city": "Sanaa", "summary": "Saudi-led coalition strikes Houthi sites after Riyadh missile alert.", "true_lat": 15.37, "true_lon": 44.19},
    {"num": 21, "region": "MIDDLE EAST", "city": "Dead Sea", "summary": "Jordan–EU summit showcases $15bn projects backed by €3bn EU aid.", "true_lat": 31.72, "true_lon": 35.58},
    {"num": 22, "region": "MIDDLE EAST", "city": "Doha", "summary": "Expanded 48-team FIFA U-17 World Cup kicks off across Aspire Zone.", "true_lat": 25.29, "true_lon": 51.53},
    {"num": 23, "region": "EUROPE", "city": "Tatarstan", "summary": "Ukrainian drones set Russia's Kaleykino oil pumping hub ablaze.", "true_lat": 54.90, "true_lon": 52.30},
    {"num": 24, "region": "EUROPE", "city": "Brussels", "summary": "EU deal delays oil-and-gas import methane rules by two years.", "true_lat": 50.85, "true_lon": 4.35},
    {"num": 25, "region": "EUROPE", "city": "London", "summary": "Final Bayesian report cites unassessed wind flaw in 2024 sinking.", "true_lat": 51.51, "true_lon": -0.13},
    {"num": 26, "region": "EUROPE", "city": "Helsinki", "summary": "Nokia, Nscale and Telia form Nordic–Baltic AI Gigafactory team.", "true_lat": 60.17, "true_lon": 24.94},
    {"num": 27, "region": "EUROPE", "city": "Vienna", "summary": "OSCE Chair Cassis calls special talks on 2027 chair deadlock.", "true_lat": 48.21, "true_lon": 16.37},
    {"num": 28, "region": "EUROPE", "city": "Madrid", "summary": "Spain enforces decree mandating pay bands, banning pay queries.", "true_lat": 40.42, "true_lon": -3.70},
    {"num": 29, "region": "AFRICA", "city": "Nairobi", "summary": "Drought cuts Kenya dairy output, deepening urban milk shortage.", "true_lat": -1.29, "true_lon": 36.82},
    {"num": 30, "region": "AFRICA", "city": "Abuja", "summary": "Senate clears state-police amendment with governor-abuse safeguards.", "true_lat": 9.08, "true_lon": 7.40},
    {"num": 31, "region": "AFRICA", "city": "Johannesburg", "summary": "Deputy Pres Mashatile faces MPs, keynotes AABLA gala.", "true_lat": -26.20, "true_lon": 28.05},
    {"num": 32, "region": "AFRICA", "city": "Accra", "summary": "Pres Mahama urges visa-free African travel at migration forum.", "true_lat": 5.60, "true_lon": -0.19},
    {"num": 33, "region": "AFRICA", "city": "Lilongwe", "summary": "Sovereign Metals installs Tim Carstens as chair for Kasiya mine.", "true_lat": -13.96, "true_lon": 33.77},
    {"num": 34, "region": "AMERICAS", "city": "Bogotá", "summary": "Unions and students mount Paro Nacional strike over tax bill.", "true_lat": 4.71, "true_lon": -74.07},
    {"num": 35, "region": "AMERICAS", "city": "Mexico City", "summary": "Banxico publishes 3–2 split minutes on rate cut to 6.25%.", "true_lat": 19.43, "true_lon": -99.13},
    {"num": 36, "region": "AMERICAS", "city": "Washington", "summary": "FCC takes up drone spectrum and prison signal-jamming rules.", "true_lat": 38.91, "true_lon": -77.04},
    {"num": 37, "region": "AMERICAS", "city": "Ottawa", "summary": "Canada Disability Benefit issues November tranche up to C$204.", "true_lat": 45.42, "true_lon": -75.70},
    {"num": 38, "region": "AMERICAS", "city": "Atlanta", "summary": "US marks 50th Great American Smokeout public health campaign.", "true_lat": 33.75, "true_lon": -84.39},
    {"num": 39, "region": "GLOBAL & OCEANIA", "city": "Wellington", "summary": "Bumrah 3/31 rocks hosts before Nicholls 100* lifts NZ to 214/5.", "true_lat": -41.29, "true_lon": 174.78},
    {"num": 40, "region": "GLOBAL & OCEANIA", "city": "Nukuʻalofa", "summary": "Tonga declares 27-day emergency over El Niño drought crisis.", "true_lat": -21.14, "true_lon": -175.20},
    {"num": 41, "region": "GLOBAL & OCEANIA", "city": "Global", "summary": "Gold rebounds toward $3,755/oz from 14-mo low; Brent near $92.", "true_lat": 26.00, "true_lon": -40.00},
    {"num": 42, "region": "GLOBAL & OCEANIA", "city": "Singapore", "summary": "13 nations issue principles to crush SE Asia cyber-scam hubs.", "true_lat": 1.35, "true_lon": 103.82},
]

MAP_BOX = (28, 1512, 700, 1936)
MAP_VIEW = (42, 1550, 686, 1838)
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
    # Subtle sky gradient & soft cloud puffs in #1
    for band_y, col in ((0, "#F5EFE3"), (32, "#EFE6D5"), (64, "#E9DEC8")):
        draw.rectangle([0, band_y, w, band_y + 34], fill=col)
    for cx, cy, r in ((86, 40, 16), (106, 36, 18), (518, 38, 16), (538, 42, 14)):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#FAF6EE")
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
    _draw_pill_badge(draw, w / 2.0 - 38, 10, "APEC", fonts.get("sans_bold", 16), "#991B1B")

    # Three leader silhouettes behind curved table
    for lx, col in ((170, "#1E293B"), (312, "#0F172A"), (454, "#334155")):
        draw.ellipse([lx - 18, 78, lx + 18, 114], fill=col)
        draw.pieslice([lx - 42, 114, lx + 42, 168], 180, 360, fill=col)

    # Curved diplomatic walnut table
    draw.pieslice([76, 128, w - 76, 250], 180, 360, fill="#78350F", outline="#451A03", width=3)
    draw.pieslice([126, 148, w - 126, 240], 180, 360, fill="#92400E")

    # Stylized miniature flags (US, China, Russia)
    # US flag
    fx, fy = 148, 110
    draw.line([(fx, fy), (fx, 145)], fill="#111827", width=3)
    draw.rectangle([fx + 2, fy, fx + 46, fy + 28], fill="#FFFFFF", outline="#475569", width=1)
    for sy in range(0, 28, 6):
        draw.rectangle([fx + 2, fy + sy, fx + 46, fy + sy + 3], fill="#B91C1C")
    draw.rectangle([fx + 2, fy, fx + 22, fy + 15], fill="#1D4ED8")

    # China flag
    fx, fy = 290, 104
    draw.line([(fx, fy), (fx, 140)], fill="#111827", width=3)
    draw.rectangle([fx + 2, fy, fx + 46, fy + 28], fill="#DC2626", outline="#991B1B", width=1)
    _draw_star(draw, fx + 12, fy + 10, 6, 2.5, 5, "#FACC15")

    # Russia flag
    fx, fy = 432, 110
    draw.line([(fx, fy), (fx, 145)], fill="#111827", width=3)
    draw.rectangle([fx + 2, fy, fx + 46, fy + 9], fill="#FFFFFF", outline="#64748B", width=1)
    draw.rectangle([fx + 2, fy + 9, fx + 46, fy + 19], fill="#1D4ED8")
    draw.rectangle([fx + 2, fy + 19, fx + 46, fy + 28], fill="#DC2626")

    # Olive-branch center motif
    draw.arc([278, 152, 346, 184], 190, 350, fill="#D97706", width=3)


def _draw_scene_2(art_canvas, draw, fonts: FontBank) -> None:
    """#2 Anthropic Record $81.3bn Nasdaq IPO: Manhattan tower, neural nodes, rising chart."""
    w, h = art_canvas.size
    draw.text((22, 14), "$81.3BN", font=fonts.get("sans_bold", 42), fill="#0F172A")

    # Stylized Manhattan & cylindrical Nasdaq tower with window panes
    skyline = [(28, 198, 72, 116, "#94A3B8"), (78, 198, 128, 86, "#64748B"), (214, 198, 258, 106, "#94A3B8")]
    for x0, y1, x1, y0, col in skyline:
        draw.rectangle([x0, y0, x1, y1], fill=col)
        for wy in range(y0 + 10, y1 - 8, 14):
            draw.line([(x0 + 6, wy), (x1 - 6, wy)], fill="#E2E8F0", width=2)

    # Grid lines behind rising bars
    for gy in (44, 82, 120, 158):
        draw.line([(332, gy), (596, gy)], fill="#CBDCEB", width=1)

    # Curved Nasdaq tower
    draw.rectangle([134, 62, 208, 198], fill="#1E3A8A", outline="#0F172A", width=2)
    draw.pieslice([134, 48, 208, 76], 180, 360, fill="#3B82F6", outline="#0F172A", width=2)
    for gy in (88, 114, 140, 166):
        draw.line([(136, gy), (206, gy)], fill="#60A5FA", width=2)
    for gx in (152, 171, 190):
        draw.line([(gx, 62), (gx, 198)], fill="#1D4ED8", width=2)

    # Subtle AI neural node cluster
    nodes = [(252, 42), (288, 28), (316, 54), (274, 72), (308, 86)]
    for i, p1 in enumerate(nodes):
        for p2 in nodes[i + 1:]:
            draw.line([p1, p2], fill="#0F766E", width=2)
    for nx, ny in nodes:
        draw.ellipse([nx - 5, ny - 5, nx + 5, ny + 5], fill="#14B8A6", outline="#0F172A", width=1)

    # Rising green/teal IPO bars & breakout arrow
    bar_heights = [36, 52, 68, 88, 112, 138, 162]
    bx = 342
    for idx, bh in enumerate(bar_heights):
        col = "#0F766E" if idx < 5 else "#059669"
        if idx == 6:
            col = "#10B981"
        draw.rectangle([bx, h - bh, bx + 28, h], fill=col, outline="#064E3B", width=1)
        bx += 36
    draw.line([(336, 152), (464, 96), (576, 30)], fill="#B91C1C", width=5)
    draw.polygon([(588, 22), (562, 24), (578, 46)], fill="#B91C1C")


def _draw_scene_3(art_canvas, draw, fonts: FontBank) -> None:
    """#3 Riyadh Dawn Missile Intercept: Kingdom Centre skyline & interception starburst."""
    _ = fonts
    w, h = art_canvas.size
    draw.rectangle([0, 128, w, h], fill="#FDE68A")
    draw.rectangle([0, 150, w, h], fill="#FDBA74")

    # Riyadh skyline: Faisaliah spire + Kingdom Centre parabolic notch + towers
    draw.rectangle([40, 134, 88, h], fill="#475569")
    draw.polygon([(112, h), (138, 52), (164, h)], fill="#334155")
    draw.ellipse([132, 68, 144, 80], fill="#F59E0B")
    draw.rectangle([186, 116, 232, h], fill="#475569")

    # Kingdom Centre tower with parabolic skybridge cutout
    draw.polygon([(264, h), (274, 34), (344, 34), (354, h)], fill="#1E293B")
    draw.chord([284, 42, 334, 96], 0, 180, fill="#F5E1DA")
    draw.rectangle([296, 40, 322, 46], fill="#94A3B8")

    draw.rectangle([382, 122, 434, h], fill="#334155")
    draw.rectangle([454, 140, 502, h], fill="#475569")
    draw.rectangle([520, 128, 574, h], fill="#334155")

    # Dotted trajectory from SW
    for i in range(9):
        t = i / 8.0
        px = 42 + t * 396
        py = 164 - math.sin(t * math.pi * 0.52) * 114
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill="#B91C1C")

    # Defense radar wedge & interceptor trail from SE
    draw.polygon([(530, 174), (434, 52), (476, 44)], fill=(15, 118, 110, 48))
    draw.line([(530, 174), (446, 52)], fill="#0F766E", width=4)

    # Interception burst & shock rings
    ix, iy = 444, 52
    for r in (28, 42):
        draw.ellipse([ix - r, iy - r, ix + r, iy + r], outline="#D97706", width=2)
    _draw_star(draw, ix, iy, 24, 10, 9, "#F59E0B", "#B91C1C")
    _draw_star(draw, ix, iy, 12, 5, 7, "#FEF3C7")


def _draw_scene_4(art_canvas, draw, fonts: FontBank) -> None:
    """#4 ICJ Rohingya Verdict: Peace Palace, scales of justice, UN wreath."""
    w, h = art_canvas.size
    _draw_pill_badge(draw, w - 76, 10, "ICJ", fonts.get("sans_bold", 15), "#1E3A8A")

    # Peace Palace brick facade + stepped clocktower
    draw.rectangle([20, 62, 176, h], fill="#B45309", outline="#78350F", width=2)
    draw.polygon([(14, 62), (98, 42), (182, 62)], fill="#334155")
    draw.rectangle([44, 22, 74, 62], fill="#9A3412", outline="#78350F", width=1)
    draw.polygon([(40, 22), (59, 6), (78, 22)], fill="#1E293B")
    for wx in (36, 72, 108, 144):
        draw.rectangle([wx, 76, wx + 18, 108], fill="#E2E8F0")

    # UN blue disc + gold scales of justice
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

    # Cyclone spiral arms over Bay of Bengal
    cx, cy = 266, 56
    for r, col, sa in ((48, "#0F766E", 20), (36, "#1E293B", 80), (24, "#0F766E", 160)):
        draw.arc([cx - r, cy - r, cx + r, cy + r], sa, sa + 210, fill=col, width=6)
        draw.arc([cx - r, cy - r, cx + r, cy + r], sa + 180, sa + 350, fill=col, width=5)
    draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill="#B91C1C")

    # Wind-bent palm, alert triangle, shelter tents
    _draw_palm(draw, 44, 114, 58, 22, "#166534")
    draw.polygon([(92, 56), (124, 56), (108, 26)], fill="#B91C1C")
    draw.line([(108, 34), (108, 46)], fill="#FEF08A", width=3)
    draw.ellipse([106, 49, 110, 53], fill="#FEF08A")
    for tx in (86, 134):
        draw.polygon([(tx, 114), (tx + 20, 88), (tx + 40, 114)], fill="#EA580C", outline="#9A3412", width=2)

    draw.rounded_rectangle([w - 78, h - 38, w - 10, h - 6], radius=6, fill="#FFFFFF")
    _draw_centered_text(draw, w - 44, h - 22, "50K", fonts.get("sans_bold", 22), "#0F172A")


def _draw_scene_6(art_canvas, draw, fonts: FontBank) -> None:
    """#6 Berlin Ukraine Security Summit: Brandenburg Gate, Ukraine shield, EU stars."""
    _ = fonts
    w, h = art_canvas.size
    # Brandenburg Gate silhouette
    draw.rectangle([20, 44, 166, 56], fill="#B49263")
    draw.rectangle([28, 30, 158, 44], fill="#D6B88D", outline="#8C6D46", width=1)
    draw.rectangle([76, 14, 110, 30], fill="#475569")
    for cx in (32, 58, 84, 110, 136, 152):
        draw.rectangle([cx, 56, cx + 10, h], fill="#D6B88D", outline="#8C6D46", width=1)

    # Diplomatic curved table + Ukraine shield + arc of EU stars
    draw.pieslice([192, 86, w - 18, h + 30], 180, 360, fill="#78350F")
    sx, sy = 272, 68
    draw.polygon([(sx - 24, sy - 20), (sx + 24, sy - 20), (sx + 20, sy + 8), (sx, sy + 26), (sx - 20, sy + 8)], fill="#1D4ED8")
    draw.polygon([(sx - 21, sy + 2), (sx + 21, sy + 2), (sx + 18, sy + 8), (sx, sy + 24), (sx - 18, sy + 8)], fill="#FACC15")

    for ang_deg in range(-75, 80, 25):
        ang = math.radians(ang_deg - 90)
        ex = sx + math.cos(ang) * 52
        ey = sy + math.sin(ang) * 44
        _draw_star(draw, ex, ey, 6, 2.6, 5, "#F59E0B")


def _draw_scene_7(art_canvas, draw, fonts: FontBank) -> None:
    """#7 Antalya COP31 Crunch Day: Mediterranean wave, balance scale of green vs fossil."""
    w, h = art_canvas.size
    _draw_pill_badge(draw, 14, 10, "COP31", fonts.get("sans_bold", 15), "#065F46")
    draw.rectangle([0, 100, w, h], fill="#0284C7")
    draw.polygon([(20, 100), (62, 68), (104, 100)], fill="#FFFFFF", outline="#94A3B8", width=2)
    draw.polygon([(82, 100), (118, 74), (154, 100)], fill="#F1F5F9", outline="#94A3B8", width=2)

    # Balance scale
    cx = 252
    draw.line([(cx, 24), (cx, 114)], fill="#1E293B", width=4)
    draw.rectangle([cx - 28, 110, cx + 28, 118], fill="#1E293B")
    draw.line([(cx - 64, 38), (cx + 64, 28)], fill="#1E293B", width=4)

    # Left: clean leaf + turbine
    lx, ly = cx - 64, 38
    draw.line([(lx, ly), (lx, 74)], fill="#64748B", width=2)
    draw.ellipse([lx - 20, 58, lx + 4, 82], fill="#059669")
    draw.line([(lx + 10, 76), (lx + 10, 48)], fill="#065F46", width=3)
    for b_deg in (0, 120, 240):
        ba = math.radians(b_deg)
        draw.line([(lx + 10, 48), (lx + 10 + 14 * math.cos(ba), 48 + 14 * math.sin(ba))], fill="#0F766E", width=3)

    # Right: fossil smoke + draft scroll
    rx, ry = cx + 64, 28
    draw.line([(rx, ry), (rx, 70)], fill="#64748B", width=2)
    draw.rectangle([rx - 14, 52, rx - 4, 72], fill="#475569")
    draw.ellipse([rx - 16, 36, rx + 2, 52], fill="#64748B")
    draw.rectangle([rx + 4, 54, rx + 24, 72], fill="#FEF3C7", outline="#B91C1C", width=2)


def _draw_scene_8(art_canvas, draw, fonts: FontBank) -> None:
    """#8 GTA VI Release Day: sunset stripes, palms, console controller."""
    w, h = art_canvas.size
    for y0, y1, col in ((0, 32, "#FB7185"), (32, 62, "#F97316"), (62, 92, "#FBBF24"), (92, h, "#312E81")):
        draw.rectangle([0, y0, w, y1], fill=col)

    draw.text((w - 134, 10), "GTA VI", font=fonts.get("sans_bold", 34), fill="#4C1D95")
    _draw_palm(draw, 44, 118, 86, -12, "#1E1B4B")
    _draw_palm(draw, 94, 122, 68, 16, "#1E1B4B")

    # Modern gamepad controller
    gx, gy = 230, 82
    draw.rounded_rectangle([gx - 58, gy - 26, gx + 58, gy + 24], radius=22, fill="#1E1B4B", outline="#EC4899", width=2)
    draw.ellipse([gx - 66, gy - 6, gx - 28, gy + 38], fill="#1E1B4B")
    draw.ellipse([gx + 28, gy - 6, gx + 66, gy + 38], fill="#1E1B4B")
    draw.ellipse([gx - 34, gy - 8, gx - 16, gy + 10], fill="#38BDF8")
    for dx, dy, c in ((26, -12, "#EC4899"), (38, -2, "#FACC15"), (26, 8, "#38BDF8"), (14, -2, "#34D399")):
        draw.ellipse([gx + dx - 4, gy + dy - 4, gx + dx + 4, gy + dy + 4], fill=c)


def _draw_scene_9(art_canvas, draw, fonts: FontBank) -> None:
    """#9 Africa 44% War-Zone Children: Africa silhouette, 44% gauge, schoolhouse."""
    w, h = art_canvas.size
    africa_pts = [(34, 24), (78, 22), (92, 46), (112, 54), (96, 82), (82, 114), (64, 116), (56, 82), (32, 62), (24, 42)]
    draw.polygon(africa_pts, fill="#C2410C")

    # 44% donut gauge
    cx, cy, r = 196, 64, 42
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline="#D6CFC2", width=14)
    draw.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 158, fill="#B91C1C", width=14)
    _draw_centered_text(draw, cx, cy, "44%", fonts.get("sans_bold", 26), "#111827")

    # Schoolhouse & child silhouettes
    draw.rectangle([274, 62, 344, 112], fill="#FFFFFF", outline="#475569", width=2)
    draw.polygon([(266, 62), (309, 32), (352, 62)], fill="#1E293B")
    for chx in (294, 324):
        draw.ellipse([chx - 6, 76, chx + 6, 88], fill="#D97706")
        draw.rectangle([chx - 7, 90, chx + 7, 112], fill="#1E293B")


def _draw_scene_10(art_canvas, draw, fonts: FontBank) -> None:
    """#10 Australia 4.9% Jobless: Sydney Opera House shells + rising crimson bar spike."""
    w, h = art_canvas.size
    draw.rectangle([0, 102, w, h], fill="#0284C7")
    draw.rectangle([16, 94, 166, 104], fill="#CBD5E1")

    # Sydney Opera House sail shells
    for sx0, sx1, sy0 in ((24, 72, 40), (58, 108, 30), (94, 138, 48), (124, 158, 62)):
        draw.polygon([(sx0, 94), (sx0 + 12, sy0), (sx1, 94)], fill="#FFFFFF", outline="#64748B", width=2)

    draw.text((180, 10), "4.9%", font=fonts.get("sans_bold", 30), fill="#B91C1C")
    bars = [(194, 28, "#475569"), (224, 36, "#475569"), (254, 44, "#64748B"), (284, 58, "#DC2626"), (314, 78, "#B91C1C")]
    for bx, bh, col in bars:
        draw.rectangle([bx, 114 - bh, bx + 22, 114], fill=col)
    draw.line([(194, 80), (258, 64), (294, 48), (325, 28)], fill="#B91C1C", width=4)
    draw.polygon([(334, 22), (316, 24), (326, 38)], fill="#B91C1C")


def _draw_scene_11(art_canvas, draw, fonts: FontBank) -> None:
    """#11 Korea Suneung Flight Halt: prohibited plane circle + OMR answer sheet & pencil."""
    w, h = art_canvas.size
    _draw_pill_badge(draw, 14, 10, "35 MIN", fonts.get("sans_bold", 15), "#1E293B")

    # Airplane inside prohibited circle-slash
    cx, cy = 104, 72
    draw.polygon([(cx - 32, cy), (cx + 30, cy - 8), (cx + 36, cy), (cx + 30, cy + 6), (cx - 32, cy + 4)], fill="#1E3A8A")
    draw.polygon([(cx - 6, cy - 2), (cx + 12, cy - 26), (cx + 2, cy - 2)], fill="#1E3A8A")
    draw.polygon([(cx - 6, cy + 4), (cx + 10, cy + 26), (cx + 4, cy + 4)], fill="#1E3A8A")
    draw.ellipse([cx - 42, cy - 42, cx + 42, cy + 42], outline="#B91C1C", width=5)
    draw.line([(cx - 28, cy - 28), (cx + 28, cy + 28)], fill="#B91C1C", width=5)

    # OMR test sheet + pencil + muted phone cleanly spaced
    draw.rectangle([180, 22, 256, 114], fill="#FFFFFF", outline="#64748B", width=2)
    for ry in range(34, 106, 14):
        for rx in range(192, 248, 14):
            fill_c = "#1E293B" if (rx + ry) % 28 == 0 else "#CBD5E1"
            draw.ellipse([rx, ry, rx + 8, ry + 8], fill=fill_c)
    draw.polygon([(268, 104), (294, 28), (304, 32), (278, 108)], fill="#EAB308", outline="#92400E", width=1)
    draw.rounded_rectangle([316, 62, 348, 112], radius=5, fill="#1E293B")
    draw.rectangle([321, 69, 343, 101], fill="#475569")
    draw.line([(312, 66), (352, 106)], fill="#B91C1C", width=3)


def _draw_scene_12(art_canvas, draw, fonts: FontBank) -> None:
    """#12 Kerch Bridge Struck: twin-chord arch bridge, blast plume, roadblock."""
    _ = fonts
    w, h = art_canvas.size
    draw.rectangle([0, 92, w, h], fill="#0369A1")
    for wx in (20, 120, 230, 300):
        draw.line([(wx, 108), (wx + 40, 108)], fill="#7DD3FC", width=2)

    # Bridge piers + twin steel arch span + deck
    for px in (72, 148, 224, 300):
        draw.rectangle([px - 6, 74, px + 6, 112], fill="#64748B")
    draw.arc([138, 28, 234, 116], 180, 360, fill="#CBD5E1", width=6)
    draw.arc([142, 34, 230, 116], 180, 360, fill="#475569", width=3)
    draw.rectangle([0, 72, w, 82], fill="#334155")

    # Blast plume mid-span
    draw.ellipse([162, 16, 206, 54], fill="#475569")
    _draw_star(draw, 186, 58, 22, 9, 8, "#B91C1C")
    _draw_star(draw, 186, 60, 12, 5, 6, "#F59E0B")

    # Red-white striped roadblock barrier left
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

    deck_font = fonts.get("serif_italic", 23)
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

    title_font = fonts.get("sans_bold", 20)
    draw.text((mx0 + 14, my0 + 10), "WHERE IT HAPPENED", font=title_font, fill=PALETTE["ink"])

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

    leg_font = fonts.get("sans_condensed_bold", 15)
    leg_y0 = vy1 + 10
    col_w = 212
    for idx, region in enumerate(REGION_ORDER):
        col_i = idx % 3
        row_i = idx // 3
        lx = vx0 + col_i * col_w
        ly = leg_y0 + row_i * 23
        draw.rectangle([lx, ly + 3, lx + 14, ly + 17], fill=REGION_COLORS[region])
        label = f"{region} ({REGION_COUNTS[region]})"
        draw.text((lx + 20, ly + 1), label, font=leg_font, fill=PALETTE["sub_ink"])

    cap_y = leg_y0 + 48
    cap_font = fonts.get("sans_regular", 13)
    draw.ellipse([vx0, cap_y + 2, vx0 + 14, cap_y + 16], fill=PALETTE["crimson"])
    _draw_centered_text(draw, vx0 + 7, cap_y + 9, "1", fonts.get("sans_bold", 10), "#FFFFFF")
    part1 = "numbered pin: stories 1–13 above · "
    draw.text((vx0 + 18, cap_y + 1), part1, font=cap_font, fill=PALETTE["muted"])
    dot_x = vx0 + 18 + cap_font.getlength(part1) + 6
    draw.ellipse([dot_x - 4, cap_y + 5, dot_x + 4, cap_y + 13], fill=PALETTE["muted"])
    part2 = "dot: briefs 14–42 · Hairlines lead from crowded"
    draw.text((dot_x + 10, cap_y + 1), part2, font=cap_font, fill=PALETTE["muted"])
    draw.text((vx0, cap_y + 17), "spots to the true place.", font=cap_font, fill=PALETTE["muted"])


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

    bold_font = fonts.get("sans_bold", 16)
    reg_font = fonts.get("sans_regular", 16)

    lbl1 = "DATE CHECK — Verified 19 Nov UTC: "
    draw.text((dx0 + 18, dy0 + 9), lbl1, font=bold_font, fill=PALETTE["crimson"])
    draw.text((dx0 + 18 + bold_font.getlength(lbl1), dy0 + 9), DATE_CHECK_UTC, font=reg_font, fill=PALETTE["ink"])

    lbl2 = "Left out on purpose as Wednesday 18 November news: "
    draw.text((dx0 + 18, dy0 + 35), lbl2, font=bold_font, fill=PALETTE["sub_ink"])
    draw.text((dx0 + 18 + bold_font.getlength(lbl2), dy0 + 35), DATE_CHECK_EXCLUDED, font=reg_font, fill=PALETTE["sub_ink"])


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
