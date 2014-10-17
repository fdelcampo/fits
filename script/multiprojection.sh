#!/bin/bash



## Ks

#./projection.py ~/zuist-scenes-local/fits/Ks/v20100411_00944_st_tl.fit ~/zuist-scenes-local/fits/Ks/v20100411_00980_st_tl.fit
#mv newfits.fits 0944_0980.fits
#./projection.py ~/zuist-scenes-local/fits/Ks/v20100411_00908_st_tl.fit ~/zuist-scenes-local/fits/Ks/v20100411_01016_st_tl.fit
#mv newfits.fits 0908_1016.fits

./projection.py ~/zuist-scenes-local/fits/Ks/v20100420_00370_st_tl.fit ~/zuist-scenes-local/fits/Ks/v20100411_01052_st_tl.fit 0370_1052.fits &

./projection.py ~/zuist-scenes-local/fits/Ks/v20100411_00872_st_tl.fit ~/zuist-scenes-local/fits/Ks/v20110508_00412_st_tl.fit 0872_0412.fits &


wait
./projection.py ~/zuist-scenes-local/fits/Ks/v20100420_00370_st_tl.fit ~/zuist-scenes-local/fits/Ks/v20110508_00412_st_tl.fit 0370_0412.fits

: './projection.py newfits.fits ~/zuist-scenes-local/fits/Ks/v20100411_00908_st_tl.fit
./projection.py newfits.fits ~/zuist-scenes-local/fits/Ks/v20100411_01016_st_tl.fit
./projection.py newfits.fits ~/zuist-scenes-local/fits/Ks/v20100411_01052_st_tl.fit
./projection.py newfits.fits ~/zuist-scenes-local/fits/Ks/v20100411_00872_st_tl.fit
./projection.py newfits.fits ~/zuist-scenes-local/fits/Ks/v20100420_00370_st_tl.fit
./projection.py newfits.fits ~/zuist-scenes-local/fits/Ks/v20110508_00412_st_tl.fit
'

## H
: '
./imageTiler.py ~/zuist-scenes-local/fits/H/v20100411_01040_st_tl.fit
./imageTiler.py ~/zuist-scenes-local/fits/H/v20100411_00968_st_tl.fit
./imageTiler.py ~/zuist-scenes-local/fits/H/v20100411_00932_st_tl.fit
./imageTiler.py ~/zuist-scenes-local/fits/H/v20100411_00860_st_tl.fit
./imageTiler.py ~/zuist-scenes-local/fits/H/v20100420_00358_st_tl.fit
./imageTiler.py ~/zuist-scenes-local/fits/H/v20100411_01004_st_tl.fit
./imageTiler.py ~/zuist-scenes-local/fits/H/v20100411_00896_st_tl.fit
./imageTiler.py ~/zuist-scenes-local/fits/H/v20110508_00400_st_tl.fit



## J

./imageTiler.py ~/zuist-scenes-local/fits/J/v20100411_01064_st_tl.fit
./imageTiler.py ~/zuist-scenes-local/fits/J/v20100411_00992_st_tl.fit
./imageTiler.py ~/zuist-scenes-local/fits/J/v20100411_00956_st_tl.fit
./imageTiler.py ~/zuist-scenes-local/fits/J/v20100411_00884_st_tl.fit
./imageTiler.py ~/zuist-scenes-local/fits/J/v20100420_00382_st_tl.fit
./imageTiler.py ~/zuist-scenes-local/fits/J/v20100411_01028_st_tl.fit
./imageTiler.py ~/zuist-scenes-local/fits/J/v20100411_00920_st_tl.fit
./imageTiler.py ~/zuist-scenes-local/fits/J/v20110508_00424_st_tl.fit
'