# Check if hishel works properly

Only works from linux:

run
```sh
poetry shell
poetry install
uvicorn main:app --reload
```


then run
```sh
sudo tcpdump -n dst host tile.openweathermap.org or host services.swpc.noaa.gov
```
