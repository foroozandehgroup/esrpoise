Installation
============

The requirements are:

 - **Xepr**. We have tested Xepr versions 2.8b.5
   
 - **Python 3**. This refers to a separate, system installation of Python 3; in particular, ESRPOISE requires a minimum version of **Python 3.7.** (We have tested up to Python 3.8.)

Installing python 3
-------------------

blabla how to install python3 with CENTOS when you can and can't sudo

Installing esrpoise
-------------------

Once python is installed, you can install POISE using ``pip`` (replace ``python`` with ``python3`` if necessary)::

    python -m pip install esrpoise

The following Python packages are required, they should get automatically installed with esrpoise if you do not already have them:

 - **numpy**
 - **XeprAPI**
 - **pybobyqa**

Updating POISE
--------------

Simply use::

    python -m pip install --upgrade esrpoise

(again replacing ``python`` with ``python3`` if necessary). All other steps (including troubleshooting, if necessary) are the same.


Installing from source
----------------------

If you obtained the source code (e.g. from ``git clone`` or a `GitHub release <https://github.com/foroozandehgroup/esrpoise/releases>`_) and want to install from there, simply ``cd`` into the top-level ``esrpoise`` directory and run::

   pip install .

or equivalently::

   python setup.py install


Installing without internet
---------------------------

If your spectrometer does not have an Internet connection, then the installation becomes a bit more protracted.
On a computer that *does* have an Internet connection:

Do we know how to do that?