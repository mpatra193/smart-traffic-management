# data/camera_network.py
# 75 CCTV cameras covering all major crossings within 100km of Bhubaneswar, Odisha
# Includes: Bhubaneswar core, extended Bhubaneswar, NH16 to Cuttack, NH316 to Puri,
#           Cuttack city, Puri city, Khordha, Jatni, Pipili, Konark corridor

CCTV_POINTS = [
    # ═══════════════════════════════════════════════════════════════════
    # ZONE A: BHUBANESWAR CORE (0–24) — original 25 + densified
    # ═══════════════════════════════════════════════════════════════════
    # Row 0: South Bhubaneswar
    {"id": "BBS-01", "name": "Khandagiri Square",       "lat": 20.2589, "lon": 85.7831, "video": "intersection.mp4", "type": "4-way"},
    {"id": "BBS-02", "name": "Ganga Nagar",             "lat": 20.2590, "lon": 85.8120, "video": "intersection.mp4", "type": "4-way"},
    {"id": "BBS-03", "name": "AG Square",               "lat": 20.2625, "lon": 85.8318, "video": "intersection.mp4", "type": "4-way"},
    {"id": "BBS-04", "name": "Raj Mahal Square",        "lat": 20.2625, "lon": 85.8385, "video": "intersection.mp4", "type": "4-way"},
    {"id": "BBS-05", "name": "Kalpana Square",          "lat": 20.2543, "lon": 85.8432, "video": "intersection.mp4", "type": "4-way"},
    # Row 1
    {"id": "BBS-06", "name": "Fire Station Square",     "lat": 20.2721, "lon": 85.7981, "video": "intersection.mp4", "type": "4-way"},
    {"id": "BBS-07", "name": "Siripur Square",          "lat": 20.2730, "lon": 85.8100, "video": "intersection.mp4", "type": "4-way"},
    {"id": "BBS-08", "name": "Unit 4 Market",           "lat": 20.2730, "lon": 85.8250, "video": "intersection.mp4", "type": "2-way"},
    {"id": "BBS-09", "name": "Master Canteen",          "lat": 20.2666, "lon": 85.8436, "video": "intersection.mp4", "type": "4-way"},
    {"id": "BBS-10", "name": "Cuttack Rd South",        "lat": 20.2710, "lon": 85.8450, "video": "intersection.mp4", "type": "2-way"},
    # Row 2
    {"id": "BBS-11", "name": "CRP Square",              "lat": 20.2853, "lon": 85.8080, "video": "intersection.mp4", "type": "4-way"},
    {"id": "BBS-12", "name": "Nayapalli",               "lat": 20.2850, "lon": 85.8150, "video": "intersection.mp4", "type": "2-way"},
    {"id": "BBS-13", "name": "Shastri Nagar",           "lat": 20.2850, "lon": 85.8250, "video": "intersection.mp4", "type": "4-way"},
    {"id": "BBS-14", "name": "Ram Mandir Square",       "lat": 20.2766, "lon": 85.8415, "video": "intersection.mp4", "type": "4-way"},
    {"id": "BBS-15", "name": "Bomikhal",                "lat": 20.2844, "lon": 85.8465, "video": "intersection.mp4", "type": "2-way"},
    # Row 3
    {"id": "BBS-16", "name": "Rental Colony",           "lat": 20.2910, "lon": 85.8050, "video": "intersection.mp4", "type": "2-way"},
    {"id": "BBS-17", "name": "IRC Village",             "lat": 20.2910, "lon": 85.8120, "video": "intersection.mp4", "type": "4-way"},
    {"id": "BBS-18", "name": "Acharya Vihar",           "lat": 20.2965, "lon": 85.8245, "video": "intersection.mp4", "type": "4-way"},
    {"id": "BBS-19", "name": "Rupali Square",           "lat": 20.2882, "lon": 85.8368, "video": "intersection.mp4", "type": "4-way"},
    {"id": "BBS-20", "name": "VSS Nagar",               "lat": 20.2910, "lon": 85.8450, "video": "intersection.mp4", "type": "2-way"},
    # Row 4
    {"id": "BBS-21", "name": "Baramunda",               "lat": 20.2711, "lon": 85.7932, "video": "intersection.mp4", "type": "2-way"},
    {"id": "BBS-22", "name": "Jayadev Vihar Square",    "lat": 20.3013, "lon": 85.8175, "video": "intersection.mp4", "type": "4-way"},
    {"id": "BBS-23", "name": "Sainik School",           "lat": 20.3010, "lon": 85.8250, "video": "intersection.mp4", "type": "2-way"},
    {"id": "BBS-24", "name": "Vani Vihar",              "lat": 20.2942, "lon": 85.8340, "video": "intersection.mp4", "type": "4-way"},
    {"id": "BBS-25", "name": "Rasulgarh Square",        "lat": 20.2982, "lon": 85.8491, "video": "intersection.mp4", "type": "4-way"},

    # ═══════════════════════════════════════════════════════════════════
    # ZONE B: EXTENDED BHUBANESWAR (25–39)
    # ═══════════════════════════════════════════════════════════════════
    {"id": "BBS-26", "name": "Museum Square",           "lat": 20.2550, "lon": 85.8230, "video": "intersection.mp4", "type": "4-way"},  # 25
    {"id": "BBS-27", "name": "Ravi Talkies Square",     "lat": 20.2580, "lon": 85.8350, "video": "intersection.mp4", "type": "4-way"},  # 26
    {"id": "BBS-28", "name": "Shishu Bhawan Square",    "lat": 20.2700, "lon": 85.8320, "video": "intersection.mp4", "type": "4-way"},  # 27
    {"id": "BBS-29", "name": "Airport Square",          "lat": 20.2480, "lon": 85.8175, "video": "intersection.mp4", "type": "4-way"},  # 28
    {"id": "BBS-30", "name": "KIIT Square",             "lat": 20.3530, "lon": 85.8200, "video": "intersection.mp4", "type": "4-way"},  # 29
    {"id": "BBS-31", "name": "Patia Square",            "lat": 20.3586, "lon": 85.8230, "video": "intersection.mp4", "type": "4-way"},  # 30
    {"id": "BBS-32", "name": "Chandrasekharpur",        "lat": 20.3250, "lon": 85.8180, "video": "intersection.mp4", "type": "4-way"},  # 31
    {"id": "BBS-33", "name": "Kalinga Hospital Sq",     "lat": 20.3180, "lon": 85.8150, "video": "intersection.mp4", "type": "4-way"},  # 32
    {"id": "BBS-34", "name": "Damana Square",           "lat": 20.3350, "lon": 85.8220, "video": "intersection.mp4", "type": "4-way"},  # 33
    {"id": "BBS-35", "name": "Nandankanan Jn",          "lat": 20.3933, "lon": 85.8144, "video": "intersection.mp4", "type": "2-way"},  # 34
    {"id": "BBS-36", "name": "Mancheswar Sq",           "lat": 20.3050, "lon": 85.8520, "video": "intersection.mp4", "type": "4-way"},  # 35
    {"id": "BBS-37", "name": "Palasuni Square",         "lat": 20.3100, "lon": 85.8680, "video": "intersection.mp4", "type": "4-way"},  # 36
    {"id": "BBS-38", "name": "Phulnakhara",             "lat": 20.3350, "lon": 85.8800, "video": "intersection.mp4", "type": "2-way"},  # 37
    {"id": "BBS-39", "name": "Tamando",                 "lat": 20.2200, "lon": 85.7850, "video": "intersection.mp4", "type": "2-way"},  # 38
    {"id": "BBS-40", "name": "Pokhariput Square",       "lat": 20.2400, "lon": 85.7900, "video": "intersection.mp4", "type": "4-way"},  # 39

    # ═══════════════════════════════════════════════════════════════════
    # ZONE C: NH16 CORRIDOR — Bhubaneswar to Cuttack (40–46)
    # ═══════════════════════════════════════════════════════════════════
    {"id": "NH16-01", "name": "Trisulia",               "lat": 20.3600, "lon": 85.8850, "video": "intersection.mp4", "type": "2-way"},  # 40
    {"id": "NH16-02", "name": "Cuttack Bypass Jn",      "lat": 20.3800, "lon": 85.8900, "video": "intersection.mp4", "type": "4-way"},  # 41
    {"id": "NH16-03", "name": "Jagatpur",               "lat": 20.4100, "lon": 85.8850, "video": "intersection.mp4", "type": "2-way"},  # 42
    {"id": "NH16-04", "name": "NH16 Km-25",             "lat": 20.3400, "lon": 85.8650, "video": "intersection.mp4", "type": "2-way"},  # 43
    {"id": "NH16-05", "name": "Barang",                 "lat": 20.3700, "lon": 85.8500, "video": "intersection.mp4", "type": "2-way"},  # 44
    {"id": "NH16-06", "name": "Kantilo Rd Jn",          "lat": 20.3200, "lon": 85.8900, "video": "intersection.mp4", "type": "2-way"},  # 45
    {"id": "NH16-07", "name": "Choudwar Jn",            "lat": 20.4400, "lon": 85.8300, "video": "intersection.mp4", "type": "2-way"},  # 46

    # ═══════════════════════════════════════════════════════════════════
    # ZONE D: CUTTACK CITY (47–55)
    # ═══════════════════════════════════════════════════════════════════
    {"id": "CTC-01", "name": "Badambadi Bus Stand",     "lat": 20.4574, "lon": 85.8825, "video": "intersection.mp4", "type": "4-way"},  # 47
    {"id": "CTC-02", "name": "Buxi Bazaar",             "lat": 20.4620, "lon": 85.8880, "video": "intersection.mp4", "type": "4-way"},  # 48
    {"id": "CTC-03", "name": "College Square CTC",      "lat": 20.4650, "lon": 85.8830, "video": "intersection.mp4", "type": "4-way"},  # 49
    {"id": "CTC-04", "name": "Chauliaganj",             "lat": 20.4544, "lon": 85.9069, "video": "intersection.mp4", "type": "4-way"},  # 50
    {"id": "CTC-05", "name": "Dolomundai Square",       "lat": 20.4680, "lon": 85.8950, "video": "intersection.mp4", "type": "4-way"},  # 51
    {"id": "CTC-06", "name": "Madhupatna",              "lat": 20.4500, "lon": 85.8700, "video": "intersection.mp4", "type": "4-way"},  # 52
    {"id": "CTC-07", "name": "Khan Nagar",              "lat": 20.4550, "lon": 85.8950, "video": "intersection.mp4", "type": "4-way"},  # 53
    {"id": "CTC-08", "name": "Markat Nagar CDA",        "lat": 20.4725, "lon": 85.8389, "video": "intersection.mp4", "type": "4-way"},  # 54
    {"id": "CTC-09", "name": "Ranihat",                 "lat": 20.4700, "lon": 85.9050, "video": "intersection.mp4", "type": "2-way"},  # 55

    # ═══════════════════════════════════════════════════════════════════
    # ZONE E: SOUTH CORRIDOR — Khordha / Jatni (56–60)
    # ═══════════════════════════════════════════════════════════════════
    {"id": "SOU-01", "name": "Jatni Square",            "lat": 20.1650, "lon": 85.7100, "video": "intersection.mp4", "type": "4-way"},  # 56
    {"id": "SOU-02", "name": "Khordha Town",            "lat": 20.1850, "lon": 85.6200, "video": "intersection.mp4", "type": "4-way"},  # 57
    {"id": "SOU-03", "name": "Begunia Jn",              "lat": 20.1900, "lon": 85.6800, "video": "intersection.mp4", "type": "2-way"},  # 58
    {"id": "SOU-04", "name": "Janla",                   "lat": 20.2100, "lon": 85.7500, "video": "intersection.mp4", "type": "2-way"},  # 59
    {"id": "SOU-05", "name": "Aiginia Square",          "lat": 20.2350, "lon": 85.7700, "video": "intersection.mp4", "type": "4-way"},  # 60

    # ═══════════════════════════════════════════════════════════════════
    # ZONE F: NH316 CORRIDOR — Bhubaneswar to Puri (61–67)
    # ═══════════════════════════════════════════════════════════════════
    {"id": "NH316-01", "name": "Lingipur",              "lat": 20.2150, "lon": 85.8300, "video": "intersection.mp4", "type": "2-way"},  # 61
    {"id": "NH316-02", "name": "Pipili",                "lat": 20.1180, "lon": 85.8310, "video": "intersection.mp4", "type": "4-way"},  # 62
    {"id": "NH316-03", "name": "Nimapara Jn",           "lat": 20.0560, "lon": 85.8590, "video": "intersection.mp4", "type": "4-way"},  # 63
    {"id": "NH316-04", "name": "Sakhigopal",            "lat": 19.9280, "lon": 85.8420, "video": "intersection.mp4", "type": "4-way"},  # 64
    {"id": "NH316-05", "name": "Puri Bypass North",     "lat": 19.8600, "lon": 85.8380, "video": "intersection.mp4", "type": "2-way"},  # 65
    {"id": "NH316-06", "name": "Delang Jn",             "lat": 20.0900, "lon": 85.7600, "video": "intersection.mp4", "type": "2-way"},  # 66
    {"id": "NH316-07", "name": "Kakatpur Jn",           "lat": 20.0050, "lon": 85.9200, "video": "intersection.mp4", "type": "2-way"},  # 67

    # ═══════════════════════════════════════════════════════════════════
    # ZONE G: PURI CITY (68–72)
    # ═══════════════════════════════════════════════════════════════════
    {"id": "PURI-01", "name": "Grand Road (Bada Danda)", "lat": 19.8047, "lon": 85.8183, "video": "intersection.mp4", "type": "4-way"},  # 68
    {"id": "PURI-02", "name": "Gundicha Temple Jn",      "lat": 19.8134, "lon": 85.8315, "video": "intersection.mp4", "type": "4-way"},  # 69
    {"id": "PURI-03", "name": "Puri Bus Stand",          "lat": 19.8100, "lon": 85.8400, "video": "intersection.mp4", "type": "4-way"},  # 70
    {"id": "PURI-04", "name": "Marine Drive Puri",       "lat": 19.7950, "lon": 85.8250, "video": "intersection.mp4", "type": "2-way"},  # 71
    {"id": "PURI-05", "name": "Puri Station Road",       "lat": 19.8020, "lon": 85.8350, "video": "intersection.mp4", "type": "4-way"},  # 72

    # ═══════════════════════════════════════════════════════════════════
    # ZONE H: KONARK CORRIDOR (73–74)
    # ═══════════════════════════════════════════════════════════════════
    {"id": "KNK-01", "name": "Konark Jn",               "lat": 19.8870, "lon": 86.0945, "video": "intersection.mp4", "type": "4-way"},  # 73
    {"id": "KNK-02", "name": "Chandrabhaga",            "lat": 19.8750, "lon": 86.0700, "video": "intersection.mp4", "type": "2-way"},  # 74
]

