import requests
import googlemaps
from bs4 import BeautifulSoup
from datetime import datetime
import re
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class Listing(object):
    def __init__(self, start, end, address, zipcode, price):
        self.start_date = start
        self.end_date = end
        self.address = address
        self.price = int(price)
        self.str_add = address
        self.zip = zipcode

def get_distances(origin, destination):
	gmaps = googlemaps.Client(key='AIzaSyAKVx1f7-Rz8h5ZniCB5rILbbMxC27aFqY')
	# Request directions via public transit
	now = datetime.now()
	directions_result = gmaps.directions(origin,destination, \
		mode="transit", departure_time=now, transit_mode='tram')
	return directions_result
	
def parse(listing):
	#input is list of lists
	matches = re.findall(r'\d{2}.\d{2}.\d{4}', listing[1])
	start_date = datetime.strptime(matches[0], '%d.%m.%Y').date()
	end_date = datetime.strptime(matches[1], '%d.%m.%Y').date()
	address, zipcode = listing[2][1].split(",")
	price = listing[3]
	return Listing(start_date, end_date, address, zipcode, price)

def get_fields(table):
	x = [child.string.strip() for child in table.children]
	return list(filter(lambda a: a != None and a != '', x))

def main():
	destination = "Stefano- Franscini-Platz 5, 8049 Zurich, Switzerland"
	my_end_date = datetime.date(datetime(2017, 8, 31))
	my_start_date = datetime.date(datetime(2017, 6, 25))
	print destination
	print my_end_date

	session = requests.session()

	req = session.get('http://www.woko.ch/en/untermieter-gesucht')

	doc = BeautifulSoup(req.content, "lxml")

	counter = 0
	listings = []
	for tab in doc.find_all('div', {'class':'row'}):
		# if counter is 0, start a new listing
		for child in tab.descendants:
			#print child
		 	if child.name == "tr":
		 		fields = get_fields(child)
				if counter % 2 == 0:
					listings = listings + [fields]
				else: #add to last listing
					listings[-1] = listings[-1] + [fields]
					price = tab.find("div", {'class':'preis'}).string
					listings[-1] = listings[-1] + [price.split('.')[0]]
				counter = counter + 1		
	
	parsedListings = [parse(listing) for listing in listings]
	parsedListings = [listing for listing in parsedListings if listing.end_date >= my_end_date and listing.start_date <= my_start_date]

	addresses = [(listing.address + "," + listing.zip) for listing in parsedListings]
	gmaps = googlemaps.Client(key='AIzaSyAKVx1f7-Rz8h5ZniCB5rILbbMxC27aFqY')	
	matrix = gmaps.distance_matrix(addresses, destination, \
		mode="transit", transit_mode='tram')

	durations = [row['elements'][0]['duration']['text'] for row in matrix['rows']]
	dur_val = [row['elements'][0]['duration']['value'] for row in matrix['rows']]
	dist_list = zip(matrix['origin_addresses'], durations, dur_val)
	dist_list.sort(key=lambda tup: tup[2])
	for x in dist_list:
		print x[1] + "-\t" + x[0]


if __name__ == '__main__':
	main()