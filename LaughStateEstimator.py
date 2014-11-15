#!/usr/bin/env python

import time
from collections import deque
import numpy

class LaughStateEstimator:
	'''Estimate 'Laugh State' with SHORE data by comparing current values to historial baseline'''

	happinessCurrent = None
	happinessThreshold = None
	bobbingCurrent = None
	bobbingThreshold = None

	# Calibration to individual audience member is done by comparing current SHORE values to historical values
	# Percentile of historical values to judge as significant happiness or head bobbing
	# 50 is saying they're happy vs not 50% of the time
	happinessPercentile = 50
	bobbingPercentile = 50

	# Duration of the rolling window in the dataseries we analyse, in seconds
	_analysisWindowDuration = 1
	_approxShoreFPS = 20
	
	# Manual calibration variable to normalise bobbing values.
	_maxBob = 15
	_maxBobFound = 0 # maximum actual bob value, can be logged out to set above.

	_secsToMilliSecs = 1000000

	_debug = False

	def __init__(self):
		self.resetHistory()

	def resetHistory(self):
		
		self._analysisWindow = deque(maxlen = self._approxShoreFPS * self._analysisWindowDuration)
		
		self._happinessHistogram = numpy.zeros(101, dtype = numpy.int32)
		self.happinessCurrent = None
		self.happinessThreshold = None
		
		self._bobbingHistogram = numpy.zeros(101, dtype = numpy.int32)
		self.bobbingCurrent = None
		self.bobbingThreshold = None
		
		self._histogramCount = 0

	def analyse(self, framedatetime, happiness, top, bottom):

		### Notes

		# This timeseries segmentation is naive but informed by manually performing the task
		# An audience member was noticeably smiling vs not. More precisely, starting to smile was a sharp change between two visibly different states. This might then slowly wind down. 
		# An audience member laughing amongst other things would be smiling and their head would bob up and down
		# Smile detection is implemented as SHORE Happiness score entering a certain percentile of their Happiness history. Score is median averaged over a second to reduce effect of outliers.
		# Bobbing detection is implemented as SHORE Face vertical position variance over a second entering a certain percentile of their position variance history

		# The certain percentile required needs to be a best fit obtained through comparison of this process to the manual annotations

		# To say this is unoptimised is an understatement. 
		# xHistory deques should be numpy arrays
		# xHistory shouldn't even exist, rather a cumulative function

		# if any measures are missing, skip
		if happiness is None or top is None or bottom is None:
			self.happinessCurrent = None
			self.bobbingCurrent = None
			return 'Indeterminate'

		# calculate vertical centre of face
		yPos = (top - bottom) / 2.0

		# create an int timestamp, adapted from python 3.3 here for python 2.7
		frametime = ( framedatetime.year, framedatetime.month, framedatetime.day, framedatetime.hour, framedatetime.minute, framedatetime.second, -1, -1, -1 )
		timestamp = time.mktime(frametime)
		timestamp = int(timestamp)*self._secsToMilliSecs + framedatetime.microsecond
		if self._debug: print framedatetime, timestamp
		
		# roll on our rolling window of data with the frame data as tuple
		self._analysisWindow.append( (timestamp, happiness, yPos) )

		# make a list for each measure to analyse through our rolling *duration*
		windowStartTime = timestamp - (self._analysisWindowDuration * self._secsToMilliSecs)
		happinessValues = [x[1] for x in self._analysisWindow if x[0] > windowStartTime]
		yPosValues = [x[2] for x in self._analysisWindow if x[0] > windowStartTime]    
		
		if self._debug: print self, 'Count: ' + str(len(happinessValues))
				
		# get computed measure from rolling window    
		self.happinessCurrent = numpy.median(happinessValues) # happiness is in range 0-100
		if self._debug: print self.happinessCurrent
		
		self.bobbingCurrent = numpy.std(yPosValues) # bobbing comes out in range 0 - ~15, mostly < 2.
		self.bobbingCurrent = min(self.bobbingCurrent * 100/self._maxBob, 100)
		if self._debug: print self.bobbingCurrent
		
		# _maxBob manual calibration info logging
		if self._debug and (self.bobbingCurrent > self.__maxBobFound):
			self._maxBob = self.bobbingCurrent
			print self, '_maxBob: ' + str(self.bobbingCurrent)
		
		# add values to that measure's histogram
		self._happinessHistogram[self.happinessCurrent] += 1
		self._bobbingHistogram[self.bobbingCurrent] += 1
		self._histogramCount += 1
		
		# if we don't have enough measures to judge, skip
		if self._histogramCount < 10:
			return 'Indeterminate'
		
		# compute significance levels from history
		self.happinessThreshold = 0
		count = 0
		while (count < (self.happinessPercentile * self._histogramCount / 100)):
			count += self._happinessHistogram[self.happinessThreshold]
			self.happinessThreshold += 1
		if self._debug: print self.happinessThreshold
		
		self.bobbingThreshold = 0
		count = 0
		while (count < (self.bobbingPercentile * self._histogramCount / 100)):
			count += self._bobbingHistogram[self.bobbingThreshold]
			self.bobbingThreshold += 1
		if self._debug: print self.bobbingThreshold
		
		laughingState = 'Not Laughing'

		if self.happinessCurrent > self.happinessThreshold:
			laughingState = 'Smiling'

			if self.bobbingCurrent > self.bobbingThreshold:
				laughingState = 'Laughing'

		if self._debug: print laughingState + '\n'

		return laughingState
		
	def analyseWithShoreDict(self, shoreDict):
		
		shoreDict['LaughState'] = self.analyse(shoreDict['TimeStamp'], shoreDict['Happy'], shoreDict['Top'], shoreDict['Bottom'])

	