# ═══════════════════════════════════════════════════════════════════════════════
# ROAD GRAPH — adjacency list (index-based, 0 = BBS-01 ... 74 = KNK-02)
# Encodes actual road connections: urban grid links, highway corridors, inter-city
# ═══════════════════════════════════════════════════════════════════════════════

ROAD_GRAPH = {
    # --- ZONE A: Bhubaneswar core (0-24) with cross-links to extended & new cams ---
    0:  [1, 5, 6, 20, 39],
    1:  [0, 2, 6, 7, 25],
    2:  [1, 3, 7, 8, 25, 26, 27],
    3:  [2, 4, 8, 9, 26, 27],
    4:  [3, 9],
    5:  [0, 6, 10, 11, 20],
    6:  [0, 1, 5, 7, 11, 12, 20],
    7:  [1, 2, 6, 8, 12, 13, 27],
    8:  [2, 3, 7, 9, 13, 14, 27],
    9:  [3, 4, 8, 14],
    10: [5, 11, 15, 16],
    11: [5, 6, 10, 12, 16, 17],
    12: [6, 7, 11, 13, 17, 18],
    13: [7, 8, 12, 14, 18, 19],
    14: [8, 9, 13, 19],
    15: [10, 16, 21],
    16: [10, 11, 15, 17, 21, 22],
    17: [11, 12, 16, 18, 22, 23],
    18: [12, 13, 17, 19, 23, 24],
    19: [13, 14, 18, 24],
    20: [0, 5, 6, 39],
    21: [15, 16, 22, 32],
    22: [16, 17, 21, 23, 32],
    23: [17, 18, 22, 24],
    24: [18, 19, 23, 35],

    # --- ZONE B: Extended Bhubaneswar (25-39) ---
    25: [1, 2, 26, 28],               # Museum Square
    26: [2, 3, 25, 27],               # Ravi Talkies
    27: [2, 3, 7, 8, 26, 28],         # Shishu Bhawan
    28: [25, 27, 29, 39, 60, 61],     # Airport Square → connects south
    29: [30, 33, 34],                  # KIIT Square
    30: [29, 34],                      # Patia Square
    31: [22, 32, 33],                  # Chandrasekharpur
    32: [21, 22, 31, 33],             # Kalinga Hospital
    33: [29, 31, 32, 34],             # Damana Square
    34: [29, 30, 33, 44],             # Nandankanan → connects to Barang
    35: [24, 36, 43],                  # Mancheswar
    36: [35, 37, 43, 45],             # Palasuni
    37: [36, 40, 43, 44],             # Phulnakhara
    38: [0, 39, 59],                   # Tamando
    39: [0, 20, 28, 38, 60],          # Pokhariput

    # --- ZONE C: NH16 Bhubaneswar-Cuttack corridor (40-46) ---
    40: [37, 41, 44],                  # Trisulia
    41: [40, 42, 46, 52],             # Cuttack Bypass Jn
    42: [41, 46, 52],                  # Jagatpur
    43: [35, 36, 37, 44],             # NH16 Km-25
    44: [34, 37, 40, 43],             # Barang
    45: [36, 37],                      # Kantilo Rd Jn
    46: [41, 42, 54],                  # Choudwar Jn

    # --- ZONE D: Cuttack city (47-55) ---
    47: [48, 52, 53],                  # Badambadi Bus Stand
    48: [47, 49, 51, 53],             # Buxi Bazaar
    49: [48, 51, 54],                  # College Square
    50: [51, 53, 55],                  # Chauliaganj
    51: [48, 49, 50, 55],             # Dolomundai Square
    52: [41, 42, 47, 54],             # Madhupatna
    53: [47, 48, 50],                  # Khan Nagar
    54: [46, 49, 52],                  # Markat Nagar CDA
    55: [50, 51],                      # Ranihat

    # --- ZONE E: South corridor - Khordha/Jatni (56-60) ---
    56: [57, 58, 59],                  # Jatni Square
    57: [56, 58],                      # Khordha Town
    58: [56, 57, 59],                  # Begunia Jn
    59: [38, 56, 58, 60],             # Janla
    60: [28, 39, 59, 61],             # Aiginia Square

    # --- ZONE F: NH316 Bhubaneswar-Puri corridor (61-67) ---
    61: [28, 60, 62],                  # Lingipur
    62: [61, 63, 66],                  # Pipili
    63: [62, 64, 66, 67],             # Nimapara Jn
    64: [63, 65, 67],                  # Sakhigopal
    65: [64, 69, 70],                  # Puri Bypass North
    66: [62, 63],                      # Delang Jn
    67: [63, 64, 73],                  # Kakatpur Jn → Konark

    # --- ZONE G: Puri city (68-72) ---
    68: [69, 71, 72],                  # Grand Road
    69: [65, 68, 70],                  # Gundicha Temple Jn
    70: [65, 69, 72],                  # Puri Bus Stand
    71: [68, 72],                      # Marine Drive Puri
    72: [68, 70, 71],                  # Puri Station Road

    # --- ZONE H: Konark corridor (73-74) ---
    73: [67, 74],                      # Konark Jn
    74: [73],                          # Chandrabhaga
}
