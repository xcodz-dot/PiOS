# PiOS
PiOS is a Python written Operating System which features almost everything in a minimal OS.
You can check also check-out [PiOS-SDK](https://github.com/xcodz-dot/PiOS-SDK) and
[Denver (Optional)](https://github.com/xcodz-dot/denver), if you want to develop applications for it.

For documentation you will have to wait, currently this project is in alpha stage (basic things are yet to implement)

## Installation

To install OS
```bash
pip install PiOS -U
```

after installation you can run a quick check for upgrade by using this command (*Note: this requires internet*)

```bash
python -m pios -c
```

If the above shows a stable release then upgrade it via the command given. Or else if you are one of those
who wants to try out the developer release you can upgrade via the commands given.

## Running

To run a PiOS instance you can simply invoke this command
```bash
python -m pios
```

this will start the default PiOS available.