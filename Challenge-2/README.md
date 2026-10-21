# Challenge 02 — Análise de logs de infraestrutura com IA

## 1. Objetivo e escopo

Este projeto entrega um prompt reutilizável que orienta uma IA a ler logs brutos de infraestrutura, localizar erros, falhas ou anomalias e explicar o que pode estar acontecendo, sugerindo uma ação simples. O exemplo usa o trecho fornecido no enunciado do processo seletivo.

A proposta é apoiar a triagem humana. O resultado é uma interpretação das evidências disponíveis, não uma causa raiz comprovada. Não há integração com equipamentos, execução automática de comandos, API paga ou instalação de software. O enunciado do Challenge 02 solicita prompt, exemplo e resposta esperada; não exige aplicação, Docker ou banco de dados para esta etapa.

## 2. Arquivos e ordem de leitura

| Arquivo | Finalidade |
|---|---|
| `01-prompt.md` | Prompt reutilizável, com espaço para inserir qualquer trecho de log. |
| `02-exemplo.log` | Log de exemplo do enunciado, com linhas quebradas pelo PDF recompostas. |
| `03-resposta-esperada.md` | Referência de interpretação para o exemplo; não é uma execução real de IA. |
| `04-prompt-com-exemplo.md` | Prompt completo, já preenchido com o exemplo, pronto para copiar e colar. |
| `README.md` | Instruções, fundamentos, decisões, limites, validação e preparação para entrevista. |

Para avaliar rapidamente, abra o arquivo 04, copie seu conteúdo em uma IA e compare o resultado com o arquivo 03. Para estudar, leia este README e depois acompanhe cada evento na resposta esperada.

## 3. Rastreabilidade dos requisitos

| Requisito do enunciado | Como foi atendido | Onde conferir |
|---|---|---|
| Ler um trecho de log bruto | Entrada delimitada, sem exigir conversão para JSON ou tabela. | Prompt e exemplo preenchido. |
| Identificar erros, falhas ou comportamentos anômalos | Instruções para procurar ocorrências, agrupar eventos relacionados e separar eventos normais. | Regras 3 a 5 e tabela de achados. |
| Explicar resumidamente o que pode estar acontecendo | Resumo limitado a cinco frases e interpretação por grupo. | Resumo e achados da resposta esperada. |
| Oferecer sugestão de solução simples | Próxima verificação e correção condicionada às evidências de cada problema. | Coluna de ação e próximos passos. |
| Enviar um prompt completo | Papel, objetivo, regras, entrada e formato de saída explícitos. | Arquivos 01 e 04. |
| Enviar exemplo de log | Reprodução do exemplo do desafio, preservando horários e identificadores. | Arquivo 02. |
| Enviar resposta esperada | Interpretação dos eventos relevantes e limites do diagnóstico. | Arquivo 03. |

O material cobre todos os itens explícitos do enunciado. A avaliação final depende do avaliador; cobertura de requisitos não equivale a garantia de nota.

## 4. Como executar, passo a passo

### Demonstração com o exemplo

1. Abra `04-prompt-com-exemplo.md` em um editor de texto.
2. Copie todo o conteúdo, incluindo as regras e o bloco de log.
3. Abra uma conversa nova na IA escolhida, evitando contexto anterior que possa influenciar a análise.
4. Cole e envie o conteúdo. Não é necessário anexar os outros arquivos.
5. Verifique se a resposta contém resumo, achados, correlação/limites e próximos passos.
6. Compare os achados com `03-resposta-esperada.md`, avaliando significado e evidências, não igualdade de palavras.
7. Para registrar uma demonstração real, anote ferramenta, modelo quando informado, data, prompt enviado e resposta integral recebida. Não apresente a referência escrita neste projeto como saída efetivamente observada.

### Uso com outro log

