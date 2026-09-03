# PerformanceLab — Plano de melhorias das páginas

**Criado em:** 3 de setembro de 2026  
**Estado:** implementação por etapas; consultar o registo de progresso abaixo  
**Destino no repositório:** `docs/APP_PAGE_IMPROVEMENTS_260903.md`

## 1. Objetivo e âmbito

Registar as alterações funcionais e visuais a efetuar nas páginas da aplicação,
com tarefas identificáveis e critérios de aceitação.

Este documento complementa, mas não substitui nem atualiza,
`ROADMAP_PUBLIC_UI_260825.md`. Não altera os requisitos de segurança,
privacidade, deployment ou convite da alpha.

As listas originais descrevem o resultado pretendido. As caixas ainda não
reconciliadas não significam que todas as alterações continuem por implementar.
O registo de progresso distingue confirmação do utilizador de trabalho em curso.

## 2. Regras comuns

- Evitar scroll da página no desktop nas dimensões de referência usadas na
  validação. Registar resolução, zoom e dimensões da janela nessa validação.
- Usar scroll interno nas listas extensas; não esconder conteúdo para cumprir
  o objetivo de uma página compacta.
- Não impor alturas que provoquem sobreposição, corte de texto ou perda de
  botões com conteúdos maiores, zoom ou ecrãs pequenos.
- Interpretar os alinhamentos e posições fixas como posições estáveis no
  layout desktop, não como sobreposições absolutas ao conteúdo.
- No dispositivo móvel, permitir empilhamento e scroll normal da página.
- Manter contraste nos modos claro e escuro. Cores não devem ser a única forma
  de identificar modalidades, tipos de treino ou estados.
- Alterações de apresentação não devem modificar os dados guardados nem as
  fórmulas de cálculo, exceto quando isso for explicitamente definido.
- Preservar autorização, consentimentos, exportação, eliminação e isolamento
  dos dados do atleta.

## 3. Plan

### PLN-01 — Transferir Export Calendar

- [ ] Retirar o botão **Export Calendar** da página Plan.
- [ ] Disponibilizar a mesma funcionalidade na página Calendar, conforme CAL-01.

**Aceitação:** a exportação continua acessível e funcional em Calendar, sem
regressões no conteúdo exportado. Não existe uma segunda cópia do botão em Plan.

### PLN-02 — Plan Weeks num contentor com scroll interno

- [ ] Criar um contentor para as linhas semanais de **Plan Weeks**.
- [ ] Colocar todas as linhas semanais no seu interior.
- [ ] Limitar a altura no desktop e permitir scroll dentro do contentor.
- [ ] Manter acessíveis as semanas, os expansores e os respetivos detalhes.

**Aceitação:** planos mais longos ou semanas expandidas não aumentam
indefinidamente a altura da página; o conteúdo permanece acessível por scroll
interno, rato, toque e teclado.

### PLN-03 — Compactar e alinhar a coluna direita

- [ ] Após remover Export Calendar, reorganizar **Current Phase**, **Current
  Week** e **Latest Adaptation**.
- [ ] Reduzir espaços verticais desnecessários sem comprometer a leitura.
- [ ] Alinhar o limite inferior de Latest Adaptation com o limite inferior do
  contentor Plan Weeks.

**Aceitação:** a composição desktop não gera scroll desnecessário da página.
Validar também ausência de adaptação, textos longos e diferentes fases do plano.

## 4. Activities

### ACT-01 — RPE sem casas decimais

- [ ] Mostrar RPE apenas em unidades inteiras na página Activities.
- [ ] Aplicar a mesma formatação na lista e nos detalhes que apresentem RPE.
- [ ] Preservar a precisão do valor guardado e usado nos cálculos.

**Aceitação:** nenhum RPE visível nesta página apresenta casas decimais;
valores ausentes não são convertidos em zero. Usar arredondamento para
apresentação, com regra consistente e testada, não truncagem silenciosa.

### ACT-02 — Frequência cardíaca a vermelho

- [ ] Alterar para vermelho a linha de frequência cardíaca, em BPM.
- [ ] Manter coerência entre linha, legenda e informação apresentada no hover.

**Aceitação:** a série é legível em ambos os temas e distingue-se das restantes.

### ACT-03 — Posição de Activities Summary

- [ ] Posicionar **Activities Summary** no canto inferior direito do layout
  desktop.
- [ ] Alinhar o seu limite inferior com o limite inferior do contentor de
  atividades.
