# Challenge 01 — Analisador simples de tráfego

Aplicação de terminal em Python que captura pacotes de uma interface escolhida, grava seus campos em SQLite e apresenta total de pacotes, quantidade por protocolo e top 5 IPs de origem e destino por volume em bytes. Executa em Docker, sem servidor web ou banco externo.

## 1. O que entregar

Suba esta pasta como `challenge-01/` no repositório. Os arquivos principais são `app.py`, `requirements.txt`, `Dockerfile` e este README. `demo.py` e `tests/` facilitam demonstração e verificação. Não suba bancos ou capturas reais; a pasta `data/` é ignorada pelo Git, exceto pelo marcador `.gitkeep`.

## 2. Correspondência com o enunciado

| Requisito | Implementação |
|---|---|
| Capturar de uma interface especificada | Comando `capture --interface NOME`, usando `sniff` do Scapy. |
| IP de origem, IP de destino, protocolo e tamanho | Uma linha por pacote na tabela `packets`. |
| Total de pacotes | Consulta `COUNT(*)`. |
| Número de pacotes por protocolo | Agrupamento por `protocol`. |
| Top 5 IPs de origem e destino | Soma de bytes por IP, ordenação decrescente, limite de cinco. |
| Banco de dados | SQLite em arquivo persistente no volume Docker. |
| Preferência por Python | Aplicação Python com uma dependência: Scapy. |
| Execução em Docker | Dockerfile com Python 3.12. |
| Configuração, execução, uso e decisões | Documentados abaixo, incluindo esquema e limites. |

O enunciado não exige interface gráfica. “Mais tráfego” foi interpretado como maior soma de bytes; a saída também mostra pacotes por IP para esclarecer o critério.

## 3. Primeiro passo: construir a imagem

Instale e inicie Docker Engine (Linux) ou um runtime Docker compatível (macOS/Windows). Confira:

```bash
docker version
```

A saída precisa incluir a seção Server. Se aparecer “Cannot connect to the Docker daemon”, inicie o runtime antes de continuar.

Abra o terminal dentro da pasta `challenge-01` e execute:

```bash
docker build -t challenge-01 .
docker run --rm challenge-01 --help
```

Os comandos a seguir usam Bash/Zsh, incluindo o terminal do macOS. No PowerShell, troque `"$(pwd)/data:/app/data"` por `"${PWD}/data:/app/data"`.

## 4. Demonstração simples com dados sintéticos

Este modo testa leitura de pacotes, armazenamento e estatísticas sem permissões de captura. Não substitui a captura real da seção 5.

```bash
mkdir -p data
docker run --rm -v "$(pwd)/data:/app/data" --entrypoint python challenge-01 demo.py
docker run --rm -v "$(pwd)/data:/app/data" challenge-01 --db data/demo.db read data/demo.pcap
docker run --rm -v "$(pwd)/data:/app/data" challenge-01 --db data/demo.db stats
```

Na primeira importação em um banco novo, o resultado esperado é:

```text
TOTAL: 6 pacotes | 426 bytes
TCP: 2
UDP: 2
ARP: 1
ICMP: 1
```

Top de origem: `192.0.2.3` com 142 bytes, `192.0.2.1` com 126, `2001:db8::1` com 74 e `192.0.2.2` com 42. Há quatro IPs distintos; o ranking exibe até cinco, sem inventar uma quinta linha. Os endereços são de documentação e o gerador de PCAP não envia esses pacotes à rede.

Cada importação adiciona registros. Importar o mesmo PCAP duas vezes duplica os registros intencionalmente; não existe deduplicação. Para repetir a demonstração sem acumular, use outro nome de banco, por exemplo `data/demo2.db`.

## 5. Captura real dentro do Docker: macOS, Windows ou Linux

O exemplo captura a interface `lo` do próprio container e gera dez datagramas UDP entre processos locais. É captura real de uma interface de rede; o alcance é a rede do container, não a placa Wi-Fi do computador.

### 5.1 Descobrir as interfaces

```bash
docker run --rm challenge-01 interfaces
```

