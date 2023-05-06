import opencage.geocoder

key = 'c9108ca48b98481b9625802a5b2affa4' # replace with your OpenCage API key
geocoder = opencage.geocoder.OpenCageGeocode(key)

results = geocoder.reverse_geocode(17.6801, 83.2016) # pass in the latitude and longitude coordinates of your current location

print(results[0]['components']["state_district"])