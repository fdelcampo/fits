#!/usr/bin/python
# -*- coding: UTF-8 -*-

SUCCEEDED_IMPORTING_NUMPY = True
SUCCEEDED_IMPORTING_ASTROPY = True

import os, sys

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


def memory_usage_resource():
	import resource
	rusage_denom = 1024.
	if sys.platform == 'darwin':
		# ... it seems that in OSX the output is different units ...
		rusage_denom = rusage_denom * rusage_denom
	mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
	return mem

def header(src_path):
	#print "RESOURCE: %.2f" % (memory_usage_resource())
	print "header"
	hdulist = fits.open(src_path, mode="readonly", memmap=True)
	print "RESOURCE: %.2f MB" % (memory_usage_resource())
	if hdulist[0].header['NAXIS'] == 2:
		size = (hdulist[0].header['NAXIS1'], hdulist[0].header['NAXIS2'])
		wcsdata = wcs.WCS(hdulist[0].header)
		header = hdulist[0].header
	elif hdulist[1].header['NAXIS'] == 2:
		size = (hdulist[1].header['NAXIS1'], hdulist[1].header['NAXIS2'])
		wcsdata = wcs.WCS(hdulist[1].header)
		header = hdulist[1].header
	else:
		print("Naxis == %d" % (hdulist[0].header['NAXIS']) )
		hdulist.close()
		return

	hdulist.close()
	#print "RESOURCE: %.2f" % (memory_usage_resource())
	return {'header': header, 'wcsdata': wcsdata, 'size': size}


def listener(reference):

	import pika
	import time
	'''
	credentials = pika.PlainCredentials('fitsuc', 'wall.13')
	parameters = pika.ConnectionParameters('192.168.1.213',
	                                       5672,
	                                       '/fitsuc',
	                                       credentials)
	'''
	#parameters = pika.URLParameters('amqp://fitsuc:wall.13@192.168.1.213:5672/fitsuc%2F')

	#connection = pika.BlockingConnection(parameters)

	connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='192.168.1.213', port=5672, virtual_host='/fitsuc', ))
	channel = connection.channel()

	channel.queue_declare(queue='task_queue', durable=True)
	print ' [*] Waiting for messages. To exit press CTRL+C'

	def callback(ch, method, properties, body):
	    print " [x] Received %r" % (body,)
	    time.sleep( body.count('.') )
	    print " [x] Done"
	    ch.basic_ack(delivery_tag = method.delivery_tag)

	channel.basic_qos(prefetch_count=1)
	channel.basic_consume(callback,
	                      queue='task_queue')

	channel.start_consuming()

	print "Listing queues ..."

# main
def main(argv):

	if len(argv) > 1:
		SRC_PATH = os.path.realpath(argv[1])
	else:
		print "You need parameter of Fits image reference"
		return

	if not SUCCEEDED_IMPORTING_ASTROPY and not SUCCEEDED_IMPORTING_NUMPY:
		print "You need library Astropy and Numpy"
		return
	else:
		if os.path.isfile(SRC_PATH):
			REFERENCE = header(SRC_PATH)
			listener(REFERENCE);
		else:
			print "The file not exist"
			return



if __name__ == "__main__":
	main(argv=sys.argv)