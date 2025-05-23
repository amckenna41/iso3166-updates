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
Return all the latest and historic ISO 3166 updates data for all available countries and publication years. You will need to firstly create an instance of the ``Updates`` class and
then access the ``all`` attribute object instance. You can then access an individual country's ISO 3166 updates data by passing in the sought ISO 3166-1 2 letter alpha-2, 
3 letter alpha-3 or numeric country code.

.. code-block:: python

   from iso3166_updates import *

   #create instance of Updates class
   iso = Updates()
   
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
You firstly need to create an instance of the ``Updates`` class and then pass in the sought ISO 3166-1 codes. You can also return multiple 
country's data by passing in a comma separated list of country codes.

For example, Egypt (EG, EGY, 818), Jordan (JO, JOR, 400) and Bosnia & Herz (BA, BIH, 070):

.. code-block:: python

   from iso3166_updates import *

   #create instance of Updates class
   iso = Updates()

   eg_updates = iso["EG"] #EGY, 818
   jo_updates = iso["JOR"] #JO, 400
   ba_updates = iso["070"] #BA, BIH
   
   #all of the above updates can be returned to the same variable
   eg_jo_ba_updates = iso["EG, JOR, 070"]

You can also pass in the sought country code or country codes to the object instantiation using the ``country_code`` input parameter, if only their updates 
are required from the dataset. This allows for memory to be saved and for all updates data to not be unnecessarily imported on object instantiation. 

For example, if only Sao Tome & Principe's (ST, STP, 678) updates data is needed:

.. code-block:: python

   from iso3166_updates import *

   #create instance of Updates class
   iso_st = Updates(country_code="ST")
   

Get all ISO 3166 updates from a year or list of years
-----------------------------------------------------
Return all the ISO 3166 updates data from a specific year or list of years, using the ``year()`` function within an object instance of 
the ``Updates`` class, passing in the required years as parameters.

For example, 2009 and (2001,2004,2019):

.. code-block:: python

   from iso3166_updates import *

   #create instance of Updates class
   iso = Updates()

   #get all updates for 2009
   iso.year("2009")

   #get all updates for 2001, 2004, 2019
   iso.year("2001, 2004, 2019")


Get all ISO 3166 updates from a year range
------------------------------------------
Return all the ISO 3166 updates data from a specific year range, using the ``year()`` function within an object instance of 
the ``Updates`` class, passing in the required year range as parameter.

For example, 2010-2015 and 2001-2005:

.. code-block:: python

   from iso3166_updates import *

   #create instance of Updates class
   iso = Updates()

   #get all updates between 2010-2015
   iso.year("2010-2015")

   #get all updates between 2001-2005
   iso.year("2001-2005")


Get all ISO 3166 updates greater than or less than a year
---------------------------------------------------------
Return all the ISO 3166 updates data that are greater than or less than a specific year, using the ``year()`` function
within an object instance of the ``Updates`` class, passing in the required year as parameters.

For example, <2020 and >2022:

.. code-block:: python

   from iso3166_updates import *

   #create instance of Updates class
   iso = Updates()
   
   #get all updates with year less than 2020
   iso.year("<2020")

   #get all updates with year greater than or equal to 2022
   iso.year(">2022")

Get all ISO 3166 updates excluding a year or list of years
----------------------------------------------------------
Return all the ISO 3166 updates data but excluding data with a specified publication year or list of years, using the ``year()`` function
within an object instance of the ``Updates`` class, passing in the required years as parameters.

For example, <>2004 and <>2019:

.. code-block:: python

   from iso3166_updates import *

   #create instance of Updates class
   iso = Updates()
   
   #get all updates, excluding publication year 2004
   iso.year("<>2004")

   #get all updates, excluding publication year 2019
   iso.year("<>2019")

   #get all updates, excluding both publication years 2004 and 2019
   iso.year("<>>2004,2019")


Get all ISO 3166 updates from a specific date range
---------------------------------------------------
Return all the ISO 3166 updates data published within a specified date range, inclusive, using the ``date_range()`` function
within an object instance of the ``Updates`` class, passing in the required date range range as parameter. You can also sort
the output by publication date via the ``sort_by_date`` parameter. The accepted values are dateDesc and dateAsc which will
sort the outputs date descending and ascending, respectively.

For example, 2012-04-15 to 2013-11-11:

.. code-block:: python

   from iso3166_updates import *

   #create instance of Updates class
   iso = Updates()

   #get all updates within specified date range, inclusive
   iso.date_range("2012-04-15,2013-11-11")

   #get all updates from specified date range, inclusive, sort by Date Issued rather than default Country Code, can be sorted descending or ascending 
   iso.date_range("12/04/2015,07/05/2010", sort_by_date="dateDesc")

   #get all updates from specified date, inclusive
   iso.date_range("2012-04-15")


