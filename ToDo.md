# To Do 

- [ ] Create CRON job that runs the script every few months, checking for updates on all the Wikis and exporting and updating the neccessary files (https://www.youtube.com/watch?v=2OwLb-aaiBQ).
- [ ] Check variable naming conventions.
- [ ] Check output of bandit and flake8 check.
- [X] Export updates to csv, dataframe.
- [ ] Create API so each ISO3166-2 update info can be retrieved as json format.
- [ ] Create demo using python notebook.
- [ ] Generate updated for a particular year. 
- [ ] Change all instances of iso3166-updates to iso3166_updates except for pypi name.
- [ ] Add GCP upload to workflow.
- [ ] Upload all iso3166-updates for all countries in seperate folder of main repo dir.
- [ ] If single ISO code put in then print, if mutliple then output to files.
- [X] Append date to update filenames.
- [X] Add maintainer and keywords to setup.py & cfg.
- [X] When using Year var, if DF empty then don't export it.
- [ ] Change "Effective date of change" column to "Date issued"
- [ ] Change "Newsletter" column to "Edition/Newsletter"
- [ ] All countries should have 4 columns: "Edition/Newsletter", "Date issued", "Description of change in newsletter", "Code/Subdivision change"
- [ ] href of newsletter not exporting to json