Normalmente aparecem `lo` e `eth0`.

### 5.2 Iniciar captura de 30 segundos

```bash
docker run -d --name challenge-capture --cap-drop ALL --cap-add NET_RAW -v "$(pwd)/data:/app/data" challenge-01 --db data/live.db capture --interface lo --duration 30
```

O container fica em execução enquanto captura. Aguarde cerca de dois segundos para inicialização e então gere tráfego antes de terminar os 30 segundos:

```bash
docker exec challenge-capture python demo.py --udp
```

### 5.3 Aguardar e ver o resultado

```bash
docker wait challenge-capture
docker logs challenge-capture
docker rm challenge-capture
docker run --rm -v "$(pwd)/data:/app/data" challenge-01 --db data/live.db stats
```

O `docker wait` deve retornar 0. Os logs devem mostrar UDP e o IP `127.0.0.1` nos rankings. A contagem observada no loopback pode variar por sistema/backend: envio e recebimento podem ser observados separadamente. Não exija exatamente dez pacotes capturados. O banco também acumula execuções anteriores.

Se não houver pacotes, confira se o gerador executou durante a janela de captura e se a interface escolhida foi `lo`. Se o container já terminou, repita com um nome disponível e duração maior, por exemplo `--duration 60`.

**Limitação do Docker Desktop:** seus containers executam em um ambiente Linux separado. `eth0` dentro do container não é a interface `en0` do Mac. O host networking do Docker Desktop opera em camada 4 e não fornece acesso direto à interface física para captura de quadros. Para capturar a interface do host com Docker, use Docker Engine em Linux, como descrito a seguir.

## 6. Capturar a interface do host Linux

Em uma máquina ou VM Linux com Docker Engine:

```bash
docker run --rm --network host challenge-01 interfaces
```

Escolha uma interface realmente listada, por exemplo `eth0`, `ens33` ou `enp0s3`. Substitua `eth0` abaixo pelo nome correto:

```bash
docker run --rm -it --network host --cap-drop ALL --cap-add NET_RAW -v "$(pwd)/data:/app/data" challenge-01 --db data/linux.db capture --interface eth0 --duration 30
```

Gere tráfego normal nessa máquina durante a captura. O programa mostra as estatísticas ao terminar. `Ctrl+C` encerra a captura e mantém os registros já gravados. Também é possível limitar por quantidade:

```bash
docker run --rm -it --network host --cap-drop ALL --cap-add NET_RAW -v "$(pwd)/data:/app/data" challenge-01 --db data/linux.db capture --interface eth0 --duration 60 --count 100
```

A captura termina ao atingir 100 pacotes ou 60 segundos, o que vier primeiro. A interface mostra somente o tráfego visível naquele ponto de observação. Não é uma promessa de enxergar todo o tráfego de uma rede comutada. Use em interfaces e ambientes em que você tenha autorização.

## 7. Comandos e comportamento

| Comando/opção | Função |
|---|---|
| `interfaces` | Lista interfaces visíveis ao processo. |
| `capture --interface NOME` | Captura ao vivo; duração padrão de 30 segundos. |
| `--duration N` | Duração máxima positiva em segundos. |
| `--count N` | Limite opcional positivo de pacotes. |
| `read arquivo.pcap` | Importa uma captura existente. |
| `stats` | Consulta todo o histórico do banco escolhido. |
| `--db CAMINHO` | Opção global; deve vir antes do comando. Padrão: `data/traffic.db`. |

Exemplo correto: `python app.py --db data/teste.db stats`.

As estatísticas são apresentadas ao final da captura/importação e quando solicitado por `stats`; não há dashboard em tempo real. O programa informa separadamente quantos registros adicionou na execução atual. As estatísticas referem-se a todo o arquivo de banco, inclusive capturas anteriores. Escolha um banco novo para isolar uma sessão.

## 8. Banco de dados e decisões

### Esquema

