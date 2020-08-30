# Flask-Analytics
A Flask analytics library that stores analytics data on your servers and does not use Google Analytics or other analytics services to get analytics data.

The point of this library is to add a way for people to have an anlaytics tool that respects their uses data and does not hand it over to 3rd partys and in the future it will add ways to not track the user at all (no session cookies no visitor cookies etc)


## TODO
### What is needed to be done:

Add comments

Respect DNT (Do Not Track) headers (no session ids no visitor ids)

Make allow cookies banners to get user consent to track them

Convert the indivsual entrys into dimintions (sessions per country percent mobile devices what operating system people use what urls people visit what time of hour+day people are visiting etc)

Convert the whole analytics into a importable module

Make a Javascript tracker as well (a tracker in javascript that tracks how long your on a page if you click things)

Store anonamized data and not raw data with identifyers

### Far down the road:

Support SQL as well as MongoDB and other things like DynamoDB and other databases