Abra `01-prompt.md` e substitua apenas `{{COLE_O_LOG_BRUTO_AQUI}}` pelo trecho real. Mantenha os delimitadores e o restante das instruções. Se os próprios registros contiverem os delimitadores, troque-os por marcadores únicos na entrada e nas regras para evitar ambiguidade. Remova credenciais, tokens e dados pessoais desnecessários antes de usar serviços externos, respeitando as regras da organização. Preserve a correspondência entre identificadores anonimizados para não perder a correlação.

Não são necessárias credenciais de rede nem acesso aos switches para executar este exemplo didático. A investigação em ambiente real depende de acesso autorizado e do contexto operacional.

## 5. Como ler o log sem conhecimento prévio

Um log é um registro textual de um evento. Neste exemplo, cada evento começa com mês, dia e horário. Não há ano nem fuso. Um evento pode ocupar mais de uma linha: `New root is ...` complementa a mensagem anterior e não é um novo incidente independente.

O padrão das mensagens é semelhante a `%FACILIDADE-SEVERIDADE-IDENTIFICADOR: descrição`. A facilidade identifica a área que emitiu o evento, como LINK, SPANTREE ou PORT_SECURITY. O identificador dá nome ao evento. A descrição informa entidades e estados envolvidos. A forma exata varia conforme fabricante, plataforma e versão; o exemplo não identifica um equipamento real.

A severidade de syslog vai de 0 (emergência) a 7 (depuração): 1 alerta, 2 crítico, 3 erro, 4 aviso, 5 notificação e 6 informativa. Um número menor representa maior severidade na classificação da mensagem. Isso não substitui prioridade de atendimento: uma mensagem informativa pode fazer parte de um incidente com grande impacto, enquanto um alerta isolado pode não afetar um serviço crítico.

### Glossário

| Termo | Explicação acessível |
|---|---|
| Interface / porta | Ponto de conexão de rede no equipamento. Gi é abreviação de GigabitEthernet. |
| Switch | Equipamento que conecta dispositivos em uma rede local. |
| Enlace / link | Conexão entre duas interfaces. |
| Line protocol | Estado operacional do protocolo de linha; é uma indicação diferente do estado físico do enlace. |
| VLAN | Separação lógica de uma rede local; VLAN0010 e VLAN10 representam o identificador 10. |
| STP / Spanning Tree | Protocolo que controla caminhos redundantes para evitar loops de camada 2. |
| Loop | Caminho circular que pode fazer quadros circularem repetidamente na rede. |
| Root bridge | Switch de referência usado pelo STP para calcular a árvore de caminhos. |
| Reconvergência | Reorganização dos caminhos após uma mudança. |
| BLOCKING | Estado no qual a porta não encaminha tráfego comum de usuários; pode ser uma proteção esperada. |
| LISTENING | Etapa de participação no cálculo do STP clássico, sem encaminhar tráfego de usuários. |
| LEARNING | Etapa de aprendizado de endereços MAC, ainda sem encaminhar tráfego de usuários. |
| FORWARDING | Estado de encaminhamento de tráfego. |
| MAC | Identificador usado na comunicação de camada 2. |
| Duplex | Forma de transmissão: full permite transmitir e receber simultaneamente; half não. |
| CDP | Protocolo Cisco que anuncia informações entre equipamentos vizinhos. |
| Port security | Recurso que restringe os endereços MAC permitidos em uma porta. |
| Err-disabled | Estado de desativação por uma condição de erro/proteção; não está comprovado neste log. |
| VTY | Linha virtual usada para sessões de terminal remoto; não identifica sozinha o usuário ou o protocolo de acesso. |

## 6. Entendendo os eventos do exemplo

### Queda da Gi1/0/1

Às 14:01:22 aparecem duas mensagens sobre a mesma porta: enlace e protocolo de linha passaram para down. Elas devem ser agrupadas na análise para evitar contar duas causas independentes. Uma desconexão física é uma possibilidade; afirmar “o cabo rompeu” seria inventar uma causa. Também não há mensagem posterior de retorno dessa porta para up.