```sql
CREATE TABLE packets (
    id INTEGER PRIMARY KEY,
    captured_at TEXT NOT NULL,
    interface TEXT NOT NULL,
    src_ip TEXT,
    dst_ip TEXT,
    protocol TEXT NOT NULL,
    size_bytes INTEGER NOT NULL CHECK(size_bytes >= 0)
);
```

- `id`: identificador único automático da linha.
- `captured_at`: horário do pacote em UTC, no formato ISO 8601; no PCAP, preserva o horário registrado na captura.
- `interface`: nome selecionado na captura; na importação, `pcap:nome-do-arquivo` identifica a origem da leitura, sem alegar conhecer a interface original.
- `src_ip` e `dst_ip`: endereços IPv4 ou IPv6. Quadros não IP têm NULL, inclusive ARP, que usa endereços de protocolo em um formato diferente.
- `protocol`: TCP, UDP, ICMP, ICMPv6, ARP, outro protocolo IP numérico ou categoria de outros quadros.
- `size_bytes`: tamanho dos bytes do pacote entregue pelo Scapy, incluindo cabeçalhos disponíveis. Não estima preâmbulo, intervalo entre quadros ou FCS ausente; uma captura truncada não permite medir todos os bytes originais do enlace.

Não são armazenados payloads nem o pacote binário completo no banco: são persistidos os campos do pacote pedidos no desafio, mais horário e interface. O PCAP sintético é apenas apoio de demonstração. A documentação torna essa interpretação explícita.

### Por que estas tecnologias?

**Python:** leitura simples e biblioteca padrão suficiente para CLI e banco. **Scapy:** captura e decodificação de protocolos em uma única biblioteca. **SQLite:** banco em um arquivo, sem servidor, credenciais ou infraestrutura adicional. **Docker:** padroniza Python e dependências. Uma interface de terminal mantém a solução pequena e fácil de explicar.

O callback de `sniff` grava cada pacote. `store=False` evita manter toda a captura em uma lista na memória. `promisc=False` evita depender de modo promíscuo e permite usar somente a capacidade NET_RAW no exemplo Linux. O container roda com o usuário padrão da imagem para a captura, sem `--privileged`; a capacidade necessária é adicionada explicitamente.

Cada inserção é confirmada imediatamente com `commit`, priorizando simplicidade e persistência. Isso limita o desempenho em alto volume. Há apenas uma tabela e não foram adicionados índices para otimizações não demonstradas. Para grandes volumes, seria necessário medir perdas, usar filas/lotes e avaliar índices ou outro banco.

O ranking soma bytes e usa o texto do IP como critério determinístico de desempate. Pacotes não IP contam no total e na distribuição por protocolo, mas não entram no top de IPs. Fragmentos sem cabeçalho de transporte decodificado podem aparecer como `IP-N`; túneis e protocolos incomuns não recebem análise profunda. Não há reassemblagem, análise de payload ou detecção de ameaças.

## 9. Ver o que foi salvo

Não é preciso instalar cliente SQLite. Após a demonstração:

```bash
docker run --rm -v "$(pwd)/data:/app/data" --entrypoint python challenge-01 -c "import sqlite3; c=sqlite3.connect('data/demo.db'); print(*c.execute('SELECT id, src_ip, dst_ip, protocol, size_bytes FROM packets LIMIT 10'), sep='\n')"
```

Consultas usadas para as estatísticas:

```sql
SELECT COUNT(*) FROM packets;
SELECT protocol, COUNT(*) FROM packets GROUP BY protocol;
SELECT src_ip, SUM(size_bytes), COUNT(*)
FROM packets WHERE src_ip IS NOT NULL
GROUP BY src_ip ORDER BY SUM(size_bytes) DESC, src_ip ASC LIMIT 5;
```

Para destinos, a mesma consulta usa `dst_ip`.

## 10. Testes e estado de verificação

Veja também [o registro de validação](VALIDACAO.md).

```bash
docker run --rm --entrypoint python challenge-01 -m unittest discover -s tests -v
```

Os quatro testes verificam campos persistidos e IPv6 com extensão, preservação de ARP sem IP, top 5 por bytes para origem e destino, totais, contagens por protocolo e banco vazio.

