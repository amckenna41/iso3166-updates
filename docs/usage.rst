Usage
=====

.. _installation:

Installation
------------

To use **iso3166-updates**, firstly install via ``pip``:

.. code-block:: console

   pip install iso3166-updates

Get all ISO 3166 updates for all countries and years
----------------------------------------------------
Return all the latest and historic ISO 3166 updates data for all available countries and publication years. You will need to firstly create an instance of the ``ISO3166_Updates`` class and
then access the ``all`` attribute object instance. You can then access an individual country's ISO 3166 updates data by passing in the sought ISO 3166-1 2 letter alpha-2, 
3 letter alpha-3 or numeric country code.

.. code-block:: python

   from iso3166_updates import *

   #create instance of ISO3166_Updates class
   iso = ISO3166_Updates()
   
   #get all data from 'all' attribute of class
   all_updates_data = iso.all

   all_updates_data["AD"] #all updates data for Andorra
   all_updates_data["DZ"] #all updates data for Algeria
   all_updates_data["TUV"] #all updates data for Tuvalu
   all_updates_data["YEM"] #all updates data for Yemen
   all_updates_data["704"] #all updates data for Vietnam


Get all ISO 3166 updates for a country using its ISO 3166-1 alpha code (alpha-2, alpha-3, numeric)
--------------------------------------------------------------------------------------------------
Return all the latest and historic ISO 3166 updates data for 1 or more countries, using the country's ISO 3166-1 alpha-2, alpha-3 or numeric codes. 
You firstly need to create an instance of the ``ISO3166_Updates`` class and then pass in the sought ISO 3166-1 codes. You can also return multiple 
country's data by passing in a comma separated list of country codes.

For example, Egypt (EG, EGY, 818), Jordan (JO, JOR, 400) and Bosnia (BA, BIH, 070):

.. code-block:: python

   from iso3166_updates import *

   #create instance of ISO3166_Updates class
   iso = ISO3166_Updates()

   eg_updates = iso["EG"] #EGY, 818
   jo_updates = iso["JOR"] #JO, 400
   ba_updates = iso["070"] #BA, BIH
   
   #all of the above updates can be returned to the same variable
   eg_jo_ba_updates = iso["EG, JOR, 070"]

You can also pass in the sought country code or country codes to the object instantiation using the ``country_code`` input parameter, if only their updates 
are required from the dataset. This allows for memory to be saved and for all updates data to not be unnecessarily imported on object initialisation. 

For example, if only Sao Tome & Principe's (ST, STP, 678) updates data is needed:

.. code-block:: python

   from iso3166_updates import *

   #create instance of ISO3166_Updates class
   iso_st = ISO3166_Updates(country_code="ST")
   

Get all ISO 3166 updates from a year or list of years
-----------------------------------------------------
Return all the ISO 3166 updates data from a specific year or list of years, using the ``year()`` function within an object instance of 
the ``ISO3166_Updates`` class, passing in the required years as parameters.

For example, 2009 and (2001,2004,2019):

.. code-block:: python

   from iso3166_updates import *

   #create instance of ISO3166_Updates class
   iso = ISO3166_Updates()

   #get all updates for 2009
   iso.year("2009")

   #get all updates for 2001, 2004, 2019
   iso.year("2001, 2004, 2019")


Get all ISO 3166 updates from a year range
------------------------------------------
Return all the ISO 3166 updates data from a specific year range, using the ``year()`` function within an object instance of 
the ``ISO3166_Updates`` class, passing in the required year range as parameter.

For example, 2010-2015 and 2001-2005:

.. code-block:: python

   from iso3166_updates import *

   #create instance of ISO3166_Updates class
   iso = ISO3166_Updates()

   #get all updates between 2010-2015
   iso.year("2010-2015")

   #get all updates between 2001-2005
   iso.year("2001-2005")


Get all ISO 3166 updates greater than or less than a year
---------------------------------------------------------
Return all the ISO 3166 updates data that are greater than or less than a specific year, using the ``year()`` function
within an object instance of the ``ISO3166_Updates`` class, passing in the required year as parameter.

For example, <2020 and >2022:

.. code-block:: python

   from iso3166_updates import *

   #create instance of ISO3166_Updates class
   iso = ISO3166_Updates()
   
   #get all updates with year less than 2020
   iso.year("<2020")

   #get all updates with year greater than or equal to 2022
   iso.year(">2022")


Get all ISO 3166 updates from the previous number of months or month range
--------------------------------------------------------------------------
Return all the ISO 3166 updates data published over the past number of months or over a specified month range, using the ``months()`` function
within an object instance of the ``ISO3166_Updates`` class, passing in the required months or month range as parameters.

For example, 12 and 36-48 months:

.. code-block:: python

   from iso3166_updates import *

   #create instance of ISO3166_Updates class
   iso = ISO3166_Updates()

   #get all updates from the past 12 months
   iso.months("12")

   #get all updates from the past 36-48 months
   iso.months("36-48")

.. Get any ISO 3166 updates for a country, using its ISO 3166-1 alpha code (alpha2, alpha-3, numeric), and year
.. -------------------------------------------------------------------------------------------------------------------
.. Return all the ISO 3166 updates data for 1 or more countries for a year, list of years, year range or greater than or less than a year. Firstly, you need to 
.. create an object instance of the ``ISO3166_Updates`` class. You can then pass in the required year's value to the ``year()`` function and then pass in the 
.. sought ISO 3166-1 2 letter alpha-2, 3 letter alpha-3 or numeric country codes to the object output of the function.

.. .. code-block:: python

..    from iso3166_updates import *

..    #get all Hungarian (HU) ISO 3166 data from 2010
..    iso.year("2010").HU
   
..    #get all Finnish (FI) ISO 3166 data in years 2011, 2014, 2022
..    iso.year("2011,2014,2022").FI

..    #get all Tanzanian (TA) ISO 3166 data after 2015, inclusive
..    iso.year(">2015").TA

..    #get all Irish (IE) ISO 3166 data between 2012 and 2021, inclusive
..    iso.year("2012-2021").IE

..    #get all Romanian (RO) ISO 3166 data before 2007
..    iso.year("<2007").RO