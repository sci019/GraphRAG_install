# 導入方法
```
wsl Ubuntu 24.04.1 LTS
```

## ollamaインストール
```shell
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl stop ollama
sudo systemctl disable ollama
ollama serve & ollama_PID=$!
ollama pull llama3 ; kill $ollama_PID
```

## Pythonライブラリ
```shell
python -m venv ragenv
source ragenv/bin/activate
pip install -r requirements.txt.txt
```

<details>

<summary>Python・pipのバージョン</summary>

<br>

```
# python -V
Python 3.12.3

# pip list
Package                  Version
------------------------ ----------
aiohappyeyeballs         2.4.4
aiohttp                  3.11.11
aiosignal                1.3.2
annotated-types          0.7.0
anyio                    4.7.0
attrs                    24.3.0
certifi                  2024.12.14
charset-normalizer       3.4.1
dataclasses-json         0.6.7
frozenlist               1.5.0
greenlet                 3.1.1
h11                      0.14.0
httpcore                 1.0.7
httpx                    0.27.2
httpx-sse                0.4.0
idna                     3.10
json_repair              0.35.0
jsonpatch                1.33
jsonpointer              3.0.0
langchain                0.3.13
langchain-community      0.3.13
langchain-core           0.3.28
langchain-experimental   0.3.4
langchain-ollama         0.2.2
langchain-text-splitters 0.3.4
langsmith                0.2.7
marshmallow              3.23.2
multidict                6.1.0
mypy-extensions          1.0.0
neo4j                    5.27.0
numpy                    2.2.1
ollama                   0.4.5
orjson                   3.10.13
packaging                24.2
pip                      24.0
propcache                0.2.1
pydantic                 2.10.4
pydantic_core            2.27.2
pydantic-settings        2.7.0
python-dotenv            1.0.1
pytz                     2024.2
PyYAML                   6.0.2
regex                    2024.11.6
requests                 2.32.3
requests-toolbelt        1.0.0
sniffio                  1.3.1
SQLAlchemy               2.0.36
tenacity                 9.0.0
tiktoken                 0.8.0
typing_extensions        4.12.2
typing-inspect           0.9.0
urllib3                  2.3.0
yarl                     1.18.3
```

</details>


## neo4j導入
```shell
# javaインストール
apt-get remove --purge openjdk-17-jdk
apt install openjdk-17-jdk
# update-alternatives --config java
java --version

# neo4jのインストール
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add -
echo 'deb https://debian.neo4j.com stable 5' | tee -a /etc/apt/sources.list.d/neo4j.list
apt-get update
apt-get install neo4j=1:5.25.1
neo4j version
cd /var/lib/neo4j/plugins
wget https://repo.maven.apache.org/maven2/org/neo4j/procedure/apoc-core/5.25.1/apoc-core-5.25.1-core.jar 
echo "dbms.security.procedures.allowlist=apoc.coll.*,apoc.load.*,apoc.*" >> /etc/neo4j/neo4j.conf
echo "dbms.security.procedures.unrestricted=algo.*,apoc.*" >> /etc/neo4j/neo4j.conf
echo 'server.default_listen_address=0.0.0.0' >> /etc/neo4j/neo4j.conf
```


# 実行方法
```shell
sudo su
neo4j console &
ollama serve & ollama_PID=$!

source ragenv/bin/activate
python create_graph.py
python graph_rag.py

#最後に不要なプロセス削除
kill $ollama_PID ; neo4j stop
```

# neo4jのDB操作

DBの検索・削除
```SQL
MATCH (n) RETURN n
MATCH (n) DETACH DELETE n
```

リレーションの名前を改名
```SQL
MATCH (a)-[r:SALARY_COMPARISON]->(b)
CREATE (a)-[newRel:HAS_THE_TWICE_MORE_SALARY_THAN]->(b)
SET newRel = r
DELETE r