- [ ] Manter a posição estável perante alterações nos filtros ou na seleção,
  sem sobrepor a lista ou os detalhes.

**Aceitação:** o resumo e a lista mantêm o alinhamento; no móvel, o resumo é
reposicionado no fluxo normal da página.

### ACT-04 — Resumos globais e por modalidade

- [ ] Substituir o conteúdo atual de Activities Summary.
- [ ] Disponibilizar os períodos **Desde sempre**, **1 ano**, **6 meses** e
  **1 mês**.
- [ ] Mostrar resumos globais e resumos por modalidade para o período escolhido.
- [ ] Identificar claramente o período e a modalidade ativos.

**A definir antes da implementação:** conjunto exato de métricas; período
predefinido; significado das janelas temporais; interação com os filtros da
lista; tratamento de atividades sem modalidade ou sem determinados dados.

**Aceitação:** totais verificáveis a partir das atividades do período; estados
vazios explícitos; ausência de dupla contagem. Não somar ou comparar métricas
entre modalidades quando isso não fizer sentido.

### ACT-05 — Melhorar a apresentação do mapa

- [ ] Rever o estilo visual do mapa e do percurso.
- [ ] Apresentar uma proposta visual antes de escolher o estilo final.
- [ ] Melhorar contraste, enquadramento e legibilidade em desktop e móvel.

**A definir:** estilo cartográfico, tratamento da rota e controlos visíveis.
Qualquer mudança de fornecedor deve ser avaliada quanto a privacidade,
atribuição, credenciais e custos antes de ser adotada.

**Aceitação:** mapa mais legível e coerente com a aplicação, preservando a
informação geográfica e o comportamento de atividades sem rota.

## 5. Calendar

### CAL-01 — Receber Export Calendar

- [ ] Integrar o botão transferido de Plan num local coerente com os controlos
  de Calendar.
- [ ] Tornar claro o âmbito da exportação existente. Não alterar silenciosamente
  o conteúdo exportado para apenas o mês visível.

**Aceitação:** navegação mensal, seleção de dia, gestão de eventos e exportação
funcionam em conjunto, sem criar scroll ou desalinhamentos desnecessários.

### CAL-02 — Fundo das sessões de treino

- [ ] Aplicar um fundo cinzento claro às sessões de treino, à semelhança do
  destaque de fundo já usado nas provas.
- [ ] Preservar o fundo vermelho das provas.
- [ ] Adaptar o tom de cinzento ao tema para manter texto e conteúdo legíveis.

### CAL-03 — Cor da linha lateral por tipo de treino

- [ ] Aplicar a seguinte correspondência à linha vertical esquerda de cada treino:

| Tipo de treino | Cor pretendida |
|---|---|
| Easy run e Shakeouts | Verde claro |
| Tempo runs e Intervals | Amarelo |
| Hills | Verde escuro |
| Long runs | Violeta |

- [ ] Manter o nome do tipo de treino visível, sem depender apenas da cor.
- [ ] Definir um estilo neutro para tipos não incluídos nesta lista.

**Aceitação:** classificação consistente, preferencialmente baseada no tipo
estruturado do treino, não apenas em correspondências frágeis do título.
Validar contraste, seleção de dia e coexistência de treino e prova no mesmo dia.

## 6. Development

### DEV-01 — Distância total em vez de Running Pace

- [ ] Substituir **Running Pace**, na primeira linha, por **Total Running Distance**.
- [ ] Adicionar um menu de três pontos no canto superior direito do contentor.
- [ ] Permitir alternar entre distância de corrida e distância de ciclismo.
- [ ] Atualizar título, valor e unidade de acordo com a modalidade escolhida.

**A definir:** persistência da escolha entre sessões e inclusão de trail no
total de corrida. O período deve ser explícito e coerente com o resumo da página.

**Aceitação:** total correto, sem mistura acidental de modalidades; zero e
ausência de dados apresentados de forma inequívoca.

### DEV-02 — Legenda completa de Load and form

- [ ] Verificar no código qual a métrica representada pela terceira linha roxa.
- [ ] Corrigir a legenda para identificar todas as séries visíveis, não apenas
  Fatigue e Fitness.
- [ ] Explicar as siglas, unidades e correspondência com os eixos.

**Aceitação:** cada linha tem nome, cor e significado identificáveis. Se a série
roxa corresponder a Form/TSB, confirmar essa relação no código antes de a
documentar. Não modificar o cálculo apenas para corrigir a legenda.

