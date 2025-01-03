# 導入方法

ollamaインストール
```shell
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl stop ollama
sudo systemctl disable ollama
ollama serve & ollama_PID=$!
ollama pull llama3 ; kill $ollama_PID
```

Pythonライブラリ
```shell
python -m venv ragenv
source ragenv/bin/activate
pip install -r requirements.txt.txt
```

neo4j導入
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

