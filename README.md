# subscribersim

> A simple program that emulates buying a yearly subscription for hosting websites.

subscribersim implements proration logic to handle mid-cycle subscription changes for a hypothetical website platform.


## Getting started
### Installation

Create and enter directory

```
mkdir dir
cd dir
```

Create a virtual environment.

```
python3 -m venv env
```

Activate virtual environment

```
source env/bin/activate
```

Clone repository

```
git clone https://emilledigital@bitbucket.org/emilledigital/subscribersim.git
```

Install dependencies

```
pip install -r requirements.txt
```

Run tests to verify OK


```
python test.py
```

### Example usage

Example interactions contained in subscribersim.py

Run

```
python subscribersim/subscribersim.py
```

Sample interactions

```python
if __name__ == '__main__':
  jake = models.Customer("Jake Peralta", "diehardfan", "@jakeperalta99.com")

  jake.select_plan("Single", helpers.datetime_now())

  jake.add_website("superdupercop.com", True)

  jake.move_to_plan("Plus", helpers.datetime_months_hence(helpers.datetime_get_last_event(jake), 2))

  jake.add_website("iamjohnmclane.com", False)

  jake.add_website("iheartpuzzles.com", False)

  jake.print_table()
```

Sample output

![sample-output](https://i.ibb.co/BNk4jYQ/output.png)


### Documentation

pydoc can be used to lookup module documentation.

```
python -m pydoc test
```


## To do
  * Change event tuple to namedtuple to benefit from field names in models.py
  * Quantize dollar amounts throughout the subscribersim package with decimal library
  * Initialize buffers with empty list instead of zero (will simplify references to the list) in models.py
  * Define method that allows interactive user to specify a datetime object to the second in helpers.py  
  * Add a few more interactions to example program: subscribersim.py

---

## Authors
  * Emille G. - *Initial work* - [Twitter](http://twitter.com/emilledigital), [Blog](https://egxdigital.wordpress.com)


## Acknowledgements
  - Jean-Baptiste Marchand-Arvier - *initial object oriented design*
