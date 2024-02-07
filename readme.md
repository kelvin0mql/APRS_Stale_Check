# aprsStaleCheck.py
## Old "misc_python" project moved to "APRS_Stale_Check" on Feb 7, 2024
The short story: my APRS 2-way Gateway has sometimes gone offline for several days without my noticing. This checks it
and sends email to alert me of a problem.

The long story: I had a TYT DMR dual-band radio for sale on CraigsList, & someone was low-balling me on it. Irritated,
I decided to find another use for it out of spite. Bought a Rigblaster Advantage, & figured out how to set it up as an
APRS 2-way Gateway. Kind of fun to then see how far away I could hit it with my HT at lowest power. But then, just left
it running and mostly forgot about it.

Few weeks later, a guy across town emailed me to thank me for putting the Gateway up. Apparently it was "the only one
in all of Anoka County". It was filling a gap, & doing a greater service to the area Ham Community than I'd've expected.
I re-arranged things so the APRS station had the highest antenna, & shortest, best feedline. It got even better.

Fast forward a year, and something had glitched on the Raspberry pi that runs this thing. It was offline a while, and
that same fellow ham emailed me to inform me. Rebooted, got it back on the air.

A month or so later, another email informing me I was offline. This time, it was the radio - the channel knob must've
gotten bumped & it was no longer on 144.39MHz. This same thing happened at least one more time, when I decided to look
for a way to monitor this automatically. Just like at my day job, Nagios or splunk> or something should check it on a
regular basis and notify me if it's gone.

The solution was made possible by...
Firstly the fact that aprs.fi has an API which can be used to get info on an APRS station more efficiently than trying 
to scrape data off a human-readable web-page (and in fact, if you do try to do that, like I did, the aprs.fi system
detects this, throws you an error, redirecting you to a page that tells you, "Dude, you're doing it wrong, please use
the API for this sort of shit." Essentially, not literally.)

Secondly, IntelliJ IDEA has an AI Assistant which take a pseudo-code description of what you want to do, and write you
a script in python (et al), which can then be refined with subsequent adjustment prompts. You can also tell the
Assistant the URL of aprs.fi's page about the API, and say "explain how to use the API".

Thirdly, Proton Mail has an app called a Bridge, which allows me to leverage a local SMTP-server-like service without
actually running a local SMTP server.

Please see line 35 of the script for its usage.

It will send an email with Importance=High if the monitored station hasn't been heard by aprs.fi in an hour. But if it
has been heard within the hour, the email Importance=Low.

The 6th command line argument is DEBUG, INFO or WARN. If you choose WARN, then it will not email you if the station 
has been heard within the hour. But choose (DEBUG or) INFO and it will email you either way. So use INFO to make sure
you've got all your stuff set up right, then change your crontab entry to use WARN instead.
