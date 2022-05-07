# Monitoring visa appointments

This software currently supports AIS-based visa appointment systems (Canada, Mexico, ...)

## Setup

0. Before starting to use this software, please make sure you have signed up your account in the AIS system, and scheduled an initial appointment.
0. Clone this repo. Our working directory is `api/`
0. Create a conda environment named "visa": `conda env create -f scripts/requirements.yml`
0. Activate the conda environment: `conda activate visa`
0. If you are not using an M1 Macbook, please replace `./scripts/chromedriver` with the one that fits your computer. You may download the binary here: [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)
0. Store your AIS system login credentials in the environment variables: `VISA_EMAIL` and `VISA_PSWD`

## Set up notification

0. Download IFTTT to your phone and sign up for an account.
0. Activate the IFTTT [Maker Webhook](https://ifttt.com/maker_webhooks) service. Store the webhook key in the environment variable `VISA_IFTTT_KEY`
0. Create an Applet in IFTTT so that, if a Maker event named `VISA` is detected, then send a notification from the IFTTT app.

## Run

0. Run `python3 manage.py runserver 0:8800`. This will start a local server.
0. Run `python3 scripts/run.py [code]`, where `[code]` is the region in which you are making the appointment. This can be found in the URL of AIS system.
    * For Canada, use `en-ca`
    * For Mexico, use `en-mx`

