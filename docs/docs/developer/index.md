# Developers

How about making a app? (If you are here for profit earning by creating apps, then you are at wrong place)

To make a app first thing to do is to install SDK for PiOS, start by installing packages `PiOS[SDK]`, `denver-api`, `PiOS`

```bash
pip install PiOS[SDK] denver-api PiOS --upgrade
```

The above should install latest version of everything required to run PiOS and develop for PiOS.
So let's start with something simple by creating a app that can **Count on spacebar click**.

First create a new folder for example in my case `Demo App`. After that go into the folder and open
a terminal. There you can type these commands:

```bash
pios-sdk-app --new -c version=1.0.0 -c name=TestApp
pios-sdk-ppk config -o
```

The above should do the most of the initial setup you can also go with a easier way by using tool `ark`.

```bash
ark quickstart new  # You can also omit `new` because it is default, you can also use `from_source` to create
                    # from existing sources.
ark automate -o setup.py  # Again, you can omit the option because it is by default `setup.py`
```


