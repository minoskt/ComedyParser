## ComedyParser

ComedyParser is a system that allows humanoid robots to act as stand-up comedians in live comedy shows. The system uses [SHORE computer vision framework](http://www.iis.fraunhofer.de/en/ff/bsy/tech/bildanalyse/shore-gesichtsdetektion.html) to analyse the audience in real-time, identify the existing people and make the robot look at or point to them. It also uses both SHORE and audio signal levels to recognise responses of the audience such as Laughing or Applauding.

Watch a [Video](https://vimeo.com/72090729) of ComedyParser in action using a [RoboThespian](http://www.robothespian.com) robot.


### Requirements

- Python 2.7
- Natural Language Toolkit (NLTK) from http://www.nltk.org
- English punkt tokenizer using nltk.download() in a python shell
- PyAudio from http://people.csail.mit.edu/hubert/pyaudio/


### Usage

	python playComedy.py input.json

### Comedy Script check

Always use a JSON validator on your input script (e.g. http://jsonlint.com)

Using the following command, you can check for invalid Unicode characters and unsupported commands ("WARNING" messages).

    python Comedy.py input.json

### Publications

Kleomenis Katevas, Patrick G.T. Healey, Matthew Tobias Harris, “Robot Stand-up: Engineering a Comic Performance”, Extended abstract, Humanoid Robots and Creativity workshop @ IEEE Humanoids 2014, Madrid, November 2014.