### DEV-03 — Distinguir barras e linha em Daily training load

- [ ] Usar cores diferentes para as barras e para a linha.
- [ ] Manter as cores coerentes com a legenda e o hover.

**Aceitação:** ambas as séries são distinguíveis nos dois temas e em ecrãs móveis.

## 7. Dashboard

### DSH-01 — Aumentar Weekly Plan

- [ ] Aumentar a largura de **Weekly Plan**.
- [ ] Compactar em largura **Latest Activity** e **Next Event**.

**Aceitação:** o plano semanal ganha espaço sem cortar os dados essenciais dos
outros dois contentores; o layout móvel mantém-se funcional.

### DSH-02 — Training Summary dos últimos 30 dias

- [ ] Limitar Training Summary aos últimos 30 dias, em coerência com Development.
- [ ] Indicar visivelmente o período.

**Aceitação:** a mesma janela temporal e os mesmos dados produzem totais
consistentes nas duas páginas; testar limites de datas e ausência de atividades.

### DSH-03 — Estimated Recovery coerente com Today

- [ ] Substituir o Recovery atual por **Estimated Recovery**, reutilizando a
  lógica e a apresentação de Today.
- [ ] Evitar duplicação de fórmulas entre páginas.

**Aceitação:** para o mesmo atleta, dados e instante de referência, Today e
Dashboard apresentam o mesmo valor e estado de recuperação.

### DSH-04 — Barras de estado com cor significativa

- [ ] Manter a barra de Estimated Recovery e a barra de Training Load.
- [ ] Fazer a cor corresponder à condição atual de cada indicador.
- [ ] Preservar um rótulo textual do estado.

**Aceitação:** cores coerentes com os estados efetivamente calculados; não
inventar novos limiares clínicos ou fisiológicos como parte de uma alteração
visual. Estados sem dados têm representação própria.

### DSH-05 — Retirar o gráfico Performance

- [ ] Retirar o gráfico **Performance** do Dashboard.

**Aceitação:** remover apenas este gráfico, sem confundir com o contentor
Performance Status nem eliminar métricas usadas noutras páginas.

### DSH-06 — Retirar Monthly Summary

- [ ] Retirar **Monthly Summary** do fundo do Dashboard.
- [ ] Eliminar o espaço vazio que possa ficar após a remoção.

## 8. Nova página — Guia de métricas e planos

**Nome proposto na interface inglesa:** Metrics & Plans Guide.  
**Nome descritivo em português:** Guia de métricas e planos.

### GUI-01 — Acesso e organização

- [ ] Criar uma página acessível através da barra lateral.
- [ ] Organizar o conteúdo por temas, com pesquisa ou índice que permita
  encontrar rapidamente um conceito.
- [ ] Usar linguagem simples, apresentando os detalhes técnicos progressivamente.

### GUI-02 — Inventário dos conceitos e fórmulas

- [ ] Inventariar todas as métricas, coeficientes e regras efetivamente usados
  na aplicação, incluindo criação e adaptação de planos.
- [ ] Cobrir carga, forma, recuperação, RPE, zonas de frequência cardíaca,
  distâncias, durações, desnível e outras métricas presentes na interface.
- [ ] Explicar como objetivos, disponibilidade, histórico, fases, tipos de
  sessão e eventos influenciam a criação e adaptação de planos.
- [ ] Distinguir cálculos determinísticos de interpretações do Training Coach.

### GUI-03 — Estrutura de cada explicação

Para cada conceito, documentar:

1. Nome e sigla apresentados na aplicação.
2. Significado em linguagem simples e finalidade.
3. Dados de entrada, unidades, origem e período considerado.
4. Fórmula ou regra efetivamente implementada.
5. Coeficientes, valores predefinidos, limiares e eventual personalização.
6. Exemplo numérico simples com dados fictícios, quando aplicável.
7. Interpretação do resultado, limitações e comportamento sem dados suficientes.
8. Origem: referência externa, heurística do produto ou configuração do utilizador.

**Aceitação:** explicações verificadas contra o código e testes; referências
externas verificadas antes de publicação. Não apresentar heurísticas como
verdades científicas nem resultados estimados como medições clínicas.

### GUI-04 — Manutenção e transparência

- [ ] Definir como manter o guia atualizado quando fórmulas ou coeficientes mudam.
- [ ] Testar exemplos e coerência com as funções reais, evitando apenas testes
  de presença de frases.
