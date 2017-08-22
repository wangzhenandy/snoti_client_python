snoti client
=======
v1.0.0

## Prerequisites
* [Python 3](https://www.python.org/)

## Setup
* User should rewrite callback functions in callback.py
* startup like:
```
import callback
client = Client("c74fd6e832eb42de80540d7d738fe025", "9UDAyB8pQY6w2HSewJmwvw", "r5A9PhsYQIGhJ03SSOsIqQ", subkey="sandbox_000", callback = callback)
client.connect()
client.control_kv("8Namn3NCUNFRbuFiZ9NRaF", "virtual:site", {"number":5})
client.disconnect()

```

## Change log: v1.0.0 (2017/08)
* First version

