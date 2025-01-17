from .nooa_parser import parse_kp_3_forecast, parse_kp_27_outlook


def test_parse_kp_3_forecast():
    data = """
:Product: 3-Day Forecast
:Issued: 2025 Jan 11 1230 UTC
# Prepared by the U.S. Dept. of Commerce, NOAA, Space Weather Prediction Center
#
A. NOAA Geomagnetic Activity Observation and Forecast

The greatest observed 3 hr Kp over the past 24 hours was 4 (below NOAA
Scale levels).
The greatest expected 3 hr Kp for Jan 11-Jan 13 2025 is 2.67 (below NOAA
Scale levels).

NOAA Kp index breakdown Jan 11-Jan 13 2025

             Jan 11       Jan 12       Jan 13
00-03UT       2.67         1.33         1.67
03-06UT       0.67         1.67         1.67
06-09UT       1.00         1.33         1.67
09-12UT       1.67         1.33         1.33
12-15UT       2.33         1.33         1.33
15-18UT       2.67         1.33         1.33
18-21UT       2.67         1.67         1.33
21-00UT       2.67         1.67         1.33

Rationale: No G1 (Minor) or greater geomagnetic storms are expected.  No
significant transient or recurrent solar wind features are forecast.
"""
    res = parse_kp_3_forecast(data)
    r = [i.model_dump(mode="json") for i in res]
    assert r == [
        {
            "date": "Jan 11",
            "values": [
                {
                    "time": "00-03UT",
                    "kp_index": 2.67,
                },
                {
                    "time": "03-06UT",
                    "kp_index": 0.67,
                },
                {
                    "time": "06-09UT",
                    "kp_index": 1.00,
                },
                {
                    "time": "09-12UT",
                    "kp_index": 1.67,
                },
                {
                    "time": "12-15UT",
                    "kp_index": 2.33,
                },
                {
                    "time": "15-18UT",
                    "kp_index": 2.67,
                },
                {
                    "time": "18-21UT",
                    "kp_index": 2.67,
                },
                {
                    "time": "21-00UT",
                    "kp_index": 2.67,
                },
            ],
        },
        {
            "date": "Jan 12",
            "values": [
                {
                    "time": "00-03UT",
                    "kp_index": 1.33,
                },
                {
                    "time": "03-06UT",
                    "kp_index": 1.67,
                },
                {
                    "time": "06-09UT",
                    "kp_index": 1.33,
                },
                {
                    "time": "09-12UT",
                    "kp_index": 1.33,
                },
                {
                    "time": "12-15UT",
                    "kp_index": 1.33,
                },
                {
                    "time": "15-18UT",
                    "kp_index": 1.33,
                },
                {
                    "time": "18-21UT",
                    "kp_index": 1.67,
                },
                {
                    "time": "21-00UT",
                    "kp_index": 1.67,
                },
            ],
        },
        {
            "date": "Jan 13",
            "values": [
                {
                    "time": "00-03UT",
                    "kp_index": 1.67,
                },
                {
                    "time": "03-06UT",
                    "kp_index": 1.67,
                },
                {
                    "time": "06-09UT",
                    "kp_index": 1.67,
                },
                {
                    "time": "09-12UT",
                    "kp_index": 1.33,
                },
                {
                    "time": "12-15UT",
                    "kp_index": 1.33,
                },
                {
                    "time": "15-18UT",
                    "kp_index": 1.33,
                },
                {
                    "time": "18-21UT",
                    "kp_index": 1.33,
                },
                {
                    "time": "21-00UT",
                    "kp_index": 1.33,
                },
            ],
        },
    ]


