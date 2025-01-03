# 導入方法

1. ollamaインストール
```shell
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl stop ollama
sudo systemctl disable ollama
```

2. Pythonパッケージ
```shell
pip install -r requirements.txt.txt
```

3. neo4j導入
```shell
# javaインストール
apt-get remove --purge openjdk-11-jdk
apt install openjdk-17-jdk
# update-alternatives --config java
java --version

# neo4jのインストール
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add -
echo 'deb https://debian.neo4j.com stable 5' | tee -a /etc/apt/sources.list.d/neo4j.list
apt-get update
# sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys [16桁のアルファベットと数字] 
apt-get install neo4j=1:5.25.1
neo4j version

cd /var/lib/neo4j/plugins
wget https://repo.maven.apache.org/maven2/org/neo4j/procedure/apoc-core/5.25.1/apoc-core-5.25.1-core.jar 
echo "dbms.security.procedures.allowlist=apoc.coll.*,apoc.load.*,apoc.*" >> /etc/neo4j/neo4j.conf
echo "dbms.security.procedures.unrestricted=algo.*,apoc.*" >> /etc/neo4j/neo4j.conf
echo 'server.default_listen_address=0.0.0.0' >> /etc/neo4j/neo4j.conf
cd; neo4j console
# パスワード変更: neo4j -> password
```

4. 既存のデータベースを保存・再利用
```shell
# 保存
cp -r -f /var/lib/neo4j/data ./graph/sample
# 再利用
cp -r -f ./graph/sample/data /var/lib/neo4j/
```

5. DBの検索・削除
```SQL
MATCH (n) RETURN n
MATCH (n) DETACH DELETE n
```

6. リレーションの名前を改名
```SQL
MATCH (a)-[r:SALARY_COMPARISON]->(b)
CREATE (a)-[newRel:HAS_THE_TWICE_MORE_SALARY_THAN]->(b)
SET newRel = r
DELETE r
```

6. 使用モデル
```
NAME                                ID              SIZE      MODIFIED    
llama3.1:8b-instruct-q8_0           b158ded76fa0    8.5 GB    2 weeks ago    
dsasai/llama3-elyza-jp-8b:latest    ecfdd92e89f6    4.9 GB    2 weeks ago    
llama3.1:8b-instruct-fp16           4aacac419454    16 GB     2 weeks ago    
llama3.1:8b                         46e0c10c039e    4.9 GB    2 weeks ago    
```

