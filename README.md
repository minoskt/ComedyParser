## ComedyParser

ComedyParser is a system that allows humanoid robots to act as stand-up comedians in live comedy shows. The system uses [SHORE computer vision framework](http://www.iis.fraunhofer.de/en/ff/bsy/tech/bildanalyse/shore-gesichtsdetektion.html) to analyse the audience in real-time, identify the existing people and make the robot look at or point to them. It also uses both SHORE and audio signal levels to recognise responses of the audience such as Laughing or Applauding.

Watch a [Video](https://vimeo.com/72090729) of ComedyParser in action using a [RoboThespian](http://www.robothespian.com) robot.


### Requirements

- Python 2.7
- Natural Language Toolkit (NLTK) from http://www.nltk.org
- English punkt tokenizer using nltk.download() in a python shell
- PyAudio from http://people.csail.mit.edu/hubert/pyaudio/


### Usage

```
python playComedy.py input.json
```

### Comedy Script check

Always use a JSON validator on your input script (e.g. http://jsonlint.com)

Using the following command, you can check for invalid Unicode characters and unsupported commands ("WARNING" messages).

```
python Comedy.py input.json
```

## Publications

Kleomenis Katevas, Patrick G.T. Healey, Matthew Tobias Harris, “Robot Stand-up: Engineering a Comic Performance”, Short paper, [Humanoid Robots and Creativity](http://cogsci.eecs.qmul.ac.uk/humanoids/) workshop @ IEEE Humanoids 2014, Madrid, November 2014.
[\[pdf\]](http://www.eecs.qmul.ac.uk/~ec09351/papers/HumanoidRobots14.pdf)

Kleomenis Katevas, Patrick G.T. Healey and Matthew Tobias Harris, “Robot Comedy Lab: Experimenting with the Social Dynamics of Live Performance”, Frontiers in Psychology 6:1253. doi: 10.3389/fpsyg.2015.01253.
[\[pdf\]](http://journal.frontiersin.org/article/10.3389/fpsyg.2015.01253)

## Press Coverage

This project was featured on the following on-line magazines and websites:

- [New Scientist: Robot comedian stands up well against human rivals](https://www.newscientist.com/article/dn24050-robot-comedian-stands-up-well-against-human-rivals)

- [Queen Mary University of London: Comedy robot metal tested at the Barbican](http://www.qmul.ac.uk/media/news/items/se/111813.html)

- [Chortle: Rise of the Robocomics - The machines performing stand-up](http://www.chortle.co.uk/news/2013/08/05/18432/rise_of_the_robocomics)

- [London Evening Standard: Scientists create robot to take on comedians in stand-up challenge](http://www.standard.co.uk/news/london/scientists-create-robot-to-take-on-comedians-in-standup-challenge-8753779.html)

- [The New Yorker: A Robot Walks Into a Bar...](http://www.newyorker.com/online/blogs/elements/2013/12/a-robot-walks-into-a-bar.html)

- [Phys.org: Robot does standup for London audience](http://phys.org/news/2013-08-robot-standup-london-audience-video.html)

- [The Huffington Post: Comedy Robot Video: Researchers Program 'RoboThespian' To Perform Stand-Up Comedy & Gauge Crowd](http://www.huffingtonpost.com/2013/08/19/comedy-robot-video_n_3781490.html)

- [CNET: RoboThespian tests its mettle as stand-up comic](http://www.cnet.com/uk/news/robothespian-tests-its-mettle-as-stand-up-comic/)

Ph.D. student Toby Harris won the 1st prize in a national photo competition with a picture of RoboThespian performing stand-up comedy live on-stage:

- [Queen Mary University of London: Student’s stand-up robot photo wins national competition](http://www.qmul.ac.uk/media/news/items/se/126324.html)

- [The Guardian: National science photography competition](http://www.theguardian.com/science/gallery/2014/mar/31/national-science-photography-competition-in-pictures)

- [Times Higher Education: From robots to charades - 15 remarkable science photographs](http://www.timeshighereducation.co.uk/from-robots-to-charades-15-remarkable-science-photographs/2012464.article)

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
