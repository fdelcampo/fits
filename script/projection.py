#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os, sys
import inspect

SUCCEEDED_IMPORTING_NUMPY = True
SUCCEEDED_IMPORTING_ASTROPY = True

try:
	import numpy as np
	import math
except ImportError:
	SUCCEEDED_IMPORTING_NUMPY = False

# http://www.astropy.org/
try:
	from astropy.io import fits
	from astropy import wcs 
except ImportError:
	SUCCEEDED_IMPORTING_ASTROPY = False


OUTPUT = "newfits.fits"

def header(src_path):

	hdulist = fits.open(src_path)

	if hdulist[0].header['NAXIS'] == 2:
		size = (hdulist[0].header['NAXIS1'], hdulist[0].header['NAXIS2'])
		im = hdulist[0].data
		wcsdata = wcs.WCS(hdulist[0].header)
		header = hdulist[0].header
	elif hdulist[1].header['NAXIS'] == 2:
		size = (hdulist[1].header['NAXIS1'], hdulist[1].header['NAXIS2'])
		im = hdulist[1].data
		wcsdata = wcs.WCS(hdulist[1].header)
		header = hdulist[1].header
	else:
		print("Naxis == %d" % (hdulist[0].header['NAXIS']) )
		return

	return {'header': header, 'im': im, 'wcsdata': wcsdata, 'size': size}