Search for all ISO 3166 updates that have specific keywords
-----------------------------------------------------------
Return all the ISO 3166 updates data who's changes/description of change attributes feature the inputted search terms, using the ``search()`` 
function within an object instance of the ``Updates`` class, passing in the required search terms as parameters. The function also accepts
the ``likeness_score`` parameter which sets a % of likeness that the input search term can be to the matching updates, by default a likeness 
of 100 (an exact match) is used. If a date is explicitly input to the search function, the Date Issued column will additionally be added to 
the search space. The outputs from the search are ordered by ``match_score``, highest match first. This score can be excluded from the output 
by setting the ``exclude_match_score`` to 1, meaning the outputs will be ordered alphabetically by country code.

For example, Paris, RU-PSK or addition/deletion:

.. code-block:: python

   from iso3166_updates import *

   #create instance of Updates class
   iso = Updates()

   #search for any update objects that have Paris in them
   iso.search("Paris")

   #search for any update objects that have RU-PSK in them
   iso.search("RU-PSK")

   #search for any update objects that have addition or deletion in them, reduce % likeness score to 80
   iso.search("addition, deletion", likeness_score=80)

   #search for any update objects that have the date 2023-11-23, exclude the % match score from output
   iso.search("2023-11-23", exclude_match_score=1)


Add custom ISO 3166 updates
---------------------------
Add or delete a custom change/update to an existing country in the main iso3166-updates.json object. Custom updates can be used for in-house/bespoke 
applications that are using the **iso3166-updates** software but require additional custom changes/updates to be included. When adding a new update, the 
"Change" and "Date Issued" attributes are required with the "Description of Change" and "Source" attributes being optional. If the input custom 
change/update already exists then an error will be raised, otherwise it will be appended to the main object.
  
If the added change/update is required to be deleted from the object, then you can call the same function with the "Change" and "Date Issued" 
parameters/attributes of the added change/update, but also setting the 'delete' parameter to 1/True. You can also uninstall and reinstall to reset the main object.

*Note that this is a destructive yet temporary functionality. Adding a new custom change/update will make the dataset out of sync with the official 
ISO 3166 Updates data, therefore it is the user's responsibility to keep track of any custom changes/updates and delete them when necessary.*

For example, adding custom Kenyan and Belfast updates:

.. code-block:: python

   from iso3166_updates import *

   #create instance of Updates class
   iso = Updates()

   #adding custom update object for Kenya
   iso.custom_update(alpha_code="KE", change="New subdivision added", date_issued="2025-01-01", description_of_change="big ole description")

   #adding custom update object for Belfast
   iso.custom_update("IE", change="Brand new Belfast subdivision", date_issued="2020-05-12", description_of_change="", source="https:...")


If you need to remove the custom updates you can set the ``delete`` parameter in the same function to True, e.g custom Kenyan and Belfast updates:

.. code-block:: python

   from iso3166_updates import *

   #create instance of Updates class
   iso = Updates()

   #deleting custom update object for Kenya
   iso.custom_update(alpha_code="KE", change="New subdivision added", date_issued="2025-01-01", delete=1)

   #deleting custom update object for Belfast
   iso.custom_update("IE", change="Brand new Belfast subdivision", date_issued="2020-05-12", delete=1)


Get all ISO 3166 updates using a custom updates object
------------------------------------------------------
Return all the latest and historic ISO 3166 updates data for all available countries and publication years, using a custom updates object specified
by the updates_filepath class parameter. The custom object should be in the same format and structure as the original updates object.  You can 
firstly create an instance of the ``Updates`` class, passing in the desired filepath and then access the ``all`` attribute object instance. You can 
then access an individual country's ISO 3166 updates data by passing in the sought ISO 3166-1 2 letter alpha-2, 3 letter alpha-3 or numeric country code.

.. code-block:: python

   from iso3166_updates import *

   #create instance of Updates class
   iso = Updates(custom_updates_filepath="custom_filepath.json")
   
   #get all data from 'all' attribute of class
   all_updates_data = iso.all

   all_updates_data["AD"] #all updates data for Andorra
   all_updates_data["DZ"] #all updates data for Algeria
   all_updates_data["TUV"] #all updates data for Tuvalu
   all_updates_data["YEM"] #all updates data for Yemen
   all_updates_data["704"] #all updates data for Vietnam


Get the total number of ISO 3166 updates 
----------------------------------------
Return the total number of individual ISO 3166 updates objects within the imported JSON of the class, via the in-built ``len()`` function.

.. code-block:: python

   from iso3166_updates import *

   #create instance of Updates class
   iso = Updates()

   #get total number of updates object via len()
   len(iso)


Check for the latest ISO 3166 updates from repository
-----------------------------------------------------
Check for the latest updates data from the repository in comparison to the current object in the software. This is to ensure that the version of the software
you are using is up-to-date with the latest data. The function will return what changes, if any, need to be incorporated into your current object. If there
are any changes, it's recommended to upgrade to the latest version of the software. 

.. code-block:: python

   from iso3166_updates import *

   #create instance of Updates class
   iso = Updates()

   #compares local dataset with the latest version in the repository
   iso.check_for_updates()


.. note::
    A demo of the software and API is available `here <https://colab.research.google.com/drive/1oGF3j3_9b_g2qAmBtv3n-xO2GzTYRJjf?usp=sharing>`_.