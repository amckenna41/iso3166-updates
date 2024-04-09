API 
====
The main API endpoint displays the API documentation and forms the base URL for the 5 other endpoints: |api_main_endpoint|

.. |api_main_endpoint| raw:: html

   <a href="https://iso3166-updates.com/api" target="_blank">https://iso3166-updates.com/api</a>

The other endpoints available in the API are:

* https://iso3166-updates.com/api/all
* https://iso3166-updates.com/api/alpha/<input_alpha>
* https://iso3166-updates.com/api/name/<input_name>
* https://iso3166-updates.com/api/year/<input_year>
* https://iso3166-updates.com/api/alpha/<input_alpha>/year/<input_year>
* https://iso3166-updates.com/api/name/<input_name>/year/<input_year>
* https://iso3166-updates.com/api/months/<input_month>
* https://iso3166-updates.com/api/months/<input_month>/alpha/<input_alpha>

Below are some example usage of the API and the above endpoints, utilising the **Python Requests** library.
 
.. The paths/endpoints available in the API are - `/api/all`, `/api/alpha`, `/api/name`, `/api/year` and `/api/months`.

.. * The `/api/all` path/endpoint returns all of the ISO 3166 updates/changes data for all countries.

.. * The ISO 3166-1 2 letter alpha-2, 3 letter alpha-3 or numeric country codes can be appended to the alpha path/endpoint e.g., `/api/alpha/JP`. A single alpha code or a comma separated list of them can be passed to the API e.g., `/api/alpha/FR,DEU,HUN,360`. The alpha endpoint can be used in conjunction with the year endpoint to get the country updates for a country and year, in the format `/api/alpha/<input_alpha>/year/<input_year>` or `/api/year/<input_year>/alpha/<input_alpha>`. If an invalid alpha code is input then an error will be returned.

.. * The name parameter can be a country name as it is most commonly known in English, according to the ISO 3166-1. The name can similarly be appended to the name path/endpoint e.g., `/api/name/Denmark`. A single country name or list of them can be passed into the API e.g., `/api/name/France,Moldova,Benin`. A closeness function is used to get the most approximate available country from the one input, e.g., Sweden will be used if the input is `/api/name/Swede`. The name endpoint can be used in conjunction with the year endpoint to get the country updates for a specific country name and year, in the format `/api/name/<input_name>/year/<input_year>`. If no country is found from the closeness function or an invalid name is input then an error will be returned.

.. * The year parameter can be a year, year range, or a cut-off year to get updates less than/more than a year. The year value can be appended to the year path/endpoint e.g., `/api/year/2017`, `/api/year/2010-2015`, `/api/year/<2009`, `/api/year/>2002`. The year endpoint can be used in conjunction with the alpha and name endpoints to get the country updates for a country and year, in the format `/api/alpha/<input_alpha>/year/<input_year>` and `/api/name/<input_name>/year/<input_year>`, respectively. If an invalid year is input then an error will be returned.

.. * The months parameter will gather all updates for 1 or more countries from an input number of months from the present day. The month value can be appended to the months path/endpoint e.g., `/api/months/12`, `/api/months/24`. If an invalid month value is input then an error will be returned.

.. * The main API endpoint (`/` or `/api`) will return the homepage and API documentation.

Get all ISO 3166 updates for all countries and years
----------------------------------------------------
Return all the latest and historic ISO 3166 updates data for all available countries and publication years, using the ``/api/all`` endpoint.

.. code-block:: python

    import requests

    base_url = "https://www.iso3166-updates.com/api/"
    all_data = requests.get(base_url + "all").json()
    
    all_data["AD"] #updates data for Andorra
    all_data["DJ"] #updates data for Djibouti
    all_data["IE"] #updates data for Ireland
    all_data["PW"] #updates data for Palau

curl::
    
    $ curl -i https://www.iso3166-updates.com/api/all

Get all ISO 3166 updates for a country using its ISO 3166-1 alpha code (alpha-2, alpha-3, numeric)
--------------------------------------------------------------------------------------------------
Return all the latest and historic ISO 3166 updates data for 1 or more countries, using their ISO 3166-1 2 letter 
alpha-2, 3 letter alpha-3 or numeric country codes and the ``/api/alpha`` endpoint. The endpoint also accepts a  
comma separated list of multiple alpha country codes. 

For example, France (FR,FRA,250), Germany (DE,DEU,276) and Hungary (HU,HUN,348):

.. code-block:: python

    import requests

    base_url = "https://www.iso3166-updates.com/api/"

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

    $ curl -i https://www.iso3166-updates.com/api/alpha/FR
    $ curl -i https://www.iso3166-updates.com/api/alpha/DEU
    $ curl -i https://www.iso3166-updates.com/api/alpha/348
    $ curl -i https://www.iso3166-updates.com/api/alpha/FR,DEU,348

This endpoint can also be used in conjunction with the ``/api/year`` and ``/api/months`` endpoints.


Get all ISO 3166 updates for a country using its country name
-------------------------------------------------------------
Return all the latest and historic ISO 3166 updates data for 1 or more countries, using their ISO 3166-1 country name,
as it is most commonly known in English, and the ``/api/name`` endpoint. The endpoint also accepts a comma separated 
list of multiple country names.

