# Validação do Challenge 01

Validação realizada pelo candidato no Docker Desktop em macOS e revisada a partir das capturas de tela compartilhadas na conversa.

| Verificação | Resultado observado |
|---|---|
| Construção da imagem | `docker build -t challenge-01 .` concluído com sucesso. |
| Testes dentro do Docker | Quatro testes executados, todos aprovados (`OK`). |
| Captura real | Interface `lo` dentro do container, duração de 60 segundos, código de saída 0. |
| Tráfego gerado | Dez datagramas UDP locais enviados e recebidos. |
| Registros capturados | 20 pacotes UDP, totalizando 1.120 bytes. |
| Rankings | Origem e destino `127.0.0.1`, com 20 pacotes e 1.120 bytes em cada ranking. |
| Persistência | Após remover o container de captura, um novo container consultou `data/live.db` pelo volume e retornou os mesmos totais e rankings. |

A contagem observada no loopback inclui a observação dos datagramas em envio e recebimento; não representa vinte solicitações distintas da aplicação. Há apenas um IP distinto nesta demonstração, portanto o top 5 exibe uma linha.

A demonstração valida captura ao vivo na interface local do container. Não comprova captura da placa física do Mac, captura do host Linux, desempenho em alto volume ou ausência de perda de pacotes.

