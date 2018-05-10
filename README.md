# Codecatch-RSSE
This is the CodeCatch recommendation system.
Paper: https://www.dropbox.com/s/4brusvkz75c2og8/CodeCatch.pdf?dl=0


## How to install and run:

1. Install python3 and pip3 with apt-get. Execute also the command:
```
sudo apt-get install python3-tk
```

2. Install required packages listed in 'requirements.txt' using
```
sudo pip3 install -r requirements.txt
```

3. Change SCRAPY_EXEC in 'codecatch.py' to the full path of the scrapy executable.

4. Run 'codecatch.py' and navigate to http://localhost:6060/ to see the service.
