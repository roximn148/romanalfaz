.. *****************************************************************************
   Copyright (c) 2026 RoXimn <roximn148@gmail.com>
   This source code is licensed under the MIT license found in the
   LICENSE.txt file in the root directory of this source tree.
   *****************************************************************************

********************************************************************************
Installation
********************************************************************************
You can install `romanalfaz` directly from PyPI using `pip`.

Standard Installation
================================================================================

Run the following command in your terminal::

    pip install romanalfaz

Recommended: Using a Virtual Environment
================================================================================

It is highly recommended to install Python packages inside a virtual environment
to prevent dependency conflicts with your global system packages.

On macOS/Linux
--------------
Create a virtual environment::

    python3 -m venv venv

Activate the virtual environment::

    source venv/bin/activate

Install the package::

    pip install romanalfaz



On Windows
----------
Create a virtual environment::

    python -m venv venv

Activate the virtual environment::

    venv\Scripts\activate

Install the package::

    pip install romanalfaz

Adding to Project Dependencies
================================================================================

If you are using `romanalfaz` as part of a larger project, you can add it
to your dependency tracking files:

* **requirements.txt**: Add `romanalfaz` to your requirements file, then install using::

    pip install -r requirements.txt

* **pyproject.toml**: Add `romanalfaz` to the project file and install using::

    pip install .

* **Poetry**::

    poetry add romanalfaz
* **uv**::

    uv add romanalfaz