For example, Tajikistan (TJ,TJK,762), Seychelles (SC,SYC,690) and Uganda (UG,UGA,800):

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.com/api/"

    #Tajikistan 
    input_name = "Tajikistan" 
    tajikistan_updates_data = requests.get(base_url + f'name/{input_name}').json()
    tajikistan_updates_data["TJ"] 
    
    #Seychelles
    input_name = "Seychelles" 
    seychelles_updates_data = requests.get(base_url + f'name/{input_name}').json()
    seychelles_updates_data["SC"] 

    #Uganda
    request_url = base_url + f"name/{input_name}"
    uganda_updates_data = requests.get(base_url + f'name/{input_name}').json()
    uganda_updates_data["UG"] 

curl::

    $ curl -i https://iso3166-updates.com/api/name/Tajikistan
    $ curl -i https://iso3166-updates.com/api/name/Seychelles
    $ curl -i https://iso3166-updates.com/api/name/Uganda
    $ curl -i https://iso3166-updates.com/api/name/Tajikistan,Seychelles,Uganda

Get all ISO 3166 updates from a year or list of years
-----------------------------------------------------
Return all the ISO 3166 updates data that were published in a specific year or list of years, using the ``/api/year`` endpoint. 
The endpoint can also accept a comma separated list of years.

For example, 2004 and 2007:

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.com/api/"

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

    $ curl -i https://iso3166-updates.com/api/year/2004
    $ curl -i https://iso3166-updates.com/api/year/2007
    $ curl -i https://iso3166-updates.com/api/year/2004,2007

Get all ISO 3166 updates from a year range
------------------------------------------
Return all the ISO 3166 updates data that were published within a specific year range, using the ``/api/year`` 
endpoint.

For example, 2009-2015 and 2001-2008:

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.com/api/"

    #2009-2015
    input_year = "2009-2015" 
    request_url = base_url + f"year/{input_year}"
    _2009_2015_updates = requests.get(request_url).json()

    #2001-2008
    input_year = "2001-2008" 
    request_url = base_url + f"year/{input_year}"
    _2001_2008_updates = requests.get(request_url).json()

curl::

    $ curl -i https://iso3166-updates.com/api/year/2009-2015
    $ curl -i https://iso3166-updates.com/api/year/2001-2008

Get all ISO 3166 updates greater than or less than a year
---------------------------------------------------------
Return all ISO 3166 updates for an input country that were published less than or greater than an input year 
using the ``/api/year`` endpoint.

For example, <2010 and >2012:

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.com/api/"

    #<2010
    input_year = "<2010" 
    request_url = base_url + f"/year/{input_year}"
    lt_2010 = requests.get(request_url).json()

    #>2012
    input_year = ">2012" 
    request_url = base_url + f"/year/{input_year}"
    gt_2012 = requests.get(request_url).json()

curl::

    $ curl -i https://iso3166-updates.com/api/alpha/year/<2010
    $ curl -i https://iso3166-updates.com/api/alpha/year/>2012

Get all ISO 3166 updates for a country and year, list of years, year range or greater than or less than a year
--------------------------------------------------------------------------------------------------------------
Return all ISO 3166 updates for an input country that were published in a year, list of years, year range or
greater than or less than a specified year, using the endpoint ``/api/alpha/{input_alpha}/year/{input_year}`` or
``/api/year/{input_year}/alpha/{input_alpha}``.

For example, Andorra for 2007, Argentina for 2010, 2015, 2017, Bulgaria 2003-2008 and Ecuador for <2019:

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.com/api/"

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

curl::

    $ curl -i https://iso3166-updates.com/api/alpha/AD/year/2007
    $ curl -i https://iso3166-updates.com/api/alpha/AR/year/2010,2015,2017
    $ curl -i https://iso3166-updates.com/api/alpha/BG/year/2003-2008
    $ curl -i https://iso3166-updates.com/api/alpha/EC/year/<2019


Get all ISO 3166 updates for all countries from the previous months or month range
----------------------------------------------------------------------------------
Returning all available country's ISO 3166 updates data that were published within the previous input number of 
months or within a specified month range using the ``/api/months`` endpoint.

For example, publication dates within the past 6 months or within the past 60-72 months:

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.com/api/"

    #past 6 months
    input_month = "6"
    request_url = base_url + f"months/{input_month}"
    months_6 = requests.get(request_url).json()

    #past 60-72 months
    input_month = "60-72"
    request_url = base_url + f"months/{input_month}"
    months_60_72 = requests.get(request_url).json()

curl::

    $ curl -i https://iso3166-updates.com/api/months/6
    $ curl -i https://iso3166-updates.com/api/months/60-72


Get all ISO 3166 updates for a country from the previous months or month range
------------------------------------------------------------------------------
Returning all ISO 3166 updates data for a specific country or list of countries that were published 
within the previous input number of months or within a specified month range using the ``/api/months`` endpoint.

For example, publication dates within the past 9 months or within the past 12-36 months, for GR and IE:

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.com/api/"

    #past 9 months for Greece
    input_month = "9" 
    input_alpha = "GR"

    request_url = base_url + f"months/{input_month}/alpha/{input_alpha}"
    gr_9_months = requests.get(request_url).json()

    #past 12-36 months for Ireland
    input_month = "12-36" 
    input_alpha = "GR"

    request_url = base_url + f"months/{input_month}"
    ie_12_36_months = requests.get(request_url).json()

curl::

    $ curl -i https://iso3166-updates.com/api/months/9/alpha/GR
    $ curl -i https://iso3166-updates.com/api/alpha/ie/months/12-36


.. note::
    A demo of the software and API is available `here <https://colab.research.google.com/drive/1btfEx23bgWdkUPiwdwlDqKkmUp1S-_7U?usp=sharing/>`_.