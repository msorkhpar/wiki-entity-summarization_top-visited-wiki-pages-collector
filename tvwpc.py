import requests
import pandas as pd
from datetime import date

PROJECT = "en.wikipedia.org"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.3"
}
IGNORED_PAGES = [
    "Special:",
    "Wikipedia:",
    "Portal:",
    "Template:",
    "Category:",
    "File:",
    "MediaWiki:",
    "User:",
    "Help:",
    "Draft:",
    "Book:",
]


def fetch_top_visited_wikipedia_pages(top_n, output_csv_path, to_year, to_month, from_year=2015, from_month=7):
    if from_year < 2015 and from_month < 7:
        raise ValueError("The minimum date is 2015/07.")
    if to_year > date.today().year or (to_year == date.today().year and to_month > date.today().month - 1):
        raise ValueError("The maximum date is the current month-1.")
    data_dict = {}

    for year in range(from_year, to_year + 1):
        for month in range(1, 13):
            if year == 2015 and month < 7:
                continue
            # Skip future months
            if year == to_year and month > to_month:
                break

            print(f"Fetching data for `{year}/{month:02}`...")
            api_endpoint = (f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/"
                            f"{PROJECT}/all-access/{year}/{month:02}/all-days")

            response = requests.get(api_endpoint, headers=HEADERS)

            if response.status_code == 200:
                data = response.json()
                for entry in data["items"][0]["articles"]:
                    name = entry["article"]
                    if (any(name.startswith(page) for page in IGNORED_PAGES) or
                            name.endswith(".php") or
                            name == "Main_Page"):
                        continue

                    if name in data_dict:
                        data_dict[name]["Views"] += entry["views"]
                    else:
                        data_dict[name] = {"Name": name, "Views": entry["views"]}
            else:
                print(f"Failed to retrieve data for `{year}/{month}`. Status Code: `{response.status_code}`")

    df = pd.DataFrame(list(data_dict.values()))
    df = df.sort_values(by="Views", ascending=False)
    top_df = df.head(top_n)
    print("Finished fetching data!")
    top_df.to_csv(output_csv_path, index=False, header=True)
    print(f"Saved the top `{top_n}` pages to `{output_csv_path}`.")
