API 
====
The main API endpoint displays the API documentation and homepage and forms the base URL for the 5 other endpoints: |api_main_endpoint|

.. |api_main_endpoint| raw:: html

   <a href="https://iso3166-updates.vercel.app/api" target="_blank">https://iso3166-updates.vercel.app/api</a>

The other endpoints available in the API are:

* https://iso3166-updates.vercel.app/api/all
* https://iso3166-updates.vercel.app/api/alpha/<input_alpha>  
* https://iso3166-updates.vercel.app/api/year/<input_year>
* https://iso3166-updates.vercel.app/api/search/<input_search>
* https://iso3166-updates.vercel.app/api/alpha/<input_alpha>/year/<input_year>
* https://iso3166-updates.vercel.app/api/search/<input_search>/year/<input_year>
* https://iso3166-updates.vercel.app/api/date_range/<input_date_range>
* https://iso3166-updates.vercel.app/api/date_range/<input_date_range>/alpha/<input_alpha>
* https://iso3166-updates.vercel.app/api/date_range/<input_date_range>/search/<input_search>

Below are some example usage of the API and the above endpoints, utilising the **Python Requests** library.
 
.. The paths/endpoints available in the API are - `/api/all`, `/api/alpha`, `/api/name`, `/api/year, `/api/date_range` and `/api/search`

.. * The `/api/all` path/endpoint returns all of the ISO 3166 updates/changes data for all countries.

.. * The ISO 3166-1 2 letter alpha-2, 3 letter alpha-3 or numeric country codes can be appended to the alpha path/endpoint e.g., `/api/alpha/JP`. A single alpha code or a comma separated list of them can be passed to the API e.g., `/api/alpha/FR,DEU,HUN,360`. The alpha endpoint can be used in conjunction with the year endpoint to get the country updates for a country and year, in the format `/api/alpha/<input_alpha>/year/<input_year>` or `/api/year/<input_year>/alpha/<input_alpha>`. It can also be used in conjunction with the date_range endpoint, to get the updates for a particular country in a date range, in the format `/api/alpha/<input_alpha>/date_range/<input_date_range>` or `/api/date_range/<input_date_range>/alpha/<input_alpha>`. If an invalid alpha code is input then an error will be returned.

.. * The year parameter can be a year, year range, a cut-off year to get updates less than/more than a year, or a year to exclude in the results. The year value can be appended to the year path/endpoint e.g., `/api/year/2017`, `/api/year/2010-2015`, `/api/year/<2009`, `/api/year/>2002`, `/api/year/<>2020` The year endpoint can be used in conjunction with the alpha and search endpoints to get the country updates for a country using the publication year, alpha code and inputted search terms, in the format `/api/alpha/<input_alpha>/year/<input_year>` and `/api/search/<input_search>/year/<input_year>`, respectively. If an invalid year is input then an error will be returned.

.. * The date range endpoint will gather all updates for 1 or more countries from an input publication date range, inclusive. The date range value can be appended to the date_range path/endpoint e.g., `/api/date_range/2002-03-12,2004-10-08`, `/api/date_range/2005-12-01,2006-03-03`, `/api/date_range/2020-11-10`. If an invalid date range value is input then an error will be returned.

.. * The search endpoint will gather all updates for 1 or more countries that contain the specified search terms in their Change or Description of Change attributes, in the format `/api/search/<input_search_term>`. By default an exact match is looked for within the updates data, but the query string parameter `likeness` (default of 1.0) can be reduced which will expand the search space, e.g `?likeness=0.5` will return updates data whose attributes have a 50% match to the inputtes search terms, thus likely returning more results.

.. * The main API endpoint (`/` or `/api`) will return the homepage and API documentation.

Query String Parameters
-----------------------
There are 3 main query string parameters available throughout the API that can be appended to your GET request:

* **likeness** - this is a parameter between 0 and 1 that increases or reduces the % of similarity/likeness that the inputted search terms have to match to the updates data in the Change and Desc of Change attributes. This can only be used in the `/api/search` endpoint. Having a higher value should return more exact and less matches and having a lower value will return less exact but more matches, e.g `/api/search/Paris?likeness=0.5`, `/api/search/canton?likeness=0.9`. (**Default=1.0**)
* **sortBy** - this parameter allows you to sort the output results by publication date (Date Issued) or by the default country code. By default, the updates data will be returned alphabetically, according to ISO 3166 2 letter country code, but you can order by date. The parameter accepts two values: `countryCode` and `dateIssued`, by default the output is sorted by country code. This can be appended to all of the endpoints, e.g `/api/all?sortBy=dateIssued` `/api/year/2010-2015?sortBy=DATEISSUED`, `/api/date_range/2019-01-01?sortBy`. (**Default=countryCode**).
* **excludeMatchScore** - this parameter allows you to exclude the `matchScore`` attribute from the search results when using the `/api/search` endpoint. The match score is the % of a match each returned updates data object is to the search terms, with 100% being an exact match. By default the match score is returned for each object, e.g `/api/search/addition?excludeMatchScore=1`, `/api/search/New York?excludeMatchScore=1`. (**Default=0**).