def test_parse_kp_3_forecast_g_values():
    data = """
:Product: 3-Day Forecast
:Issued: 2025 Jan 23 0030 UTC
# Prepared by the U.S. Dept. of Commerce, NOAA, Space Weather Prediction Center
#
A. NOAA Geomagnetic Activity Observation and Forecast

The greatest observed 3 hr Kp over the past 24 hours was 3 (below NOAA
Scale levels).
The greatest expected 3 hr Kp for Jan 23-Jan 25 2025 is 5.33 (NOAA Scale
G1).

NOAA Kp index breakdown Jan 23-Jan 25 2025

             Jan 23       Jan 24       Jan 25
00-03UT       1.67         1.67         3.33
03-06UT       1.33 (G3)    1.33         5.33 (G1)
06-09UT       1.33         1.33         5.00 (G5)
09-12UT       1.33         1.33 (G2)    4.00
12-15UT       1.33         4.00         4.00
15-18UT       1.33         2.67         3.33
18-21UT       1.67 (G4)    4.00         3.33
21-00UT       1.67         4.33         4.00

Rationale: G1 (Minor) or greater geomagnetic storms are expected on 25
Jan due to the potential arrival of a CME from 22 Jan.

B. NOAA Solar Radiation Activity Observation and Forecast

Solar radiation, as observed by NOAA GOES-18 over the past 24 hours, was
below S-scale storm level thresholds.

Solar Radiation Storm Forecast for Jan 23-Jan 25 2025

              Jan 23  Jan 24  Jan 25
S1 or greater   10%     10%     10%

Rationale: No S1 (Minor) or greater solar radiation storms are expected.


C. NOAA Radio Blackout Activity and Forecast

Radio blackouts reaching the R1 levels were observed over the past 24
hours. The largest was at Jan 22 2025 1108 UTC.

Radio Blackout Forecast for Jan 23-Jan 25 2025

              Jan 23        Jan 24        Jan 25
R1-R2           55%           55%           55%
R3 or greater   10%           10%           10%

Rationale: R1-R2 (Minor-Moderate) radio blackout events are likely, with
slight chance for R2 (Strong) events, over 23-25 Jan due to the flare
potential of multiple regions on the visible disk.
"""
    res = parse_kp_3_forecast(data)
    r = [i.model_dump(mode="json") for i in res]
    assert r == [
        {
            "date": "Jan 23",
            "values": [
                {
                    "time": "00-03UT",
                    "kp_index": 1.67,
                },
                {
                    "time": "03-06UT",
                    "kp_index": 1.33,
                },
                {
                    "time": "06-09UT",
                    "kp_index": 1.33,
                },
                {
                    "time": "09-12UT",
                    "kp_index": 1.33,
                },
                {
                    "time": "12-15UT",
                    "kp_index": 1.33,
                },
                {
                    "time": "15-18UT",
                    "kp_index": 1.33,
                },
                {
                    "time": "18-21UT",
                    "kp_index": 1.67,
                },
                {
                    "time": "21-00UT",
                    "kp_index": 1.67,
                },
            ],
        },
        {
            "date": "Jan 24",
            "values": [
                {
                    "time": "00-03UT",
                    "kp_index": 1.67,
                },
                {
                    "time": "03-06UT",
                    "kp_index": 1.33,
                },
                {
                    "time": "06-09UT",
                    "kp_index": 1.33,
                },
                {
                    "time": "09-12UT",
                    "kp_index": 1.33,
                },
                {
                    "time": "12-15UT",
                    "kp_index": 4.00,
                },
                {
                    "time": "15-18UT",
                    "kp_index": 2.67,
                },
                {
                    "time": "18-21UT",
                    "kp_index": 4.0,
                },
                {
                    "time": "21-00UT",
                    "kp_index": 4.33,
                },
            ],
        },
        {
            "date": "Jan 25",
            "values": [
                {
                    "time": "00-03UT",
                    "kp_index": 3.33,
                },
                {
                    "time": "03-06UT",
                    "kp_index": 5.33,
                },
                {
                    "time": "06-09UT",
                    "kp_index": 5.0,
                },
                {
                    "time": "09-12UT",
                    "kp_index": 4.0,
                },
                {
                    "time": "12-15UT",
                    "kp_index": 4.0,
                },
                {
                    "time": "15-18UT",
                    "kp_index": 3.33,
                },
                {
                    "time": "18-21UT",
                    "kp_index": 3.33,
                },
                {
                    "time": "21-00UT",
                    "kp_index": 4.00,
                },
            ],
        },
    ]


def test_parse_kp_27_outlook():
    data = """
:Product: 27-day Space Weather Outlook Table 27DO.txt
:Issued: 2025 Jan 06 0242 UTC
# Prepared by the US Dept. of Commerce, NOAA, Space Weather Prediction Center
# Product description and SWPC contact on the Web
# https://www.swpc.noaa.gov/content/subscription-services
#
#      27-day Space Weather Outlook Table
#                Issued 2025-01-06
#
#   UTC      Radio Flux   Planetary   Largest
#  Date       10.7 cm      A Index    Kp Index
2025 Jan 06     172          22          5
2025 Jan 07     165          12          4
2025 Jan 08     165           8          3
"""
    res = parse_kp_27_outlook(data)
    r = [i.model_dump(mode="json") for i in res]
    assert r == [
        {
            "date": "2025-01-06",
            "radio_flux": 172,
            "planetary_index": 22,
            "largest_kp_index": 5,
        },
        {
            "date": "2025-01-07",
            "radio_flux": 165,
            "planetary_index": 12,
            "largest_kp_index": 4,
        },
        {
            "date": "2025-01-08",
            "radio_flux": 165,
            "planetary_index": 8,
            "largest_kp_index": 3,
        },
    ]
