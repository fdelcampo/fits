#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys
import inspect
import exceptions

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


def displace(reference, concatenable):

	pointsRef = [[0,0], [0,reference['size'][1]], [reference['size'][0],0], [reference['size'][0],reference['size'][1]]]
	points = [[0,0], [0,concatenable['size'][1]], [concatenable['size'][0],0], [concatenable['size'][0],concatenable['size'][1]]]

	minx = 99999999
	miny = 99999999
	maxx = -99999999
	maxy = -99999999
	print "second"
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
	print "reference"
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

	disy = math.sqrt(miny*miny)
	disx = math.sqrt(minx*minx)

	print "displace y:%d x:%d" % (disy, disx)
	return {"minx": int(minx), "maxx": int(maxx), "miny": int(miny), "maxy": int(maxy), "disx": int(disx), "disy": int(disy)}


def writeFile(reference, concatenable, disx, disy):

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
		w.wcs.cd = cd
		w.wcs.cdelt = [np.sqrt(w.wcs.cd[0,0]*w.wcs.cd[0,0]+w.wcs.cd[1,0]*w.wcs.cd[1,0]), np.sqrt(w.wcs.cd[0,1]*w.wcs.cd[0,1]+w.wcs.cd[1,1]*w.wcs.cd[1,1])]
		w.wcs.pc = [[w.wcs.cd[0,0]/ w.wcs.cdelt[0], w.wcs.cd[0,1]/ w.wcs.cdelt[0]],[w.wcs.cd[1,0]/ w.wcs.cdelt[1], w.wcs.cd[1,1]/ w.wcs.cdelt[1]]]
	else:
		pc = reference['wcsdata'].wcs.pc
		w.wcs.pc = pc
		w.wcs.cdelt = reference['wcsdata'].wcs.cdelt

	header = w.to_header()

	header['OBJECT'] = reference['header']['OBJECT'] + " - " + concatenable['header']['OBJECT']

	hdu = fits.PrimaryHDU(header=header, data=IM)
	if os.path.isfile(OUTPUT):
		os.remove(OUTPUT)	
	
	hdu.writeto(OUTPUT)

	#fits.writeto(path+"_newfits.fits", im, header)

'''
def init_project(reference, concatenable, disx, disy, xini, yini, lenght, width, height):
	init_project(reference, disx, disy, xini, yini, lenght, width, height)
'''

def init_project(reference, concatenable, disx, disy, xini, yini, lenght, width, height):
	global IM

	try:
		for k in range(xini * width + yini, xini * width + yini + lenght):
			i = (k/width)
			j = (k%width)
			if IM[j+disy,i+disx] < reference['im'][j,i]:
				IM[j+disy,i+disx] = reference['im'][j,i]
	except IndexError:
		print "disx: %f disy: %f xini: %d yini: %d lenght: %d width: %d height: %d IM: (%d, %d)" % (disx, disy, xini, yini, lenght, width, height, IM.shape[1], IM.shape[0])
		print "i: %d j: %d" % (i, j)




def project(reference, concatenable, disx, disy, xini, yini, lenght, width, height):
	global IM

	try:
		for k in range(xini * width + yini, xini * width + yini + lenght):
			#print "k: %d i: %d j: %d" % (k, (k/width), (k%width))
			i = (k/width)
			j = (k%width)
			ra, dec = concatenable['wcsdata'].wcs_pix2world(i, j, 0)
			ii, jj = reference['wcsdata'].wcs_world2pix(ra, dec, 0)
			if IM[jj+disy,ii+disx] < concatenable['im'][j,i]:
				IM[jj+disy,ii+disx] = concatenable['im'][j,i]
	except IndexError:
		print "disx: %f disy: %f xini: %d yini: %d lenght: %d width: %d height: %d IM: (%d, %d)" % (disx, disy, xini, yini, lenght, width, height, IM.shape[1], IM.shape[0])
		print "i: %d j: %d" % (i, j)

# main
def main(argv):
	global SRC_PATH
	global SRC_PATH2
	global OUTPUT
	global IM
	global DISP
	global REFERENCE
	global CONCATENABLE


	if len(argv) > 3:
	    SRC_PATH = os.path.realpath(argv[1])
	    SRC_PATH2 = os.path.realpath(argv[2])
	    OUTPUT = argv[3]
	elif len(argv) > 2:
	    SRC_PATH = os.path.realpath(argv[1])
	    SRC_PATH2 = os.path.realpath(argv[2])
	elif len(argv) > 1:
		SRC_PATH = os.path.realpath(argv[1])
	else:
		"You need parameters"

	if not SUCCEEDED_IMPORTING_ASTROPY and not SUCCEEDED_IMPORTING_NUMPY:
		print "You need library Astropy and Numpy"
	else:


		REFERENCE = header(SRC_PATH)
		print "Object ref: %s" % (REFERENCE['header']['OBJECT'])
		CONCATENABLE = header(SRC_PATH2)
		print "Object concatenable: %s" % (CONCATENABLE['header']['OBJECT'])
		
		
		DISP = displace(REFERENCE, CONCATENABLE)

		IM = np.zeros( [DISP['maxy'] - DISP['miny'], DISP['maxx'] - DISP['minx']], dtype=np.float32 )

		#init_project(reference, DISP['disx'], DISP['disy'], 0, 0, reference['size'][0]*reference['size'][1], reference['size'][0], reference['size'][1])

		#project(reference, concatenable, DISP['disx'], DISP['disy'], 0, 0, concatenable['size'][0]*concatenable['size'][1], concatenable['size'][0], concatenable['size'][1])

		#writeFile(reference, concatenable, DISP['disx'], DISP['disy'])
	


if __name__ == "__main__":
	main(argv=sys.argv)