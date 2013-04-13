import re

pomona_regex = re.compile(r"[\w.]+@[\w.]*pomona.edu")
cmc_regex = re.compile(r"[\w.]+@[\w.]*cmc.edu")
hmc_regex = re.compile(r"[\w.]+@[\w.]*hmc.edu")
scripps_regex = re.compile(r"[\w.]+@[\w.]*scripps.edu")
pitzer_regex = re.compile(r"[\w.]+@[\w.]*pitzer.edu")

a = 'joshua.edgcomb@pomona.edu'
b = 'jte02011@pomona.edu'
c = 'jte02011@mymail.pomona.edu'
d = 'a'

print pomona_regex.match(a)
print pomona_regex.match(b)
print pomona_regex.match(c)
print pomona_regex.match(d)
