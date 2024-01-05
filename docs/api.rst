API 
====
The main API endpoint is:

`https://iso3166-updates.com/api <https://iso3166-updates.com/api/>`_. This endpoint displays the API documentation and forms the
base URL for the 5 other endpoints.

The other endpoints available in the API are:

* https://iso3166-updates.com/api/all
* https://iso3166-updates.com/api/alpha2/<input_alpha2>
* https://iso3166-updates.com/api/name/<input_name>
* https://iso3166-updates.com/api/year/<input_year>
* https://iso3166-updates.com/api/alpha2/<input_alpha2>/year/<input_year>
* https://iso3166-updates.com/api/name/<input_name>/year/<input_year>
* https://iso3166-updates.com/api/months/<input_month>
 
.. The paths/endpoints available in the API are - `/api/all`, `/api/alpha2`, `/api/name`, `/api/year` and `/api/months`.

.. * The `/api/all` path/endpoint returns all of the ISO 3166 updates/changes data for all countries.

.. * The 2 letter alpha-2 country code can be appended to the alpha2 path/endpoint e.g. `/api/alpha2/JP`. A single alpha-2 code or a list of them can be passed to the API e.g. `/api/alpha2/FR,DE,HU,ID,MA`. For redundancy, the 3 letter alpha-3 counterpart for each country's alpha-2 code can also be appened to the path e.g. `/api/alpha2/FRA,DEU,HUN,IDN,MAR`. The alpha2 endpoint can be used in conjunction with the year endpoint to get the country updates for a specific country and year, in the format `/api/alpha2/<input_alpha2>/year/<input_year>` or `/api/year/<input_year>/alpha2/<input_alpha2>`. If an invalid alpha-2 code is input then an error will be returned.

.. * The name parameter can be a country name as it is most commonly known in English, according to the ISO 3166-1. The name can similarly be appended to the name path/endpoint e.g. `/api/name/Denmark`. A single country name or list of them can be passed into the API e.g. `/api/name/France,Moldova,Benin`. A closeness function is used to get the most approximate available country from the one input, e.g. Sweden will be used if the input is `/api/name/Swede`. The name endpoint can be used in conjunction with the year endpoint to get the country updates for a specific country name and year, in the format `/api/name/<input_name>/year/<input_year>`. If no country is found from the closeness function or an invalid name is input then an error will be returned.

.. * The year parameter can be a specific year, year range, or a cut-off year to get updates less than/more than a year. The year value can be appended to the year path/endpoint e.g. `/api/year/2017`, `/api/year/2010-2015`, `/api/year/<2009`, `/api/year/>2002`. The year endpoint can be used in conjunction with the alpha2 and name endpoints to get the country updates for a specific country and year, in the format `/api/alpha2/<input_alpha2>/year/<input_year>` and `/api/name/<input_name>/year/<input_year>`, respectively. If an invalid year is input then an error will be returned.

.. * The months parameter will gather all updates for 1 or more countries from an input number of months from the present day. The month value can be appended to the months path/endpoint e.g. `/api/months/12`, `/api/months/24`. If an invalid month value is input then an error will be returned.

.. * The main API endpoint (`/` or `/api`) will return the homepage and API documentation.

Get all ISO 3166 updates
------------------------
Returning all available countrys' ISO 3166 updates data using the ``/all`` endpoint.

Python Requests:

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

Get all ISO 3166 updates for a specific country
-----------------------------------------------
Returning all of a country's ISO 3166 updates data using its country's 2 letter alpha-2 ISO 3166-1 code with the ``/alpha2`` endpoint, 
for example: FR, DE, HN. For redundancy, the country's 3 letter alpha-3 ISO 3166-1 code will also be accepted. You can also return multiple 
country's data by passing in a comma seperated list of country codes.

Python Requests:

.. code-block:: python

    import requests

    base_url = "https://www.iso3166-updates.com/api/"
    input_alpha2 = "FR" #DE, HN
    all_data = requests.get(base_url + f'/alpha2/{input_alpha2}').json()

    all_data["FR"] #updates data for France

curl::

    $ curl -i https://www.iso3166-updates.com/api/alpha2/FR
    $ curl -i https://www.iso3166-updates.com/api/alpha2/DE
    $ curl -i https://www.iso3166-updates.com/api/alpha2/HND