def projection(reference, concatenable, scale):


	path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	name = "wcs_"
	ext = "fits"

	pointsRef = [[0,0], [0,reference['size'][1]], [reference['size'][0],0], [reference['size'][0],reference['size'][1]]]
	points = [[0,0], [0,concatenable['size'][1]], [concatenable['size'][0],0], [concatenable['size'][0],concatenable['size'][1]]]

	minx = 99999999
	miny = 99999999
	maxx = -99999999
	maxy = -99999999
	print "point"
	for p in points:
		ra, dec = concatenable['wcsdata'].wcs_pix2world(p[0], p[1], 0)
		ii, jj = reference['wcsdata'].wcs_world2pix(ra, dec, 0)
		print "ra:%f - dec:%f -- (%f, %f)" % (ra, dec, ii, jj)
		if ii < minx:
			minx = ii
		if jj < miny:
			miny = jj
		if ii > maxx:
			maxx = ii
		if jj > maxy:
			maxy = jj
	print "pointRef"
	for p in pointsRef:
		ra, dec = reference['wcsdata'].wcs_pix2world(p[0], p[1], 0)
		ii, jj = reference['wcsdata'].wcs_world2pix(ra, dec, 0)
		print "ra:%f - dec:%f -- (%f, %f)" % (ra, dec, ii, jj)
		if ii < minx:
			minx = ii
		if jj < miny:
			miny = jj
		if ii > maxx:
			maxx = ii
		if jj > maxy:
			maxy = jj


	#print "(%d, %d) (%d, %d) -- %f, %f" % (minx, miny, maxx, maxy, math.sqrt( miny*miny + maxy*maxy ), math.sqrt( minx*minx + maxx*maxx ))
	#print "math.sqrt(%f*%f + %f*%f)" % (miny, miny, maxy, maxy)
	#print "math.sqrt(%f + %f)" % (miny*miny, maxy*maxy)
	#print "math.sqrt(%f)" % (miny*miny+maxy*maxy)
	#print "%f" % ( math.sqrt(miny*miny+maxy*maxy) )
	#print "(%d, %d) (%d, %d)" % (reference['size'][0], reference['size'][1], concatenable['size'][0], concatenable['size'][1])

	im = np.zeros( [maxy - miny, maxx - minx], dtype=np.float32 )
	
	disy = math.sqrt(miny*miny)
	disx = math.sqrt(minx*minx)

	print "displace y:%d x:%d" % (disy, disx)

	for j in range(0, reference['size'][1]):
		for i in range(0, reference['size'][0]):
			im[j+disy,i+disx] = reference['im'][j,i]

	for j in range(0, concatenable['size'][1]):
		for i in range(0, concatenable['size'][0]):
			ra, dec = concatenable['wcsdata'].wcs_pix2world(i, j, 0)
			ii, jj = reference['wcsdata'].wcs_world2pix(ra, dec, 0)
			im[jj+disy,ii+disx] = concatenable['im'][j,i]

	w = wcs.WCS(naxis=2)
	#ra, dec = reference['wcsdata'].wcs_pix2world(reference['size'][0]/2, reference['size'][1]/2, 0)
	#print "crpix [%d, %d]" % (reference['header']['CRPIX1'], reference['header']['CRPIX2'])
	ra, dec = reference['wcsdata'].wcs_pix2world(reference['header']['CRPIX1'], reference['header']['CRPIX2'], 0)
	w.wcs.crval = [ra, dec]
	w.wcs.ctype = reference['wcsdata'].wcs.ctype
	w.wcs.equinox = reference['wcsdata'].wcs.equinox
	w.wcs.dateobs = reference['wcsdata'].wcs.dateobs
	#w.wcs.crpix = [reference['size'][0]/2+disx, reference['size'][1]/2+disy]
	w.wcs.crpix = [reference['header']['CRPIX1']+disx, reference['header']['CRPIX2']+disy]
	
	if reference['wcsdata'].wcs.has_cd():
		cd = reference['wcsdata'].wcs.cd
		w.wcs.cd = cd*scale
		w.wcs.cdelt = [np.sqrt(w.wcs.cd[0,0]*w.wcs.cd[0,0]+w.wcs.cd[1,0]*w.wcs.cd[1,0]), np.sqrt(w.wcs.cd[0,1]*w.wcs.cd[0,1]+w.wcs.cd[1,1]*w.wcs.cd[1,1])]
		w.wcs.pc = [[w.wcs.cd[0,0]/ w.wcs.cdelt[0], w.wcs.cd[0,1]/ w.wcs.cdelt[0]],[w.wcs.cd[1,0]/ w.wcs.cdelt[1], w.wcs.cd[1,1]/ w.wcs.cdelt[1]]]
	else:
		pc = reference['wcsdata'].wcs.pc
		w.wcs.pc = pc*scale
		#w.wcs.cdelt = 

	header = w.to_header()
	#header['NAXIS1'] = im.shape[1]
	#header['NAXIS2'] = im.shape[0]
	header['OBJECT'] = reference['header']['OBJECT'] + " - " + concatenable['header']['OBJECT']


	hdu = fits.PrimaryHDU(header=header, data=im)
	if os.path.isfile(OUTPUT):
		os.remove(OUTPUT)	
	
	hdu.writeto(OUTPUT)

	#fits.writeto(path+"_newfits.fits", im, header)



# main
if len(sys.argv) > 3:
    SRC_PATH = os.path.realpath(sys.argv[1])
    SRC_PATH2 = os.path.realpath(sys.argv[2])
    OUTPUT = sys.argv[3]
elif len(sys.argv) > 2:
    SRC_PATH = os.path.realpath(sys.argv[1])
    SRC_PATH2 = os.path.realpath(sys.argv[2])
elif len(sys.argv) > 1:
	SRC_PATH = os.path.realpath(sys.argv[1])

if not SUCCEEDED_IMPORTING_ASTROPY and not SUCCEEDED_IMPORTING_NUMPY:
	print "You need library Astropy and Numpy"
else:
	#headerRef(SRC_PATH)
	#projection(SRC_PATH2)
	reference = header(SRC_PATH)
	print "Object ref: %s" % (reference['header']['OBJECT'])
	second = header(SRC_PATH2)
	print "Object second: %s" % (second['header']['OBJECT'])
	scale = math.pow(2, 5-1)
	projection(reference, second, 1/scale)
	
