# RomanAlfaz (رومن الفاظ)

`RomanAlfaz` is a dictionary-based, predictive transliterator that
converts roman-script Urdu words into their arabic-script equivalents.
It automatically ranks and prioritizes matching suggestions
based on their real-world usage frequency.

### How it Works

The tool processes text using a specialized two-layer transformation workflow:

1. **Intermediate Representation**: It leverages the rule-based transliteration algorithm
proposed by [Tafseer Ahmed](https://www.cle.org.pk/clt09/download/ahmed_translit.pdf "Roman to Urdu Transliteration using word list. (2009)").
This converts the user's Roman Urdu input into an intermediate format
designed to bridge the phonetic and structural spelling gaps between the two scripts.
2. **Dictionary Lookup**: The engine passes this intermediate form to
[SymSpellPy](https://github.com/mammothb/symspellpy) to execute
an optimized dictionary search against a precompiled vocabulary list.

### Baseline Vocabulary

The baseline included dictionary is built upon the [CLE Urdu 5000 words](https://www.cle.org.pk/software/ling_resources/UrduHighFreqWords.htm) dataset,
which captures the most frequently used words in the Urdu language.

### Core Workflow

Using `RomanAlfaz` follows a simple three-step process:

1. **Load**: Load a preconfigured arabic-script Urdu vocabulary and corresponding usage frequency.
2. **Input**: Provide a roman-script Urdu word.
3. **Output**: Receive a ranked list of predicted arabic-script suggestions.

<img src="docs/romanalfaz.png" width="70%" alt="RomanAlfaz Core Workflow">

## Documentation

The latest full documentation, installation guide, and API reference is available [**online**](https://romanalfaz.readthedocs.io/en/latest/).

## Installation

You can install `romanalfaz` directly from PyPI using `pip`.

### Standard Installation

Run the following command in your terminal:

```bash
pip install romanalfaz
```

### Recommended: Using a Virtual Environment

It is highly recommended to install Python packages inside a virtual environment to prevent dependency conflicts with your global system packages.

#### On macOS/Linux:
```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the package
pip install romanalfaz
```

#### On Windows:
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate

# Install the package
pip install romanalfaz
```

### Adding to Project Dependencies

If you are using `romanalfaz` as part of a larger project, you can add it to your dependency tracking files:

* **requirements.txt**: Add `romanalfaz` to your file, then install using:
  ```bash
  pip install -r requirements.txt
  ```
* **Poetry**:
  ```bash
  poetry add romanalfaz
  ```
* **uv**:
  ```bash
  uv add romanalfaz
  ```
## Usage

The `romanalfaz` package provides the `RomanAlfaz` class as a centralized,
easy-to-use interface for text transliterations.

### Initialization and Input
* **Built-in Vocabulary**: Instantiating the class automatically loads the include baseline, 5000-word vocabulary.
* **Word-Level Inputs**: The `RomanAlfaz.suggest()` function processes _single words only_. It is
your responsibility to tokenize sentences or larger paragraphs into individual words
before passing them to the function.

### Outputs and Edit Distance
The RomanAlfaz.suggest() function always returns a **3-tuple** representing three matching tiers:
1. Exact Matches,
2. One-Edit Distance Matches, and
3. Two-Edit Distance Matches

The `distance` parameter determines the maximum search depth. The function
will always include the lowest tiers as well and return results across
all matching levels up to your configured limit.

### Interactive Examples

You can test the core functions interactively inside a Python shell. Open your terminal, run `python`, and follow the examples below:

```python
>>> from romanalfaz import RomanAlfaz

>>> ra = RomanAlfaz()

>>> ra.getBestMatch('kitab')
Suggestion(arabic='کتاب', encodedRoman='KTAB', frequency=4643)

>>> ra.getExactMatches('kitab')
[Suggestion(arabic='کتاب', encodedRoman='KTAB', frequency=4643),
 Suggestion(arabic='کتب', encodedRoman='KTB', frequency=666)]

>>> for w in 'kya haal he'.split():
...    d0, d1, d2 = ra.suggest(w, distance=2)
...    # Formated dump of the suggestions 
...    print(f"'{w}' ->")
...    print('  Exact matches:')
...    for item in d0:
...        print(f"    {item!r}")
...    print('  One-Edit matches:')
...    for item in d1:
...        print(f"    {item!r}")
...    print('  Two-Edit matches:')
...    for item in d2:
...        print(f"    {item!r}")
...
'kya' ->
  Exact matches:
    Suggestion(arabic='کیا', encodedRoman='KYA', frequency=108414)
  One-Edit matches:
    Suggestion(arabic='کی', encodedRoman='KY', frequency=575545)
    Suggestion(arabic='کہ', encodedRoman='KH', frequency=237419)
    Suggestion(arabic='یہ', encodedRoman='YH', frequency=128103)
    Suggestion(arabic='کیا', encodedRoman='KYA', frequency=108414)
    Suggestion(arabic='کئے', encodedRoman='KYE', frequency=14970)
    Suggestion(arabic='کیے', encodedRoman='KYE', frequency=4976)
  Two-Edit matches:
'haal' ->
  Exact matches:
    Suggestion(arabic='حال', encodedRoman='HAL', frequency=4893)
    Suggestion(arabic='ہال', encodedRoman='HAL', frequency=936)
    Suggestion(arabic='حائل', encodedRoman='HAYL', frequency=316)
  One-Edit matches:
    Suggestion(arabic='حاصل', encodedRoman='HASL', frequency=25881)
    Suggestion(arabic='حال', encodedRoman='HAL', frequency=4893)
    Suggestion(arabic='حامل', encodedRoman='HAML', frequency=2227)
    Suggestion(arabic='آل', encodedRoman='AAL', frequency=1014)
    Suggestion(arabic='ہال', encodedRoman='HAL', frequency=936)
    Suggestion(arabic='فعال', encodedRoman='FAAL', frequency=718)
  Two-Edit matches:
    Suggestion(arabic='حاصل', encodedRoman='HASL', frequency=25881)
    Suggestion(arabic='حالات', encodedRoman='HALAT', frequency=6537)
    Suggestion(arabic='حال', encodedRoman='HAL', frequency=4893)
    Suggestion(arabic='حامل', encodedRoman='HAML', frequency=2227)
    Suggestion(arabic='آل', encodedRoman='AAL', frequency=1014)
    Suggestion(arabic='ہال', encodedRoman='HAL', frequency=936)
'he' ->
  Exact matches:
    Suggestion(arabic='ہے', encodedRoman='HE', frequency=466908)
  One-Edit matches:
  Two-Edit matches:
```