You can also search using a country's name, as it is commonly in English with the ``/name`` endpoint, for example: Tajikistan, Seychelles, Uganda.
Similarly, you can pass in a comma seperated list of country names.

Python Requests:

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.com/api/"
    input_name = "Tajikistan" #Seychelles, Uganda

    request_url = base_url + f"name/{input_name}"

    all_request = requests.get(request_url)
    all_request.json() 

curl::

    $ curl -i https://iso3166-updates.com/api/name/Tajikistan
    $ curl -i https://iso3166-updates.com/api/name/Seychelles
    $ curl -i https://iso3166-updates.com/api/name/Uganda

Get all ISO 3166 updates for a specific year
--------------------------------------------
Returning all available countrys' ISO 3166 updates data using the ``/year`` endpoint that have the same year as publication as the input year, for example: 2004, 2007.

Python Requests:

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.com/api/"
    input_year = "2004" #2007 

    request_url = base_url + f"year/{input_year}"

    all_request = requests.get(request_url)
    all_request.json() 

curl::

    $ curl -i https://iso3166-updates.com/api/year/2004
    $ curl -i https://iso3166-updates.com/api/year/2007

Get all ISO 3166 updates for a specific country and year
--------------------------------------------------------
Return all ISO 3166 updates for an input country that were published on the input year using the ``/alpha2/{input_alpha2}/year/{input_year}`` endpoint, for example: Andorra, Dominica for 2007.

Python Requests:

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.com/api/"
    input_alpha2 = "AD" #DM
    input_year = "2007"

    request_url = base_url + f"alpha2/{input_alpha2}/year/{input_year}"

    all_request = requests.get(request_url)
    all_request.json() 

curl::

    $ curl -i https://iso3166-updates.com/api/alpha2/AD/year/2007
    $ curl -i https://iso3166-updates.com/api/alpha2/DM/year/2007

Get all ISO 3166 updates for a specific country in a specified year range
-------------------------------------------------------------------------
Return all ISO 3166 updates for an input country that were published within an input year range using the ``/alpha2/{input_alpha2}/year/{input_year}`` endpoint, for example: Bosnia, Haiti for 2009-2015.

Python Requests:

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.com/api/"
    input_name = "Bosnia" #Haiti
    input_year = "2009-2015"

    request_url = base_url + f"name/{input_name}/year/{input_year}"

    all_request = requests.get(request_url)
    all_request.json()

curl::

    $ curl -i https://iso3166-updates.com/api/name/Bosnia/year/2009-2015
    $ curl -i https://iso3166-updates.com/api/name/haiti/year/2009-2015

Get all ISO 3166 updates for a specific country less than/greater than a year
-----------------------------------------------------------------------------
Return all ISO 3166 updates for an input country that were published less than or greater than an input year using the ``/alpha2/{input_alpha2}/year/{input_year}`` endpoint, for example: Israel, Lithuania <2010 or >2012.

Python Requests:

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.com/api/"
    input_alpha2 = "IL" #LT
    input_year = ">2012"

    request_url = base_url + f"alpha2/{input_alpha2}/year/{input_year}"

    all_request = requests.get(request_url)
    all_request.json() 

curl::

    $ curl -i https://iso3166-updates.com/api/alpha2/IL/year/<2010
    $ curl -i https://iso3166-updates.com/api/alpha2/IL/year/>2012


Get all ISO 3166 updates for all countries, from the previous months
--------------------------------------------------------------------
Returning all available countrys' ISO 3166 updates data that were published within the previous input month range using the ``/months`` endpoint, for example: the past 3 or 6 months.

Python Requests:

.. code-block:: python

    import requests

    base_url = "https://iso3166-updates.com/api/"
    input_month = "3" #6

    request_url = base_url + f"months/{input_month}"

    all_request = requests.get(request_url)
    all_request.json() 

curl::

    $ curl -i https://iso3166-updates.com/api/months/3
    $ curl -i https://iso3166-updates.com/api/months/6

.. note::
    A demo of the software and API is available `here <https://colab.research.google.com/drive/1btfEx23bgWdkUPiwdwlDqKkmUp1S-_7U?usp=sharing/>`_.