Get all ISO 3166 updates for all countries and years
----------------------------------------------------
Return all the latest and historic ISO 3166 updates data for all available countries and publication years, using the ``/api/all`` endpoint.

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.vercel.app/api/"
    all_data = requests.get(base_url + "all").json()
    
    all_data["AD"] #updates data for Andorra
    all_data["DJ"] #updates data for Djibouti
    all_data["IE"] #updates data for Ireland
    all_data["PW"] #updates data for Palau

curl::
    
    $ curl -i https://iso3166-updates.vercel.app/api/all

Get all ISO 3166 updates for a country using its ISO 3166-1 alpha code (alpha-2, alpha-3, numeric)
--------------------------------------------------------------------------------------------------
Return all the latest and historic ISO 3166 updates data for 1 or more countries, using their ISO 3166-1 2 letter 
alpha-2, 3 letter alpha-3 or numeric country codes and the ``/api/alpha`` endpoint. The endpoint also accepts a  
comma separated list of multiple alpha country codes. 

For example, France (FR,FRA,250), Germany (DE,DEU,276) and Hungary (HU,HUN,348):

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.vercel.app/api/"

    #FR - France
    input_alpha = "FR" 
    fr_updates_data = requests.get(base_url + f'/alpha/{input_alpha}').json()
    fr_updates_data["FR"]

    #DEU - Germany
    input_alpha = "DEU"
    de_updates_data = requests.get(base_url + f'/alpha/{input_alpha}').json()
    de_updates_data["DE"] 

    #348 - Hungary
    hu_updates_data = "348" 
    hu_updates_data = requests.get(base_url + f'/alpha/{input_alpha}').json()
    hu_updates_data["HU"]

curl::

    $ curl -i https://iso3166-updates.vercel.app/api/alpha/FR
    $ curl -i https://iso3166-updates.vercel.app/api/alpha/DEU
    $ curl -i https://iso3166-updates.vercel.app/api/alpha/348
    $ curl -i https://iso3166-updates.vercel.app/api/alpha/FR,DEU,348

This endpoint can also be used in conjunction with the ``/api/year`` and ``/api/date_range`` endpoints.


.. Get all ISO 3166 updates for a country using its country name
.. -------------------------------------------------------------
.. Return all the latest and historic ISO 3166 updates data for 1 or more countries, using their ISO 3166-1 country name,
.. as it is most commonly known in English, and the ``/api/name`` endpoint. The endpoint also accepts a comma separated 
.. list of multiple country names.

.. For example, Tajikistan (TJ,TJK,762), Seychelles (SC,SYC,690) and Uganda (UG,UGA,800):

.. .. code-block:: python

..     import requests

..     base_url = "https://iso3166-updates.vercel.app/api/"

..     #Tajikistan 
..     input_name = "Tajikistan" 
..     tajikistan_updates_data = requests.get(base_url + f'name/{input_name}').json()
..     tajikistan_updates_data["TJ"] 
    
..     #Seychelles
..     input_name = "Seychelles" 
..     seychelles_updates_data = requests.get(base_url + f'name/{input_name}').json()
..     seychelles_updates_data["SC"] 

..     #Uganda
..     request_url = base_url + f"name/{input_name}"
..     uganda_updates_data = requests.get(base_url + f'name/{input_name}').json()
..     uganda_updates_data["UG"] 