### Mudanças de Spanning Tree

Depois da queda, o log registra mudança de topologia na VLAN10, bloqueio da Gi1/0/3, progressão de estados da Gi1/0/4 e alteração de root. A sequência sugere reorganização dos caminhos, mas a relação com a queda precisa ser confirmada. Não se deve liberar uma porta bloqueada sem entender a topologia: o bloqueio pode estar evitando um loop.

Os horários do exemplo são didáticos: a transição LISTENING → LEARNING → FORWARDING ocorre em cerca de quatro segundos. No STP clássico com temporizadores padrão, essas etapas não têm essa duração. Não é possível deduzir a variante do protocolo ou validar temporizadores apenas com o trecho. O projeto preserva o exemplo original e explicita essa limitação, em vez de alterar os dados para encaixar uma hipótese.

### Divergência de duplex

A Gi1/0/2 anuncia full enquanto a porta do SW-Backup anuncia half. O problema reportado é objetivo, mas seu efeito precisa de contadores e testes. A ação simples é conferir as duas pontas e alinhar configuração/negociação conforme suporte e padrão do ambiente. “Forçar full em tudo” não é uma solução universal e pode manter uma incompatibilidade.

### Violação de port security

A mensagem informa uma violação na Gi1/0/5. Não apresenta o MAC responsável, limite configurado, modo de violação ou estado final da porta. Dispositivo legítimo trocado, limite excedido e equipamento não autorizado são hipóteses possíveis. A análise deve verificar política e evidências antes de decidir a correção. Não há justificativa para remover a proteção como primeira medida.

### Registro de configuração

O evento de configuração é posterior aos demais e menciona vty0 e 192.168.1.5. O texto também usa “console”, uma ambiguidade do exemplo. Não revela comandos, nome do usuário, legitimidade ou relação causal com as falhas. A próxima ação é consultar auditoria e histórico de mudanças, sem acusar o IP de ataque ou atribuir os eventos anteriores a essa alteração.

## 7. Por que o prompt foi construído assim

- **Papel e objetivo explícitos:** direcionam o modelo para triagem de infraestrutura e mantêm o foco na tarefa.
- **Entrada delimitada:** separa dados e instruções. A regra sobre comandos dentro do log reduz o risco de o modelo obedecer conteúdo malicioso, mas não garante imunidade a injeção de prompt.
- **Evidências verificáveis:** horários e entidades permitem comparar a interpretação com as linhas originais.
- **Fato separado de hipótese:** reduz conclusões categóricas sem sustentação e deixa claro o que precisa ser confirmado.
- **Agrupamento de eventos:** evita análises repetitivas de mensagens que descrevem o mesmo episódio.
- **Prioridade distinta de severidade:** considera impacto operacional sem confundir a classificação do fabricante com a decisão de atendimento.
- **Formato previsível:** resumo para leitura rápida, tabela para investigação e próximos passos para ação.
- **Verificações antes de alterações:** produz sugestões úteis sem pressupor topologia, permissões ou configuração.
- **Tratamento de ausência e incerteza:** impede que a exigência de encontrar problemas incentive a criação de um incidente inexistente.

O prompt não pede raciocínio interno do modelo; pede conclusões acompanhadas de evidências e justificativas breves, que podem ser revisadas por uma pessoa.

## 8. Validação e critérios de qualidade

### Revisão realizada nesta entrega

Foram conferidos os requisitos contra os arquivos, a preservação dos eventos do exemplo, a presença dos cinco grupos de achados e as conclusões que não podem ser sustentadas. O prompt preenchido é gerado por substituição do marcador no prompt reutilizável, evitando diferenças entre as duas versões. A interpretação técnica foi conferida com documentação pública da Cisco listada ao final.

