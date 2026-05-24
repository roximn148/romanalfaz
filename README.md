# RomanAlfaz (رومن الفاظ)

RomanAlfaz is a dictionary based predictive roman-to-arabic script
Urdu transliterator which takes a roman-script Urdu word and
tries to match them to a predefined list of arabic-script words,
prioritizing according to order of usage frequency.

It uses transliteration algorithm proposed by 
[Tafseer Ahmed](https://www.cle.org.pk/clt09/download/ahmed_translit.pdf "Roman to Urdu Transliteration using word list. (2009)")
to convert the user provided roman-script Urdu text to
an intermediate roman representation which tries to bridge
the textual representation differences between arabic-script and roman-scripts
for Urdu language. This intermediate representation is then used
to look up the arabic-script representation of the Urdu word.

The `RomanAlfaz` internally uses [SymSpellPy](https://github.com/mammothb/symspellpy)
for the dictionary lookup from a predefined curated list of Urdu words and their usage frequencies.
The baseline word list is taken from [CLE Urdu 5000](https://www.cle.org.pk/software/ling_resources/UrduHighFreqWords.htm)
most frequently used words. The internal workflow of the RomanAlfaz.

1. Load a vocabulary list,
2. provide a word in roman-script, and
3. get the suggestions(s) in arabic-script.

![`RomanAlfaz` workflow chart](docs/romanalfaz.png)

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

`romanalfaz` provides `RomanAlfaz` class as a single convenience point of conversion.
Instantiating it uses the included baseline 5000-word vocabulary for use. The
`RomanAlfaz.suggest` function expects words input, so it's the user's responsibility
to tokenize larger texts into word tokens.

`RomanAlfaz.suggest` output is always provided in three tiers (3-tuple),
1. Exact,
2. One-Edit, and
3. Two-Edits.

The edit `distance` parameter controls which tiers to look for, the lower tiers
will always be looked for, and the corresponding results will be provided. 

### Interactive Examples

You can test the core functions interactively inside a Python shell. Open your terminal, run `python`, and follow the examples below:

```python
>>> from romanalfaz import RomanAlfaz

>>> ra = RomanAlfaz()

>>> for w in 'kya hal he'.split():
        print(f"'{w}' -> {ra.suggest(w, distance=0)}")
'kya' -> ([('کیا', 'KYA', 108414)], [], [])
'hal' -> ([('حل', 'HL', 7083), ('حال', 'HAL', 4893), ('ہال', 'HAL', 936), ('ہل', 'HL', 378)], [], [])
'he' -> ([('ہے', 'HE', 466908)], [], [])
```