.. curl

..     $ curl -i https://iso3166-updates.vercel.app/api/name/Tajikistan
..     $ curl -i https://iso3166-updates.vercel.app/api/name/Seychelles
..     $ curl -i https://iso3166-updates.vercel.app/api/name/Uganda
..     $ curl -i https://iso3166-updates.vercel.app/api/name/Tajikistan,Seychelles,Uganda

.. This endpoint can also be used in conjunction with the ``/api/year`` endpoint.


Get all ISO 3166 updates from a year or list of years
-----------------------------------------------------
Return all the ISO 3166 updates data that were published in a specific year or list of years, using the ``/api/year`` endpoint. 
The endpoint can also accept a comma separated list of years.

For example, 2004 and 2007:

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.vercel.app/api/"

    #2004
    input_year = "2004" 
    request_url = base_url + f"year/{input_year}"
    _2004_updates = requests.get(request_url).json()

    #2007
    input_year = "2007" 
    request_url = base_url + f"year/{input_year}"
    _2007_updates = requests.get(request_url).json()

    #2004,2007
    input_year = "2004,2007" 
    request_url = base_url + f"year/{input_year}"
    _2004_2007_updates = requests.get(request_url).json()

curl::

    $ curl -i https://iso3166-updates.vercel.app/api/year/2004
    $ curl -i https://iso3166-updates.vercel.app/api/year/2007
    $ curl -i https://iso3166-updates.vercel.app/api/year/2004,2007

Get all ISO 3166 updates from a year range
------------------------------------------
Return all the ISO 3166 updates data that were published within a specific year range, using the ``/api/year`` 
endpoint. Sort output by publication date (Date Issued) via ``sortBy`` query string parameter.

For example, 2009-2015 and 2001-2008:

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.vercel.app/api/"

    #2009-2015
    input_year = "2009-2015" 
    request_url = base_url + f"year/{input_year}"
    _2009_2015_updates = requests.get(request_url, params={"sortBy": "dateIssued"}).json()

    #2001-2008
    input_year = "2001-2008" 
    request_url = base_url + f"year/{input_year}"
    _2001_2008_updates = requests.get(request_url, params={"sortBy": "dateIssued"}).json()

curl::

    $ curl -i https://iso3166-updates.vercel.app/api/year/2009-2015?sortBy=dateIssued
    $ curl -i https://iso3166-updates.vercel.app/api/year/2001-2008?sortBy=dateIssued

Get all ISO 3166 updates greater than or less than a year
---------------------------------------------------------
Return all ISO 3166 updates that were published less than or greater than an input year 
using the ``/api/year`` endpoint, sort by publication date.

For example, <2010 and >2012:

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.vercel.app/api/"

    #<2010
    input_year = "<2010" 
    request_url = base_url + f"/year/{input_year}"
    lt_2010 = requests.get(request_url, params={"sortBy": "dateIssued"}).json()

    #>2012
    input_year = ">2012" 
    request_url = base_url + f"/year/{input_year}"
    gt_2012 = requests.get(request_url, params={"sortBy": "dateIssued"}).json()

curl::

    $ curl -i https://iso3166-updates.vercel.app/api/alpha/year/<2010
    $ curl -i https://iso3166-updates.vercel.app/api/alpha/year/>2012


Get all ISO 3166 updates, excluding a year or list of years
-----------------------------------------------------------
Return all ISO 3166 updates that exclude the input publication year or list of years using the
``/api/year`` endpoint.

For example, <>2020, <>2004

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.vercel.app/api/"

    #<>2020
    input_year = "<>2020" 
    request_url = base_url + f"/year/{input_year}"
    ne_2020 = requests.get(request_url).json()

    #<>2004
    input_year = "<>2004" 
    request_url = base_url + f"/year/{input_year}"
    ne_2004 = requests.get(request_url).json()

curl::

    $ curl -i https://iso3166-updates.vercel.app/api/alpha/year/<>2020
    $ curl -i https://iso3166-updates.vercel.app/api/alpha/year/<>2004


Get all ISO 3166 updates for a country and year
-----------------------------------------------
Return all ISO 3166 updates for an input country that were published in a year, list of years, year range,
greater than or less than a specified year or not equal to a yea/list of years, using the endpoint 
``/api/alpha/{input_alpha}/year/{input_year}`` or ``/api/year/{input_year}/alpha/{input_alpha}``.