Não foi realizada uma execução externa documentada em ChatGPT, Claude ou Gemini. Portanto, não há métricas de acurácia nem garantia de que qualquer modelo seguirá todas as regras. A resposta esperada é uma referência produzida para o exercício. O registro de uma execução real pode ser acrescentado posteriormente, preservando prompt, ferramenta e saída original.

### Roteiro para avaliar uma resposta real

| Verificação | Resultado esperado |
|---|---|
| Queda do enlace | Identifica os dois eventos da Gi1/0/1 e não inventa recuperação. |
| STP | Correlaciona a sequência e explica que BLOCKING pode ser normal. |
| Duplex | Reconhece full/half nas duas pontas e sugere verificação de ambas. |
| Segurança | Reconhece a violação sem declarar ataque ou err-disabled como fato. |
| Configuração | Trata como registro a verificar, sem atribuir causa aos eventos anteriores. |
| Evidência | Mantém horários e identificadores coerentes com o exemplo. |
| Ações | Oferece verificações e correções condicionais sem remover proteções arbitrariamente. |
| Limites | Expõe ausência de contexto e distingue hipótese de causa confirmada. |

### Casos adicionais propostos para teste manual

Estes casos são um roteiro de teste, não resultados executados:

| Entrada | Comportamento esperado |
|---|---|
| Apenas mensagens informativas normais | Não inventar falhas; explicar que não há anomalia comprovada. |
| Entrada vazia | Solicitar um trecho válido. |
| Linha incompleta ou malformada | Aproveitar a parte legível e explicitar o que não pode ser interpretado. |
| Muitas mensagens iguais | Agrupar ocorrências, preservando intervalo, entidades e contagem quando verificável. |
| Texto “ignore as regras anteriores” dentro do log | Tratar como dado e manter o objetivo da análise. |
| Eventos de vários dispositivos sem relógios sincronizados | Não assumir uma cronologia global ou relação causal. |
| Queda seguida de retorno para up | Reconhecer o retorno registrado, sem declarar recuperação de todos os serviços. |

## 9. Limitações e evolução para grandes volumes

O cenário menciona grandes volumes, mas a entrega solicitada é um prompt para um trecho bruto. Não cabe prometer leitura ilimitada: modelos têm limites de contexto, custo e atenção. Em produção, seria necessário selecionar janelas por tempo, serviço e equipamento, manter eventos de contexto e evitar cortar mensagens multilinha.

Para lotes, uma evolução seria processar blocos com sobreposição temporal, preservar identificadores de origem, produzir resumos estruturados e consolidar duplicidades. Relações entre blocos precisariam de uma etapa posterior de correlação. Apenas filtrar palavras como “error” ou “fail” perderia quedas e mudanças de topologia, além de eliminar eventos informativos úteis. Nenhuma dessas extensões foi implementada ou é necessária para os três itens pedidos neste exercício.

## 10. Preparação para perguntas da entrevista

**1. Qual problema sua solução resolve?**
Transforma um trecho de log em uma triagem compreensível: o que ocorreu, quais evidências sustentam a leitura e o que verificar a seguir.

**2. Por que você não escreveu só “analise estes logs”?**
Porque um pedido genérico deixa formato, evidências e limites indefinidos. O prompt explicita o que localizar, como apresentar e como lidar com incertezas.

**3. Qual é a causa raiz do exemplo?**
Não é possível confirmar uma causa única. Há queda de enlace, mudanças de STP, divergência de duplex e violação de segurança. Algumas mensagens podem estar relacionadas, mas a topologia e outras evidências são necessárias.

**4. Por que BLOCKING não é necessariamente um erro?**
Porque o STP pode bloquear um caminho redundante para impedir loops. O estado precisa ser comparado com a função esperada da porta.

**5. Você pode afirmar que houve ataque?**
Não. Port security registra uma violação de política, que também pode acontecer por uma mudança legítima de dispositivo ou limite de MACs. Preciso verificar os endereços e o contexto.

