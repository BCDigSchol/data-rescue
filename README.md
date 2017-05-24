# DataRescue at Boston College
On 19 April 2017, staff and friends of Boston College participated in [Endangered Data Week](http://endangereddataweek.org/) by holding a data rescue event. The goal for this event was to identify, archive and secure [NEH](https://catalog.data.gov/organization/neh-gov) and [IMLS](https://catalog.data.gov/organization/imls-gov) datasets gathered from [data.gov](http://data.gov).

## Approach to this task
There are a few ways of approaching this task. The most direct method is to manually scrape each respective data.gov dataset web page. At the time of the data rescue event, we identified 8 NEH datasets and 78 IMLS datasets. Manually scraping each dataset web page was managable in theory but not desirable. We instead decided to automate this process with the hope of developing reusable scripts that take advantage of the publically available data.gov APIs.

### Data.gov and CKAN
Data.gov is built atop [CKAN](https://ckan.org/developers/about-ckan/), an open-source data manangement system. CKAN offers a set of public APIs that allow for scripts to interact with the underlying data and metadata. Data.gov offers the same [APIs](https://www.data.gov/developers/apis) but it should be noted that they don't actually host any datasets. Data.gov provides the metadata that contains the URI of the datasets. These datasets are usually hosted on their respective organization's servers.

## Scraping data.gov APIs
With a little help from [GitHub comments](https://github.com/GSA/data.gov/issues/315#issuecomment-275747388), we were able to figure out the API query structure.

We used the following API queries:
* NEH: `https://catalog.data.gov/api/action/package_search?fq=(organization:%22neh-gov%22+AND+(type:dataset))`
* IMLS: `https://catalog.data.gov/api/action/package_search?fq=(organization:%22imls-gov%22+AND+(type:dataset))`

These APIs return JSON formatted results, which we then saved as [neh-gov.json](data/neh/neh-gov.json) and [imls-gov.json](data/imls/imls-gov.json) respectfully.

## Parsing API query results
Next, we needed to parse the API query results to get the dataset URIs. Since data.gov doesn't store the datasets we need to find each dataset's URI. And since there are usually multiple formats for each dataset so we wanted to fetch each one.

In the span of about 24 hours, we put together a few python scripts using [Jupyter Notebook](http://jupyter.org/) to parse and fetch each dataset. These files are labeled as [data.gov_imls-gov.ipynb](data.gov_imls-gov.ipynb) and [data.gov_imls-gov.ipynb](data.gov_imls-gov.ipynb). Also provided are normal python scripts (.py) converted from the Jupyter Notebook files. These files have been tested to work with Python 2.7.13.

We decided to develop a script for each organization since the json key names for each organization API query were slightly different from each other. 

It is definitely possible to refactor the scripts and make an adaptable framework for scraping data.gov APIs. But given our short time frame to develop these scripts, we quickly put together something that _just worked_.

## Fetching datasets

The scripts expect to find a json file within the included `data/` directory. For instance, `data.gov_imls-gov.ipynb` expects to find `neh-gov.json` within [data/neh/](data/neh/). From there, the script will parse the json file to find each dataset URI, download, and save the dataset to a generated directory where it found the json file. If there are multiple dataset formats then each one will be downloaded to the same directory. A log file of each transaction is also generated.
