# fatbaby-2

Basic Flask app that reads the latest state of a Google Sheet, nicely formats that state as a web page.

We've been using a Google Form to record in when and how much we fed our baby and wet/dirty diapers.
That Google Form writes to a Google Sheet.

This app reads from the Google sheet, tells us when his next feeding should be.

## Requirements
- a GCP service account
- json credentials for that GCP service account, stored in an env variable `GOOGLE_CREDENTIALS`
- make sure you've granted aaaccess to the Google Sheet to the GCP service account (you can do this in the sharing section of the Google Sheet...just share the sheet with the service account's email address)

## Deploy Instructions
```
git push heroku main
```