**Verificado na preparação:** os quatro testes passaram em Python 3.14.7 com Scapy 2.6.1; o fluxo CLI gerou um PCAP com seis pacotes, importou os registros e apresentou 426 bytes, os protocolos e rankings esperados. Uma segunda execução consultou as mesmas estatísticas, confirmando persistência entre processos.

**Validação em Docker concluída pelo candidato e conferida por capturas de tela:** a imagem Python 3.12 foi construída e os quatro testes automatizados passaram dentro do container. A captura real na interface `lo`, com duração de 60 segundos, terminou com código 0. O gerador enviou dez datagramas UDP; foram observados 20 pacotes, totalizando 1.120 bytes, com origem e destino `127.0.0.1`. Após remover o container de captura, uma consulta em um novo container retornou os mesmos totais e rankings, confirmando persistência no volume. A demonstração cobre a interface local do container no Docker Desktop em macOS; a captura da interface do host Linux não foi executada neste teste.

### Execução local opcional

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python demo.py
python app.py --db data/local.db read data/demo.pcap
```

No Windows, a ativação é `.venv\Scripts\Activate.ps1`. A execução local acima é auxiliar; a entrega usa Docker. Captura local depende de permissões e suporte do sistema.

## 11. Problemas comuns

| Problema | O que conferir |
|---|---|
| Docker não conecta | Runtime iniciado e seção Server em `docker version`. |
| Interface inexistente | Execute `interfaces` no mesmo modo de rede da captura. |
| Operação não permitida | Uso de NET_RAW e restrições do runtime; não resolva adicionando `--privileged` sem necessidade. |
| Zero pacotes | Interface correta, janela de captura e tráfego nessa interface. |
| Banco vazio em outra execução | Mesmo `--db` e mesmo volume `data` montado. |
| Valores duplicados | Execuções/importações anteriores no mesmo banco; use novo arquivo para uma demonstração isolada. |
| Banco bloqueado | Evite vários escritores simultâneos no mesmo arquivo; solução desenhada para uma captura por banco. |
| Porta UDP 9999 ocupada | O gerador local precisa dessa porta livre dentro do container. |

## 12. Preparação para apresentar

Fluxo: **interface → Scapy → extração de campos → INSERT no SQLite → consultas SQL → terminal**.

**Por que não há frontend?** O requisito é exibir estatísticas; o terminal cumpre essa função e reduz componentes.

**Por que SQLite?** Oferece persistência e consultas SQL sem instalar um servidor de banco.

**O que significa “mais tráfego”?** Soma de bytes capturados por IP; a quantidade de pacotes também é mostrada, porque pacotes de tamanhos diferentes não representam o mesmo volume.

**Por que ARP não aparece no top IP?** Não é pacote IP. Contabilizo o quadro no total e por protocolo, preservando NULL nos campos IP.

**Você captura a placa do Mac pelo Docker?** Não diretamente. Demonstro captura ao vivo na interface do container. Para a interface do host, uso Docker Engine no Linux com rede host.

**Os dados sobrevivem ao container?** Sim, quando o arquivo SQLite está no volume montado em `/app/data`.

**O que mudaria para alto tráfego?** Mediria perdas e gargalos, adotaria escrita em lotes e filas e avaliaria armazenamento. A versão atual prioriza o escopo básico.

**Como validou?** Testes de extração, persistência e agregação, importação CLI de PCAP determinístico, construção da imagem e quatro testes aprovados dentro do Docker. A captura real na interface `lo` registrou 20 pacotes UDP e 1.120 bytes. Uma consulta após remover o container confirmou a persistência no volume. O alcance da demonstração está descrito na seção 10.

## 13. Referências

- [Scapy: sniff, callbacks e leitura de PCAP](https://scapy.readthedocs.io/en/stable/api/scapy.sendrecv.html).
- [Docker: rede host e limitações do Docker Desktop](https://docs.docker.com/engine/network/drivers/host/).
- [Docker Desktop: funcionamento da rede em ambiente Linux separado](https://docs.docker.com/desktop/features/networking/).
