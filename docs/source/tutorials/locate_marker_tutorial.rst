Tutorial locate marker
=====================

In this tutorial we will show how *n-fold-edge* CLI can be used to locate a marker in an image.

First a marker is needed. In this tutorial we will use a marker of order 6 and it can be downloaded :download:`here <../_static/patterns.pdf>` and printed (the last page).

If *n-fold-edge* is not already installed, see :doc:`installation </installation>`.

With *n-fold-edge* installed the CLI can be run with:

.. code-block:: shell

    python -m locate-markers

or if the installation have added *n-fold-edge* to the path it can be invoked simply with:

.. code-block:: shell

    locate-markers

From here on out we will assume *n-fold-edge* is in the path, but if that is not the case for you replace :code:`locate-markers` in the following with :code:`python -m locate-markers`.

We can then run locate-markers on an image:

.. code-block:: shell

    track-markers /path/to/image.png --order 5 6 --output-image /path/to/output-image.png

Here we also supplied the marker orders *5* and *6* to detect both. Another option is to use the *--output-image* to save a image with the detected markers drawn on.
