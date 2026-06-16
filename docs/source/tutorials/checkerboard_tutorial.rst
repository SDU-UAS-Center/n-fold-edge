Checkerboard
============

In this tutorial we will show how *n-fold-edge* CLI can be used to detect corners of a checkerboard in an image.

First a image of checkerboard is needed. In this tutorial we will use the checkerboard from :download:`here <../_static/patterns.pdf>`. Page 8 which we print out at hold in front of a camera.

If *n-fold-edge* is not already installed, see :doc:`installation </installation>`.

With *n-fold-edge* installed the CLI can be run with:

.. code-block:: shell

    python -m checkerboard

or if the installation have added *n-fold-edge* to the path it can be invoked simply with:

.. code-block:: shell

    checkerboard

From here on out we will assume *n-fold-edge* is in the path, but if that is not the case for you replace :code:`checkerboard` in the following with :code:`python -m checkerboard`.

Then we can run the following:

.. code-block:: shell

    checkerboard /path/to/image.png --kernel-size 21 --output tutorial-checkerboard.csv

Here we also supplied the a kernel-size *101* to use. A Larger kernel-size can give better results depending on the size of the checkerboard but will be slower. we also tell the program *--output* to save all found corners in a csv file. Another option is to use the *--output-image* to save a image with the found corners marked with red circles.

Below is a sample of the csv file with the checkerboard corner locations. *Image x* and *image y* are the image coordinates of a corner and *object x* and *object y* are the corners relative position to each other.

=================   ==========   =========   ========    ========
Image file          image x      image y     object x    object y
=================   ==========   =========   ========    ========
...
path/to/image.png   1017.99695   310.43902    0           1
path/to/image.png   1019.22826   742.89751    0          -1
path/to/image.png   1020.22152   966.98432    0          -2
path/to/image.png   1228.76734   525.54046    1           0
path/to/image.png   1225.81256   314.68380    1           1
path/to/image.png   1232.54707   740.86310    1          -1
path/to/image.png   1237.20839   963.41986    1          -2
path/to/image.png   1455.85207   742.89855    2          -1
path/to/image.png    801.36247   522.70910   -1           0
path/to/image.png    802.78263   299.01144   -1           1
path/to/image.png    799.59552   749.18699   -1          -1
path/to/image.png    797.43134   981.06289   -1          -2
path/to/image.png    564.19622   519.57029   -2           0
...
=================   ==========   =========   ========    ========
