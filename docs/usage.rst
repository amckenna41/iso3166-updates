Usage
=====

.. _installation:

Installation
------------

To use **iso3166-updates**, firstly install via ``pip``:

.. code-block:: console

   pip install iso3166-updates

Alternatively, you can clone the repo and run ``setup.py``:

.. code-block:: console

   git clone -b master https://github.com/amckenna41/iso3166-updates.git
   cd iso3166_updates
   python3 setup.py install

Get all ISO 3166 updates for all countries and years
----------------------------------------------------
To access ALL the latest and historic ISO 3166 updates data for ALL available countries, you need to access the ``all`` attribute within the ``updates`` 
object instance of the ``ISO3166_Updates`` class. You can then access an individual country's ISO 3166 updates data by passing in the sought 2 
letter alpha-2 or 3 letter alpha-3 country code.

.. code-block:: python

   import iso3166_updates as iso

   all_updates_data = iso.updates.all

   all_updates_data["AD"] #all updates data for Andorra
   all_updates_data["DZ"] #all updates data for Algeria
   all_updates_data["TUV"] #all updates data for Tuvalu
   all_updates_data["YEM"] #all updates data for Yemen


Get all ISO 3166 updates for specific country
----------------------------------------------
To access ALL the latest and historic ISO 3166 updates data for 1 or more countries, you need to access the ``updates`` object instance of the ``ISO3166_Updates`` 
class. You can then access an individual country's ISO 3166 updates data by passing in the sought 2 letter alpha-2 or 3 letter alpha-3 country code. To return
the updates of multiple countries you can pass in a comma seperated list of alpha-2 or 3 letter alpha-3 country codes.

.. code-block:: python

   import iso3166_updates as iso

   denmark_updates = iso.updates["DK"]
   italy_updates = iso.updates["IT"]
   new_zealand_updates = iso.updates["NZ"]

   jordan_kuwait_updates = iso.updates["JO,KW"]
   bosnia_germany_france_hungary_paraguay iso.updates["BA,DE,FR,HU,PY"]

Get any ISO 3166 updates from specific year
-------------------------------------------
To access the ISO 3166 updates data for a specific year, list of years, year range or greater than/less than a year, you need to access the ``updates`` 
object instance of the ``ISO3166_Updates`` class and then pass in the required years to the ``year()`` function. 

.. code-block:: python

   import iso3166_updates as iso

   #get all updates for 2009
   iso.updates.year("2009")

   #get all updates for 2001, 2004, 2019
   iso.updates.year("2001, 2004, 2019")

   #get all updates between 2010-2015
   iso.updates.year("2010-2015")
   
   #get all updates with year less than 2020
   iso.updates.year("<2020")

   #get all updates with year greater than or equal to 2022
   iso.updates.year(">2022")


Get any ISO 3166 updates for specific country and year
-------------------------------------------------------
To access the ISO 3166 updates data for 1 or more countries for a specific year, list of years, year range or greater than/less than a year, you 
need to access the ``updates`` object instance of the ``ISO3166_Updates`` class and then pass in the required years to the ``year()`` function. You can 
access the individual updates data for a select country via dot notation on the function output.

.. code-block:: python

   import iso3166_updates as iso

   #get all Hungarian (HU) ISO 3166 data from 2010
   iso.updates.year("2010").HU
   
   #get all Finnish (FI) ISO 3166 data in years 2011, 2014, 2022
   iso.updates.year("2011,2014,2022").FI

   #get all Tanzanian (TA) ISO 3166 data after 2015, inclusive
   iso.updates.year(">2015").TA

   #get all Irish (IE) ISO 3166 data between 2012 and 2021, inclusive
   iso.updates.year("2012-2021").IE

   #get all Romanian (RO) ISO 3166 data before 2007
   iso.updates.year("<2007").RO