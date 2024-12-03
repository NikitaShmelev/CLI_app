```bash
virtualenv -p python3.11 env
source env/bin/activate
```

```bash
pip install -r requirements.txt
```


# Usage examples
```bash
python main.py validate example.txt
```

```bash
python main.py generate example.txt --transactions 10
```

```bash
python main.py add example.txt --amount 5000 --currency EUR
```

```bash
python main.py set example.txt --index 1 --field amount --value 150.00
```

```bash
python main.py get example.txt --index 1 --field amount
```

```bash
python main.py get example.txt --index 0 --field amount
```

```bash
python main.py get example.txt --index 0 --field name
```