For example, Andorra for 2007, Argentina for 2010, 2015, 2017, Bulgaria 2003-2008, Ecuador for <2019 and Japan <>2018:

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.vercel.app/api/"

    #Andorra - 2007
    input_alpha = "AD"
    input_year = "2007"

    request_url = base_url + f"alpha/{input_alpha}/year/{input_year}"
    ad_2007 = requests.get(request_url).json()

    #Argentina 2010, 2015, 2017
    input_alpha = "AR"
    input_year = "2010, 2015, 2017"

    request_url = base_url + f"alpha/{input_alpha}/year/{input_year}"
    ar_2010_2015_2017 = requests.get(request_url).json()

    #Bulgaria - 2003-2008
    input_alpha = "BG"
    input_year = "2003-2008"

    request_url = base_url + f"alpha/{input_alpha}/year/{input_year}"
    bg_2003_2008 = requests.get(request_url).json()

    #Ecuador - <2019
    input_alpha = "EC"
    input_year = "<2019"
    
    request_url = base_url + f"alpha/{input_alpha}/year/{input_year}"
    ec_lt_2019 = requests.get(request_url).json()

    #Japan - <>2018
    input_alpha = "JP"
    input_year = "<>2018"
    
    request_url = base_url + f"alpha/{input_alpha}/year/{input_year}"
    jp_ne_2018 = requests.get(request_url).json()

curl::

    $ curl -i https://iso3166-updates.vercel.app/api/alpha/AD/year/2007
    $ curl -i https://iso3166-updates.vercel.app/api/alpha/AR/year/2010,2015,2017
    $ curl -i https://iso3166-updates.vercel.app/api/alpha/BG/year/2003-2008
    $ curl -i https://iso3166-updates.vercel.app/api/alpha/EC/year/<2019
    $ curl -i https://iso3166-updates.vercel.app/api/alpha/JP/year/<>2018


Get all ISO 3166 updates for all countries from a specified date range, inclusive
---------------------------------------------------------------------------------
Return all available country's ISO 3166 updates data that were published within the specified date range, 
inclusively, using the ``/api/date_range`` endpoint.

For example, publication dates within the date range 2005-11-05 to 2007-08-09, and from 2018-05-05:

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.vercel.app/api/"

    #2005-11-05 to 2007-08-09:
    input_date_range = "2005-11-05,2007-08-09"
    request_url = base_url + f"date_range/{input_date_range}"
    date_range = requests.get(request_url).json()

    #2018-05-05
    input_date_range = "2018-05-05"
    request_url = base_url + f"date_range/{input_date_range}"
    date_range = requests.get(request_url).json()

curl::

    $ curl -i https://iso3166-updates.vercel.app/api/date_range/'2005-11-05,2007-08-09'
    $ curl -i https://iso3166-updates.vercel.app/api/date_range/2018-05-05



Search for specific keywords in ISO 3166 updates
------------------------------------------------
Return all available country's ISO 3166 updates data that have the inputted search terms in them, using the 
``/api/search`` endpoint. The query string parameter `likeness` can be used to return a more exact match or 
to increase the search space to return more approximate matches. Additionally, the query string parameter 
`excludeMatchScore` can be set to True to exlcude the match score from the search results, which shows the 
% match that the returned result is.

For example, searching for all updates that have "Parish" or "Canton" in them:

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.vercel.app/api/"

    #search for Parish, exact match
    input_search = "Parish"
    request_url = base_url + f"search/{input_search}"
    search_result = requests.get(request_url).json()

    #search for Canton, 80% match, exclude % match score
    input_search = "Canton"
    request_url = base_url + f"search/{input_search}"
    search_result = requests.get(request_url, params={"likeness": "0.8", "excludeMatchScore": "1"}).json()

curl::

    $ curl -i https://iso3166-updates.vercel.app/api/search/Parish
    $ curl -i https://iso3166-updates.vercel.app/api/search/Canton


.. note::
    A demo of the software and API is available `here <https://colab.research.google.com/drive/1btfEx23bgWdkUPiwdwlDqKkmUp1S-_7U?usp=sharing/>`_.