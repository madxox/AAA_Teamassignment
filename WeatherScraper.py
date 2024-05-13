import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from config import chromeDriverPath

CHROME_DRIVER_PATH = chromeDriverPath
WEBSITE = 'https://www.wunderground.com/history/daily/us/il/chicago/KMDW/date/'


def get_weather_data(driver, date):
    url = f"{WEBSITE}{date}"
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.mat-table")))

    # Get HTML with ChromeDriver
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    # Parsen with BeautifulSoup
    table = soup.select_one('table.mat-table')
    rows = table.select("tr.mat-row")
    daily_data = []

    for row in rows:
        cells = row.select("td")
        if cells:
            times = cells[0].get_text(strip=True)
            temperature = cells[1].get_text(strip=True).split('\xa0')[0]
            dew_point = cells[2].get_text(strip=True).split('\xa0')[0]
            humidity = cells[3].get_text(strip=True).split('\xa0')[0]
            wind = cells[4].text.strip()
            wind_speed = cells[5].get_text(strip=True).split('\xa0')[0]
            wind_gust = cells[6].get_text(strip=True).split('\xa0')[0]
            pressure = cells[7].get_text(strip=True).split('\xa0')[0]
            precipitation = cells[8].get_text(strip=True).split('\xa0')[0]
            condition = cells[9].text.strip()

            row_data = [date,
                        times,
                        temperature,
                        dew_point,
                        humidity,
                        wind,
                        wind_speed,
                        wind_gust,
                        pressure,
                        precipitation,
                        condition,
                        ]
            daily_data.append(row_data)

    return daily_data


def write_to_csv(data, date):
    filename = f'weather_data_{date}.csv'
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            ["Date",
             "Time",
             "Temperature",
             "Dew Point",
             "Humidity",
             "Wind",
             "Wind Speed",
             "Wind Gust",
             "Pressure",
             "Precip.",
             "Condition",
             ])
        for day_data in data:
            for hour_data in day_data:
                writer.writerow(hour_data)


def main():
    driver_service = Service(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=driver_service)
    driver.maximize_window()

    years = [2014, 2022]

    for year in years:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        delta = timedelta(days=1)

        weather = []
        while start_date <= end_date:
            formatted_date = start_date.strftime("%Y-%m-%d")
            daily_weather = get_weather_data(driver, formatted_date)
            weather.append(daily_weather)
            start_date += delta

        write_to_csv(weather, year)

    driver.quit()


if __name__ == "__main__":
    main()
