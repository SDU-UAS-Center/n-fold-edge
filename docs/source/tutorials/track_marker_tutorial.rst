Track marker
============

In this tutorial we will show how *n-fold-edge* CLI can be used to track a marker with a webcam.

First a marker is needed. In this tutorial we will use a marker of order 6 and it can be downloaded :download:`here <../_static/patterns.pdf>` and printed (the last page).

If *n-fold-edge* is not already installed, see :doc:`installation </installation>`.

With *n-fold-edge* installed the CLI can be run with:

.. code-block:: shell

    python -m track-markers

or if the installation have added *n-fold-edge* to the path it can be invoked simply with:

.. code-block:: shell

    track-markers

From here on out we will assume *n-fold-edge* is in the path, but if that is not the case for you replace :code:`track-markers` in the following with :code:`python -m track-markers`.

To use our webcam for tracking we will give *track-markers* a *0* as the video input which will use the default webcam. If another webcam is desired try with *1* or more.

.. code-block:: shell

    track-markers 0 --show --order 6 --kernel-size 21 --output tutorial-marker6.csv

Here we also supplied the marker order *6* and a kernel-size *21* to use. A Larger kernel-size can give better results depending on the marker size but will be slower. we also tell the program *--show* to open a window with the webcam view. Another option is to use the *--output-video* to save a video. Last we tell the program to save the marker location to a *csv* file named *tutorial-marker6.csv*

When the window opens and show the webcam feed, try and hold op the marker and move it around. If the marker is found it will mark it with a red circle and a blue line.

To stop the program press *q*, *esc* or *ctrl-c*.

Below is a sample of the csv file with marker locations:

=====   ==========   ==========   =========    ========   =====
Frame   x            y            direction    quality    order
=====   ==========   ==========   =========    ========   =====
...
57      365.601563   326.584640    1.764990    0.050800   6
58      364.123639   322.378904   -0.319500    0.030503   6
59      360.234427   314.376741   -0.294536    0.026498   6
60      356.916695   309.157411    2.852505    0.051228   6
61      354.409452   306.397820    1.811190    0.073916   6
62      352.042820   304.675182    1.813869    0.060549   6
63      348.620657   302.509173    1.826995    0.040862   6
64      345.164850   300.102629   -1.296454    0.066076   6
65      342.505863   297.894744   -0.237597    0.040265   6
66      339.940118   295.467012   -0.214262    0.076283   6
...
=====   ==========   ==========   =========    ========   =====