- [ ] Não divulgar segredos nem dados de atletas nos exemplos.

## 9. Sequência de execução proposta

1. Plan e Calendar em conjunto para transferir a exportação e ajustar os layouts.
2. Cores e identificação dos treinos em Calendar.
3. Activities: RPE e BPM; depois resumo e proposta visual do mapa.
4. Development: métricas e legibilidade dos gráficos.
5. Dashboard: redistribuição, remoções e uniformização dos indicadores.
6. Guia de métricas e planos, com inventário técnico iniciado durante as etapas
   anteriores para não deixar fórmulas por documentar.

Esta sequência é uma proposta de implementação, não altera a ordem das fases
da roadmap da alpha e não autoriza mudanças adicionais fora deste âmbito.

## 10. Regra de conclusão

Concluir um conjunto lógico de alterações de cada vez, identificando os seus IDs.
Para marcar um item como concluído:

- testes específicos e pytest completo sem erros;
- verificação de apresentação em desktop e móvel, nos modos claro e escuro;
- verificação de dados vazios, textos longos e volumes de dados elevados;
- confirmação visual pelo utilizador quando aplicável;
- commit e push confirmados, com referência registada neste documento.

A criação deste documento não conclui nenhum item e não exige alterações na
roadmap existente. As opções assinaladas como «A definir» devem ser resolvidas
antes de implementar o respetivo comportamento.

## 11. Daily Brief automático — especificação acordada

**Estado:** implementação pendente. Esta secção não activa pedidos ao fornecedor.

### DBR-01 — Geração e reutilização

- Gerar pelo Training Coach na primeira sessão autenticada de cada dia, sem
  botão de geração. Uma única autorização Training Coach abrange comentários
  pedidos em Activities e Daily Brief automático. O texto explica ambos os usos;
  não há uma segunda autorização nem um controlo separado para Daily Brief.
- Atualizar a versão desse consentimento: permissões antigas, apenas manuais,
  exigem confirmação do novo âmbito no mesmo fluxo existente. Não são migradas
  silenciosamente. Uma retirada de permissão bloqueia ambos os usos.
- Definir o dia pelo fuso horário configurado do utilizador, não pelo fuso do servidor.
- Guardar o comentário por atleta, data local e versão do contexto relevante.
  Reutilizá-lo nas sessões seguintes, noutros dispositivos e após reinícios.
- Usar uma reserva persistente e atómica para evitar pedidos duplicados em
  separadores, dispositivos ou instâncias concorrentes.
- Mostrar data/hora, motivo da última geração e estado de actualização.
- Respeitar retirada de consentimento, quotas e limites de custo. Em caso de
  falha, limitar tentativas e apresentar orientação local de Today, identificada
  como alternativa; nunca apresentar texto antigo como actualizado.

### DBR-02 — Alterações relevantes

Regenerar quando mudar o conteúdo que fundamenta a recomendação, nomeadamente:

- regeneração ou adaptação efectiva do plano;
- alteração de objectivo, prova, disponibilidade ou restrições relevantes;
- adição, edição ou eliminação de actividades que alterem a execução de hoje,
  a carga recente ou o restante plano;
- alteração de relatos relevantes em Additional Information.

Não regenerar por navegação, filtros, preferências visuais, login repetido no
mesmo dia ou simples passagem das horas. Uma importação idêntica não deverá
provocar geração. Agrupar alterações de uma mesma importação antes de avaliar
o contexto; não fazer um pedido por ficheiro. O identificador do contexto deve
excluir valores transitórios, como a hora exacta e a recuperação que varia
continuamente com o relógio.

### DBR-03 — Conteúdo e limites

- Resumir o estado actual, a acção recomendada hoje, o restante microciclo e a
  ligação ao plano e objectivo, usando apenas dados efectivamente disponíveis.
- Diferenciar factos, estimativas e relatos do atleta. Notas livres são dados
  não confiáveis para instruções: não podem sobrepor as regras do sistema.
- Não inferir diagnósticos nem assumir que sintomas antigos continuam activos.
  Conservar a data e origem dos relatos; assinalar informação desactualizada ou
  insuficiente.
- Em descanso, admitir sugestões gerais e condicionais de mobilidade ou
  fortalecimento; não prescrever reabilitação, cargas ou exercícios específicos
  para uma aparente lesão sem avaliação adequada.
