from datetime import date, datetime

from pydantic import BaseModel


class NooaAuroraKp27Row(BaseModel):
    date: date
    radio_flux: int
    planetary_index: int
    largest_kp_index: int


def parse_kp_27_outlook(data: str) -> list[NooaAuroraKp27Row]:
    res = []
    for line in data.splitlines():
        if line.startswith("#"):
            continue
        if line.startswith(":"):
            continue
        line = line.strip()
        if not line:
            continue
        raw_date, radio_flux, planetary_index, largest_kp_index = line.rsplit(
            maxsplit=3
        )
        date = datetime.strptime(raw_date, "%Y %b %d").date()
        res.append(
            NooaAuroraKp27Row(
                date=date,
                radio_flux=radio_flux,
                planetary_index=planetary_index,
                largest_kp_index=largest_kp_index,
            )
        )
    return res


class NooaAuroraKp3RowValue(BaseModel):
    time: str
    kp_index: float


class NooaAuroraKp3Col(BaseModel):
    date: str
    values: list[NooaAuroraKp3RowValue]


def parse_kp_3_forecast(data: str) -> list[NooaAuroraKp3Col]:
    res: list[NooaAuroraKp3Col] = []
    cols_init = False
    for line in data.splitlines():
        if line.startswith("#"):
            continue
        if line.startswith(":"):
            continue
        if len(line) < 3:
            continue
        if line.startswith("          ") and not cols_init:
            columns = line.strip().rsplit("    ", maxsplit=2)
            for col in columns:
                res.append(NooaAuroraKp3Col(date=col.strip(), values=[]))
            cols_init = True
        if line[2] != "-":
            continue
        if "UT" not in line:
            continue
        line = line.replace("(G1)", "").strip()
        if not line:
            continue
        raw_date, raw_values = line.split(maxsplit=1)
        values = raw_values.split(maxsplit=2)

        for num in range(len(columns)):
            if not res:
                raise Exception("No cols init")
            res[num].values.append(
                NooaAuroraKp3RowValue(
                    time=raw_date,
                    kp_index=values[num],
                )
            )
    return res
