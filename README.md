# Stockbot - chatbot for stocks

## Installation & Setup

[Install Python] https://www.python.org/downloads/

[Install pip] https://packaging.python.org/en/latest/tutorials/installing-packages/

If you want to check if Python and pip are installed

```
python3 --version
```
```
pip --version
```

## Create python environment

For macos
```
python3 -m venv myenv
source myenv/bin/activate
```

For windows
```
py -m venv myenv
myenv\Scripts\activate
```

## Installing Flask

```
pip install flask
```

## Running Stockbot app in terminal

cd into your directory

```
python app.py
```

## Demo

https://github.com/ic1618/chat-bot/assets/77613980/ac2675c2-149b-4f95-b199-9a81e300a6c7

## Future work

* Add unit tests for independent scenarios
* Increase error raising + handling
* Add solution for scalability (database) in case of larger datasets
* Provide generative AI responses to user messages (use an API such as the ones from openAI)
* Add better data structures in case of larger datasets (already using dictionaries for o(1) lookup)

