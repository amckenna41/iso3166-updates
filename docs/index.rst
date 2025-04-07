Welcome to ISO 3166 Update's documentation 🌎!
==============================================

.. image:: https://upload.wikimedia.org/wikipedia/commons/3/3d/Flag-map_of_the_world_%282017%29.png

**iso3166-updates** is a software and accompanying API that consists of a series of scripts that check for any updates/changes 
to the ISO 3166 country codes and subdivision naming conventions, as per the ISO 3166 newsletter (https://www.iso.org/iso-3166-country-codes.html) 
and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui). 

The ISO 3166 standard by the ISO (International Organization for Standardisation) defines codes for the names of countries, dependent territories, 
special areas of geographical interest, consolidated into the ISO 3166-1 standard, and their principal subdivisions (e.g. provinces, states, 
departments, regions), which comprise the ISO 3166-2 standard. The ISO 3166-1 was first published in 1974 and currently comprises 249 countries, 
193 of which are sovereign states that are members of the United Nations 🇺🇳. The ISO 3166-2 was first published in 1998 and as of November 2023 
there are **5,039** codes defined in it.

The ISO is a very dynamic organisation and they regularly change, update and or remove entries within its library of standards, including the ISO 3166. 
Additions, changes and deletions to country/territorial codes occur less often in the ISO 3166-1, but changes are more frequent for the ISO 3166-2 
codes due to there being thousands more entries, thus it can be difficult to keep up with and track these changes. These changes can occur for a 
variety of geopolitical and administrative reasons. Previously these changes were communicated via newsletters; but as of July 2013 these changes 
are now communicated via their online catalogue/Online Browsing Platform (OBP), or via a database, which usually costs money to subscribe to (>$300!). 
Usually these updates are conveyed at the end of the year, with amendments and updates occasionally published at various times throughout the year.

This software and accompanying API make it extremely easy to check for any new or historic updates to a country or set of country's ISO 3166-2 
codes for free; with an easy-to-use interface via a Python package and API, ensuring that you get the most **up-to-date** and **accurate** ISO 3166-2 codes 
and naming conventions.

Each ISO 3166 update entry has 4 main data attributes:

* *Change*: overall summary of change/update made.
* *Description of Change*: more in-depth info about the change/update that was made, including any remarks listed on the official ISO page.
* *Date Issued*: date that the change was communicated/published.
* *Source*: name and or edition of newsletter that the ISO 3166 change/update was communicated in (pre 2013), or the link to the country's ISO Online Browsing Platform (OBP) page.

Last Updated
============
The list of ISO 3166 updates was last updated on **April 2025**. A log of the latest ISO 3166 updates can be seen in the |updates_md_location_link| file.

.. |updates_md_location_link| raw:: html

   <a href="https://github.com/amckenna41/iso3166-updates/blob/main/UPDATES.MD" target="_blank">UPDATES.md</a>

License
=======
**iso3166-updates** is distributed under the MIT license.

.. |demo_location_link| raw:: html

   <a href="https://colab.research.google.com/drive/1oGF3j3_9b_g2qAmBtv3n-xO2GzTYRJjf?usp=sharing" target="_blank">here</a>

.. note::

    A demo of the software and accompanying API is available |demo_location_link|!
   
.. Changelog
.. =========

.. Latest Version: **1.8.0**.
.. ******
.. v1.8.0
.. ******

.. Latest Version: **1.7.0**.
.. ******
.. v1.7.0
.. ******


.. Latest Version: **1.6.1**.
.. ******
.. v1.6.1
.. ******
.. * Updating class instance encapsulation structure
.. * Update API index file class import
.. * Update package dependencies
.. * Update software and API docs to reflect new class import structure
.. * Update workflow actions to have validation that previous workflow created

.. ******
.. v1.6.0
.. ******
.. * Add readthedocs documentation
.. * Add remarks from ISO page to each update's description, if applicable
.. * Add tqdm loop in get_all script
.. * Adding demo, medium article and documentation links to readme
.. * Update library requirements
.. * Update workflow timeouts

.. ******
.. v1.5.0
.. ******
.. * Add UPDATES.md file that keeps track of all the ISO 3166 updates 
.. * Adding additional env vars (EXPORT, CREATE_ISSUE) to check_for_updates functionality
.. * Add OBP link to each update description
.. * Update usage examples in comments and readme's
.. * Update software package description
.. * Add additional unit tests for software and API
.. * Fix gcloud error in check_for_updates.yml workflow
.. * Rerun get_all script with latest data

.. ******
.. v1.4.5
.. ******
.. * Add API frontend with documentation and description about software & API
.. * Update check_for_updates functionality with archive folder create_issue functionality
.. * https://github.com/amckenna41/iso3166-updates/commit/2c5f6d0dc33939d7401efc27e725fedbad2ab27d#diff-28bf033b5cb718463e74964422b5de9a0ab07436c3a765363e7c6ceb8a421e8b


Contents
========
.. toctree::
   usage
   api
   contributing