- A geração não modifica automaticamente o plano nem cria treinos.
- Enviar apenas o contexto necessário, sem ficheiros originais nem credenciais.
  Incluir o novo registo nos mecanismos de exportação, eliminação e isolamento
  de dados do atleta.

### DBR-04 — Integração de interface pendente

- Dashboard, segunda linha: Training Load, Estimated Recovery, Daily Brief,
  Next Workout, Activities Summary (reutilizado de Activities).
- Retirar Physiology e Performance Status desta composição. Next Workout foi
  recuperado por decisão posterior do utilizador e deve ser preservado.
- Corrigir corte superior e ajustar as alturas à janela, mantendo conteúdo
  longo acessível e fluxo normal no móvel.
- Alinhar timeline, selector de dias e sessões de Weekly Plan pela mesma largura.
- Today: retirar os botões Add Activity e Export Calendar do contentor referido
  pelo utilizador como Next Session; verificar os rótulos reais antes de editar.

## 12. Fila futura — Alternativas multimodais ao próximo treino

### ALT-01 — Sessões alternativas comparáveis

**Estado:** planeado para um conjunto posterior; não implementar com Daily Brief.

- Criar um contentor que apresente alternativas ao próximo treino em running,
  cycling e swimming.
- Procurar estímulo fisiológico comparável, não igualdade literal de distância,
  ritmo, duração, frequência cardíaca ou carga entre modalidades.
- Considerar objectivo da sessão, intensidade, volume, experiência do atleta
  em cada modalidade, equipamento, disponibilidade e restrições relatadas.
- Explicar a aproximação usada e o que não é equivalente, incluindo impacto
  mecânico, especificidade para a prova e exigência técnica.
- Não apresentar uma mudança de modalidade como segura para uma lesão apenas
  por ter menor impacto. Se faltarem dados essenciais, explicitar a limitação.
- Mostrar a proposta antes de qualquer substituição; manter o plano original
  até confirmação do utilizador.
- Antes de implementar, definir e testar as regras de equivalência e as suas
  limitações. Não inventar factores universais de conversão.

## 13. Registo de progresso e próximo conjunto

- Dashboard compacto e All Running: commit `c53f570`; testes e apresentação
  confirmados pelo utilizador. Documento publicado em `3ffc5fc`.
- Correção de Weekly Plan neste conjunto: impedir compressão dos blocos dentro
  do cartão de altura fixa, remover margem negativa do selector e separar a
  descrição inferior. Validar visualmente textos longos, seleção de dias,
  navegação, móvel e ambos os temas antes de marcar como concluído.
- DBR-01/DBR-02, etapa inicial: módulo puro de decisão, sem ligação ao login ou
  fornecedor. Inclui chave por atleta/dia local/fuso/contexto, consentimento
  Training Coach versionado, reutilização, invalidação e respeito por backoff.
- O fingerprint recebe projeções mínimas de dados relevantes. O adaptador de
  domínio que selecionará esses dados ainda está por implementar; não passar
  objetos completos do atleta, segredos ou valores transitórios.
- A decisão de gerar representa apenas elegibilidade. Ainda faltam contexto de
  domínio, armazenamento do comentário e reserva atómica,
  quotas, geração, exportação/eliminação e integração na interface. Não ativar a
  geração automática antes de concluir e testar estas salvaguardas.
- Daily Brief continua a apresentar a orientação local de Today nesta etapa.
- Próximo conjunto: adaptar contexto e persistência à arquitetura existente,
  incluindo testes de isolamento entre atletas e concorrência.

### Consentimento unificado — conjunto seguinte

- Usar apenas o consentimento Training Coach existente, na versão v2, para
  Activities e Daily Brief automático; a versão v1 continua no histórico,
  mas não autoriza o novo âmbito sem confirmação explícita.
- Activities e Settings apresentam o mesmo texto e mantêm os botões existentes.
  Não adicionar uma segunda autorização, checkbox ou repositório.
- O armazenamento, a retirada, a exportação e a eliminação reutilizam os
  mecanismos existentes. A política Daily Brief usa a mesma versão central
  e só aceita um registo ativo pertencente ao utilizador autenticado.
- Este conjunto ainda não ativa geração automática nem envia dados ao fornecedor.
  Testes completos e confirmação visual permanecem por validar pelo utilizador.

### Contexto de domínio Daily Brief — conjunto seguinte

- Consentimento unificado: pytest, commit, push e apresentação confirmados pelo
  utilizador. Mantém-se uma única autorização Training Coach.
