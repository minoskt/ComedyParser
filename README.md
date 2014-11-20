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

## Publications

Kleomenis Katevas, Patrick G.T. Healey, Matthew Tobias Harris, “Robot Stand-up: Engineering a Comic Performance”, Short paper, [Humanoid Robots and Creativity](http://cogsci.eecs.qmul.ac.uk/humanoids/) workshop @ IEEE Humanoids 2014, Madrid, November 2014.
[\[pdf\]](http://www.eecs.qmul.ac.uk/~ec09351/papers/HumanoidRobots14.pdf)

## License

```
The MIT License (MIT)

Copyright (c) 2014. Queen Mary University of London
Kleomenis Katevas, k.katevas@qmul.ac.uk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

```
