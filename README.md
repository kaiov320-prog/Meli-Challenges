# Meli Challenges — Infraestrutura

Resolução dos Challenges 1 e 2 do processo seletivo do Mercado Livre. O repositório reúne uma aplicação de análise de tráfego de rede e um prompt para triagem de logs de infraestrutura.

## Organização

| Desafio | Objetivo | Documentação |
|---|---|---|
| [Challenge 1](Challenge-1/) | Capturar pacotes, persistir seus campos e exibir estatísticas de tráfego. | [Configuração, execução e decisões técnicas](Challenge-1/README.md) |
| [Challenge 2](Challenge-2/) | Analisar logs com IA, identificar eventos relevantes e sugerir próximas ações. | [Instruções, fundamentos e critérios de avaliação](Challenge-2/README.md) |

## Challenge 1 — Analisador de tráfego

Aplicação de terminal desenvolvida em **Python**, utilizando **Scapy** para captura, **SQLite** para armazenamento e **Docker** para execução.

Funcionalidades:

- Seleção da interface de rede para captura.
- Registro de IP de origem, IP de destino, protocolo e tamanho de cada pacote, além de horário e interface.
- Total de pacotes e quantidade por protocolo.
- Top 5 IPs de origem e destino por volume em bytes, com quantidade de pacotes por IP.
- Consulta das estatísticas persistidas e importação de PCAP para demonstração.

O banco armazena os campos extraídos dos pacotes; o conteúdo binário completo e os payloads não são persistidos.

### Início rápido

Com o Docker instalado e em execução, abra um terminal na raiz do repositório:

```bash
cd Challenge-1
docker build -t challenge-01 .
docker run --rm --entrypoint python challenge-01 -m unittest discover -s tests -v
```

Para realizar a captura e verificar a persistência, siga o [passo a passo do Challenge 1](Challenge-1/README.md).

### Validação realizada

- Imagem Docker construída com sucesso.
- Quatro testes automatizados aprovados dentro do container.
- Captura real na interface local `lo` do container: **20 pacotes UDP e 1.120 bytes**, com encerramento de código 0.
- Persistência confirmada: após remover o container de captura, um novo container consultou o banco no volume e retornou os mesmos resultados.

A demonstração foi executada em Docker Desktop no macOS. Seu alcance é a interface do container; não representa captura da placa física do Mac. O procedimento para capturar a interface do host Linux está documentado, mas não foi executado nessa demonstração.

Consulte o [registro de validação](Challenge-1/VALIDACAO.md) para os detalhes.

## Challenge 2 — Análise de logs com IA

Prompt reutilizável para interpretar logs brutos, identificar erros, falhas ou anomalias e sugerir verificações e possíveis correções. A saída solicita resumo, achados com evidências, correlação dos eventos, limitações e próximos passos.

| Arquivo | Finalidade |
|---|---|
| [Prompt reutilizável](Challenge-2/01-prompt.md) | Instruções com espaço para inserir outro trecho de log. |
| [Log de exemplo](Challenge-2/02-exemplo.log) | Trecho fornecido no enunciado. |
| [Resposta esperada](Challenge-2/03-resposta-esperada.md) | Referência de interpretação dos eventos relevantes. |
| [Prompt preenchido](Challenge-2/04-prompt-com-exemplo.md) | Versão pronta para copiar e enviar à IA, contendo o log do enunciado. |

### Como testar

1. Abra o [prompt preenchido](Challenge-2/04-prompt-com-exemplo.md).
2. Copie todo o conteúdo e envie em uma conversa nova na IA escolhida.
3. Compare a resposta com a [referência esperada](Challenge-2/03-resposta-esperada.md), considerando as evidências e os achados, sem exigir redação idêntica.

Para outros logs, utilize o [prompt reutilizável](Challenge-2/01-prompt.md) e substitua o marcador de entrada pelo trecho desejado.

A resposta esperada é uma referência elaborada para o exercício, não uma execução externa registrada. Durante a preparação, também foi revisada uma resposta de IA para um cenário fictício adicional de aplicação web e banco de dados. Essa revisão foi qualitativa, sem métrica de acurácia e sem identificação da ferramenta ou do modelo no material compartilhado.

## Decisões e limites

As soluções priorizam simplicidade, reprodução dos exemplos e clareza das decisões. O Challenge 1 usa um único banco em arquivo e apresenta estatísticas no terminal. O Challenge 2 exige distinção entre fatos e hipóteses, evitando atribuir causa raiz ou recuperação completa sem evidência.

A captura deve ser realizada em ambientes autorizados. Antes de enviar logs reais a serviços externos, remova credenciais e dados sensíveis conforme as regras da organização. Os projetos não incluem credenciais, bancos de captura ou dados de produção.
