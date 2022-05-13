Installation
============

The requirements are:

 - **Xepr**. We have tested Xepr versions 2.8b.5
   
 - **Python 3**. ESRPOISE requires a minimum version of **Python 3.6.** (We have tested up to Python 3.8.)


Installing Python 3
-------------------

This is most easily done by downloading an installer from the official CPython website (https://www.python.org/downloads/), or via your package manager (``apt``, ``yum`` or similar).

On CentOS 7, you would typically need::

    yum -y install python3

You might also need to tkinter with::

    yum -y install python3-tkinter

Note that this creates a ``python3`` executable, which is independent from the previously installed Python 2 (which can still be invoked with ``python``).

A particular issue we faced when setting up POISE was installing Python on CentOS 7 without administrator rights.
If you are in this situation, you will have to compile the Python source code, using the following steps:

1. Download `the source code for Python 3.7 <https://www.python.org/downloads/source/>`_. We used 3.7.11, but anything should work.
2. Download the source code for Tcl/Tk (at least for now, Python needs to be compiled with tkinter for POISE to run successfully).
3. Compile Tcl/Tk, making sure to install it to a user-writable directory (e.g. your home directory).
4. Compile Python, again installing it to your home directory. This step is pretty difficult as there are certain (undocumented) compilation flags which must be passed correctly.

The following series of shell commands (give or take) worked for us, so you could simply run the following::

    # Download source code
    curl -LO https://www.python.org/ftp/python/3.7.11/Python-3.7.11.tgz
    curl -LO https://prdownloads.sourceforge.net/tcl/tcl8.6.12-src.tar.gz
    curl -LO https://prdownloads.sourceforge.net/tcl/tk8.6.12-src.tar.gz
    tar xf Python-3.7.11.tgz
    tar xf tcl8.6.12-src.tar.gz
    tar xf tk8.6.12-src.tar.gz
    # Install tcl/tk
    cd tcl8.6.12/unix
    ./configure --prefix=$HOME/.local/tcltk
    make
    make install
    cd ../../tk8.6.12/unix
    ./configure --prefix=$HOME/.local/tcltk
    make
    make install
    # Install Python
    cd ../../Python-3.7.11/
    CPPFLAGS="-I$HOME/.local/tcltk/include" LDFLAGS="-L$HOME/.local/tcltk/lib -Wl,-rpath,$HOME/.local/tcltk/lib -ltcl8.6 -ltk8.6" ./configure --prefix=$HOME/.local/python3 --with-tcltk-includes="-I$HOME/.local/tcltk/include" --with-tcltk-libs="-L$HOME/.local/tcltk/lib"
    make
    make install

One of the tested spectrometer computer also required the installation of ``libffi`` and ``libffi-devel`` before being able to ``make install``.

You should then have a working installation of Python 3.7 in ``~/.local/python3/bin/python``.
Note that you should always use this version of Python whenever installing packages: so, it's safer to always use ``/path/to/python -m pip install X`` rather than just ``pip install``.

Naturally, you can place this Python executable first in your ``$PATH`` in order to avoid having to type out the full path every time, for example by placing the following line::

    export PATH=~/.local/python3/bin:$PATH

inside your ``~/.bashrc`` or ``~/.bash_profile``.

If there are any issues, please get in touch via GitHub or email.


Installing esrpoise
-------------------

Once Python 3 is installed, you can install POISE using ``pip``::

    python -m pip install esrpoise

(replace ``python`` with ``python3`` if necessary)

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

   python -m pip install .

Add ``-e`` to be able to edit the code. Equivalently you can run::

   python -m setup.py install

Replace ``install`` with ``develop`` to edit the code.

(use ``python3`` if necessary)

Installing without Internet
---------------------------

If the computer you are using does not have an Internet connection, then you will need to:

1. Download the POISE source code from GitHub: ``git clone https://github.com/foroozandehgroup/esrpoise`` and copy it over to the target computer.
2. Install Python by downloading the installer from a different computer and copying it over.
3. On the target computer, install the POISE package locally by navigating to the ``esrpoise`` directory you copied over and doing ``python -m pip install .`` (note the full stop at the end).