- Adicionar uma projeção de leitura dos campos reais de Athlete, Workout,
  PlannedWorkout, objetivos, provas, disponibilidade, preferências e restrições.
- Capturar a semana atual e o restante plano, incluindo alterações de prescrição
  e identificação da regeneração. Preservar as doses históricas de atividade
  para detetar alterações que possam afetar o estado calculado.
- Manter relatos de Additional Information separados, com a data da atividade,
  origem e estado não verificado. A data de escrita da nota e o estado atual do
  sintoma são desconhecidos quando não existem no modelo; não os inventar.
- Excluir nome, data de nascimento, credenciais, ficheiros originais, sensores
  brutos, filtros e valores de recuperação que variam apenas com o relógio.
- A projeção é contexto interno para invalidação, não um prompt pronto a enviar.
  Ainda faltam seleção/limites do contexto enviado, integração das métricas
  calculadas, armazenamento/reserva atómica e geração pelo fornecedor.
- Não alterar fórmulas, planos ou dados do atleta. A interface permanece igual
  e a geração automática continua desativada nesta etapa.
- Validar este conjunto com pytest completo antes de registar a conclusão.

### Armazenamento Daily Brief e reservas — conjunto seguinte

- Contexto de domínio: pytest, commit e push confirmados pelo utilizador.
- Adicionar tabela SQL diária e repositório de operações transacionais curtas,
  compatíveis com PostgreSQL e SQLite. Não ligar ainda à aplicação nem ao fornecedor.
- Guardar o último comentário concluído por utilizador/atleta, com chave de
  contexto, dia, fuso, data de geração e motivo. Trata-se de cache do último
  comentário, não de um arquivo ilimitado de todos os dias.
- Reservar atomicamente um pedido por utilizador/atleta, incluindo quando o
  contexto muda durante uma geração. Uma reserva válida bloqueia concorrentes.
- Usar token e prazo da reserva para rejeitar resultados atrasados; respeitar
  backoff após falhas, mesmo se entretanto mudar o contexto.
- Disponibilizar operações de cancelamento, exportação sem tokens e eliminação.
  A ligação destas operações aos fluxos da aplicação ainda falta; não ativar
  geração antes dessa integração e das verificações de consentimento e quota.
- A migração PostgreSQL adiciona a tabela, com eliminação em cascata quando o
  utilizador ou atleta é eliminado. Não modifica os dados de treinos existentes.
- Uma reserva expirada permite recuperar de processos interrompidos, mas não
  garante faturação externa exatamente uma vez após um timeout de resultado
  incerto. O coordenador deverá tratar essas situações conservadoramente.
- Testes funcionais de concorrência e persistência em SQLite; esquema e SQL
  compilados para PostgreSQL. Validar migração na base de testes PostgreSQL antes
  de ativação. O repositório não executa migrações automaticamente.
- Próxima etapa: integrar armazenamento, exportação/eliminação, fuso horário e
  coordenador com consentimento Training Coach unificado, antes da geração real.

### Coordenador Daily Brief — conjunto seguinte

- Armazenamento e reservas: pytest, commit e push confirmados pelo utilizador.
- Adicionar coordenador que verifica autorização de proprietário e consentimento
  Training Coach unificado, carrega contexto, reutiliza cache e obtém reserva.
- Exigir ativação booleana explícita e adaptadores de geração e quota configurados.
  Um pedido em cache não consome quota nem volta a chamar o gerador.
- Recarregar contexto antes da geração e antes da gravação; descartar resultado
  se o plano/dados mudarem, se o dia local mudar, se a autorização for retirada
  ou se a reserva expirar.
- O gerador injetado recebe contexto interno, não um prompt pronto. O adaptador
  Gemini terá de minimizar os dados, aplicar limites/regras, controlar timeout
  inferior à duração da reserva e registar utilização.
- Os testes usam armazenamento SQL real e gerador simulado; nenhuma chamada ao
  fornecedor. O coordenador ainda não é chamado pelo login ou Dashboard.
- Ainda faltam integração com a quota real, adaptador Gemini, fuso persistente,
  configuração do armazenamento e ligação dos fluxos de retirada de consentimento,
  exportação e eliminação. Não ativar antes de concluir essas integrações.
- Falhas devolvem estados estáveis sem expor exceções, credenciais ou contexto.
  A interface poderá continuar a mostrar orientação local de Today nesses estados.
