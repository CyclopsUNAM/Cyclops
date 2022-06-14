from astropy import units as u
from astropy.coordinates import SkyCoord, Distance

c = SkyCoord(
    ra="23 42 43.3447",
    dec="-14 32 41.652",
    unit=(u.hourangle, u.deg),
    frame="icrs",
    obstime="j2000",
    pm_ra_cosdec=99.280 * u.mas / u.yr,
    pm_dec=-66.320 * u.mas / u.yr,
    distance=Distance(parallax=21.960 * u.mas),
)
print(c)
