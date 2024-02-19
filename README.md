# Waybacker

A simple wrapper around the [Wayback Machine](https://archive.org/web/) to ensure **reproducibility** when collecting web pages from the internet.

> **TL;DR** Waybacker converts every URL into a Wayback URL, and stores the webpage together with the used URL.
> This is experimental code.


# Install
````shell
git clone git@github.com:Max216/simple-waybacker.git && cd simple-waybacker
pip install . -U
````

# Getting Started
You can use the `Waybacker` as a wrapper when collecting webpages to:
* **Avoid unnecessary traffic**: Each requested webpage is automatically downloaded.
* **Work on reproducible data**: Each downloaded data as-is exists on the Wayback Machine.
* **Know how to reproduce the data**: The Wayback URL for each requested webpage is automatically saved.

**Example Usage:**
````python
from waybacker import Waybacker, WaybackEntry

waybacker = Waybacker()  # By default, all webpages will be stored in the "waybacker" directory in HOME.

# We have these URLs we want to crawl.
urls = [
    'https://www.wired.com/story/women-in-science-sabrina-gonzalez-pasterski/',
    'https://www.wired.com/story/moon-asteroid-origins/',
    'https://www.wired.com/story/as-amazon-launches-project-kuiper-astronomers-debate-how-to-fix-a-satellite-filled-sky/',
]

for url in urls:
    entry: WaybackEntry = waybacker.get(url)
    print(entry.success)  # True
    print(entry.full_path)  # absolute path of the downloaded webpage
    print(entry.wayback_data["url"])  # wayback URL
    # ...
````

# Storage
By default, the `Waybacker` will use the directory specified via the environment variable `WAYBACKER_DIR` to store
its database and all downloaded webpages. If unspecified, the `waybacker/` directory within the user home directory will be used.
One can overwrite these preferences programmatically when specifying the `directory` directly:

````python
from waybacker import Waybacker

waybacker = Waybacker(
    directory="/my/custom/directory",  # Will overwrite the directory of the environment variable
    sleep_time_seconds=5  # Sleep five seconds after each request
)
````

# Usage of the ``Waybacker``

## ``Waybacker.get()``
Request a webpage via GET request from Wayback. By default, only new requests are forwarded to Wayback. 
If the requested URL was requested before, the corresponding entry (successful and unsuccessful) is returned instead.

By default, each time the `.get()` method is invoked with a new URL, the corresponding webpage is collected. 
If this fails (for example, if the webpage is not in Wayback), the error is stored instead. Future calls to the identical URL
will always use the cached result and not query the Wayback engine again (unless specified to do so).

**Arguments**

| Name                   | Description                                                                               | Example                                                                        |
|------------------------|-------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| ``url``                | The URL to the live webpage that will be collected from Wayback.                          | ``"https://www.wired.com/story/women-in-science-sabrina-gonzalez-pasterski/"`` |
| ``retry_unsuccessful`` | Force to retry collecting URLs where previous errors occurred.                            | `True`                                                                         |
| ``overwrite_entry``    | Force to re-load and overwrite each URL entry. **Warning: You may lose reproducibility.** | `True`                                                                         |


## ``Waybacker.lookup()``
Only looks at the database if an entry for the provided URL exists, neither updates nor attempts to collect the webpage.
Returns the corresponding `WaybackEntry` if it exists (or `None`).

**Arguments**

| Name                   | Description                                     | Example                                                                        |
|------------------------|-------------------------------------------------|--------------------------------------------------------------------------------|
| ``url``                | The URL to to lookup in the collected webpages. | ``"https://www.wired.com/story/women-in-science-sabrina-gonzalez-pasterski/"`` |



## ``Waybacker.export_csv()``
Export a list of URLs as CSV file that can be shared for other people to collect the identical webpages from Wayback.
Internally, this method calls ``.get()`` for every URL, i.e. it will attempt to collect each new URL provided within the `urls`.

**Arguments**

| Name     | Description                         | Example                                                                        |
|----------|-------------------------------------|--------------------------------------------------------------------------------|
| ``urls`` | List of URLs that will be exported. | ``"https://www.wired.com/story/women-in-science-sabrina-gonzalez-pasterski/"`` |
| ``dest_path`` | Filepath of the resulting CSV file. | ``"/path/to/exported.csv"``                                                    |

**Example:**
````python
from waybacker import Waybacker
import pandas as pd

waybacker = Waybacker()  # By default, all webpages will be stored in the "waybacker" directory in HOME.

# We have these URLs we want to crawl.
urls = [
    'https://www.wired.com/story/women-in-science-sabrina-gonzalez-pasterski/',
    'https://www.wired.com/story/moon-asteroid-origins/',
    'https://www.wired.com/story/as-amazon-launches-project-kuiper-astronomers-debate-how-to-fix-a-satellite-filled-sky/',
]

# Save CSV file and return as dataframe
df: pd.DataFrame = waybacker.export_csv(urls, "/path/to/exported.csv")
print(df.head())
````


# Usage of the ``LiveURLCollector``
To simplify the collection of relevant links, use the `LiveURLCollector` class, which automatically paginates over the 
desired webpage (*live!*) and returns a list of all links pointing to the *live* websites. The `LiveURLCollector`  takes the following arguments:

**Arguments**

| Name | Description                                                                      | Example                                    | 
| ---|----------------------------------------------------------------------------------|--------------------------------------------|
| ``link_query`` | CSS selector to locate the <a></a> links that refer to the URLs to be collected. | `"div.container > a.link"`                 |
| ``overview_iterator`` | URL used for pagination. Must include the placeholder `"@@PAGE@@"`.              | `"https://domain.org/items?page=@@PAGE@@"` |
| ``start_page_index`` | First page index to be used (will replace `"@@PAGE@@"`; default=`1`).            | `1`                                        |
| ``link_query`` | Sleep time in seconds before increasing the `start_page_index` (default=`1`).      | `5`                                        |

**Example:**

To collect `10` URLs from [WIRED about space](https://www.wired.com/category/science/space/) run the following code:
````python
from waybacker import LiveURLCollector

collector: LiveURLCollector = LiveURLCollector(
    link_query='.summary-item__content > a.summary-item__hed-link',
    overview_iterator='https://www.wired.com/category/science/space/?page=@@PAGE@@'
)

# Collect 10 links from the LIVE webpage. We will later crawl each link from WayBack.
for entry in collector.collect_urls(max_links=10):
    url: str = entry.url  # Do something with the collected URL.
    page_number: int = entry.page  # e.g. 1
````