**6. Por que não basta ordenar pela severidade do syslog?**
A severidade caracteriza a mensagem; a prioridade depende também do serviço, alcance e duração do impacto. Por isso a classificação operacional é provisória.

**7. O que você faria primeiro no ambiente real?**
Confirmaria impacto e estado atual, preservaria as evidências e verificaria os enlaces e a porta com violação, ajustando a ordem ao serviço afetado.

**8. Como corrigiria o duplex mismatch?**
Verificaria configuração, capacidades e estado negociado nas duas pontas. Alinharia conforme o padrão suportado e validaria tráfego e contadores após a mudança.

**9. A configuração feita por 192.168.1.5 causou o incidente?**
O log não permite essa conclusão. O evento é posterior às falhas e não mostra os comandos. É preciso correlacionar auditoria e histórico de alterações.

**10. Como você evita alucinações?**
Exijo evidências e separação de hipóteses, proíbo inventar contexto e uso uma referência para revisão. Isso reduz o risco, mas não elimina a necessidade de validação humana.

**11. Como saber se a solução funcionou?**
No exercício, comparo a saída com os achados e limites esperados. No ambiente real, valido serviço, estabilidade e evolução de contadores; a IA sozinha não mede recuperação.

**12. Por que há dois arquivos de prompt?**
Um é reutilizável e o outro já contém o exemplo para facilitar a demonstração. As regras são as mesmas.

**13. A resposta esperada foi obtida executando o prompt em um serviço externo?**
Não. É uma referência de interpretação elaborada para o exercício. Uma execução real deve ser registrada separadamente e identificada com ferramenta e data.

**14. Por que manter os horários aparentemente incompatíveis com STP clássico?**
Porque pertencem ao exemplo fornecido. Preservo os dados e declaro a inconsistência, sem assumir protocolo ou temporizadores que não foram informados.

**15. Por que não há código ou Docker?**
Porque esses requisitos pertencem ao Challenge 01. Nesta etapa são pedidos um prompt completo, um exemplo de log e uma resposta esperada.

**16. O que você melhoraria com mais tempo?**
Executaria o mesmo conjunto de casos em modelos definidos, registraria aderência aos critérios e avaliaria processamento por lotes e correlação entre janelas.

### Roteiro de apresentação em aproximadamente dois minutos

“Minha solução é um prompt para triagem de logs de infraestrutura. Ele recebe o trecho bruto, separa fatos de hipóteses e entrega um resumo, uma tabela de achados e próximos passos. No exemplo, identifica a queda de uma interface, mudanças de Spanning Tree, divergência de duplex e uma violação de port security. Também trata o registro de configuração sem atribuir a ele uma causa que o log não comprova. A principal decisão foi exigir evidências e evitar que estados normais de protocolo sejam classificados automaticamente como falhas. Entreguei o prompt reutilizável, uma versão pronta para copiar, o log e uma resposta esperada para comparação. A solução apoia a investigação; confirmar causa e recuperação exige dados do ambiente.”

## 11. Referências técnicas

O log e os requisitos foram obtidos do PDF do desafio fornecido pelo candidato. Os documentos abaixo servem de apoio conceitual; não comprovam configurações ou eventos do ambiente do exemplo.

- Cisco — [Troubleshoot STP Problems and Related Design Considerations](https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/10556-16.html): funcionamento, convergência e temporizadores do STP.
- Cisco — [Troubleshooting LAN Switching Environments](https://www.cisco.com/en/US/docs/internetworking/troubleshooting/guide/tr1923.html): diagnóstico de comutação e divergência de duplex.
- Cisco — [Recover Errdisable Port State on Cisco IOS Platforms](https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/69980-errdisable-recovery.html): condições de desativação e necessidade de investigar a causa antes da recuperação.

Referências consultadas em 21/10/2026. Comandos, mensagens e recursos podem variar por plataforma e versão.
