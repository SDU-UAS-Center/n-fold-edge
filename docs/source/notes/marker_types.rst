Other marker comparison
=======================

An often occurring task in computer vision is to locate a certain object or position in an image. It can either be a generic object, or an object (a marker) that the user have placed actively in the field of view. Robust detection of one or more markers can give precise pose estimates which are required for applications like Augmented Reality.

Many types of markers have been suggested, and they can be divided into two types of markers. The first type of markers are intended for estimating the pose of the object on which the marker is placed. This requires at least four points to be identifiable in the marker, which often consists of a square or rectangular array of black and white pixels. QR Codes and ARuCo markers are both of this type. The second type of markers identifies specific points in images. These markers resemble eg. chess board corners and log spirals.

QR Codes are a 2D bar code, that can contain a significant amount of information. The largest QR codes contain almost 3000 bytes of information. QR Codes was developed by DENSO WAVE. The minimum resolution for reading a QR code containing four bytes of information using the `zxing.org <https://zxing.org/w/decode.jspx>`_ QR code decoder around 50 x 50 pixels (personal experiments). ARuCo markers consists of a black border with a :math:`n \times n` pattern of black and white pixels inside the border [Garrido-Jurado2014]_ The smallest ARuCo marker consists of :math:`4 \times 4` pixel within an two pixel wide border made of black and white pixels. To detect this marker a resolution of at least 18 pixels is likely needed.

Chess board corners are regularly used for camera calibration. The corners can be detected using different techniques, eg. the Harris corner detector [Harris1988]_.

A marker formed as a logarithmic spiral was suggested in [Karlsson2011]_.

A visual comparison of the mentioned marker types are given in :numref:`fig-marker-types`.

.. _fig-marker-types:

.. list-table:: Examples of different marker types and images with a minimal resolution in which the marker can be detected (and verified).
   :width: 100%
   :class: borderless

   * - .. figure:: ../_static/notes/marker_types/qr_code_230x230.png
          :width: 200

          QR code

     - .. figure:: ../_static/notes/marker_types/qr_code_48x48.png
          :width: 200

          QR code 48x48

   * - .. figure:: ../_static/notes/marker_types/aruco_250x250.png
          :width: 200

          AruCo

     - .. figure:: ../_static/notes/marker_types/aruco_25x25.png
          :width: 200

          AruCo 25x25

   * - .. figure:: ../_static/notes/marker_types/logspiral_91x91.png
          :width: 200

          Logspiral

     - .. figure:: ../_static/notes/marker_types/logspiral_21x21.png
          :width: 200

          Logspiral 21x21



.. [Garrido-Jurado2014] \S. Garrido-Jurado, R. Muñoz-Salinas, F.J. Madrid-Cuevas, M.J. Marín-Jiménez, Automatic generation and detection of highly reliable fiducial markers under occlusion, Pattern Recognition, Volume 47, Issue 6, 2014, Pages 2280-2292, ISSN 0031-3203, https://doi.org/10.1016/j.patcog.2014.01.005. (https://www.sciencedirect.com/science/article/pii/S0031320314000235)

.. [Harris1988] \Harris, C. and Stephens, M. (1988) A Combined Corner and Edge Detector. Proceedings of the 4th Alvey Vision Conference, Manchester, 31 August-2 September 1988, 147-151.

.. [Karlsson2011] \Karlsson S, Bigun J. Synthesis and detection of log-spiral codes. In 2011. p. 4. Available from: https://urn.kb.se/resolve?urn=urn:nbn:se:hh:diva-16123
