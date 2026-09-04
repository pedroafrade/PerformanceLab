# PerformanceLab — Melhorias das páginas

**Atualizado em:** 4 de setembro de 2026

**Estado:** resumo do que está concluído e da fila de trabalho pendente

**Destino:** `docs/APP_PAGE_IMPROVEMENTS_260903.md`

## 1. Objetivo

Manter uma lista curta e atualizada das melhorias da interface da aplicação.
Este documento complementa `ROADMAP_PUBLIC_UI_260825.md` e não altera os
requisitos de segurança, privacidade ou deployment.

## 2. Regras comuns

- Evitar scroll desnecessário no desktop; usar scroll interno em listas longas.
- Não cortar nem sobrepor conteúdo para reduzir a altura das páginas.
- Permitir empilhamento e scroll normal no móvel.
- Validar os temas claro e escuro e não comunicar estados apenas através da cor.
- Reutilizar componentes e a mesma fonte de dados quando a informação aparece
  em várias páginas.
- Não alterar fórmulas ou dados guardados através de mudanças apenas visuais.
- Preservar consentimento, isolamento, exportação e eliminação dos dados.

## 3. Estado atual confirmado

Os conjuntos seguintes foram implementados, validados por testes e confirmados
visualmente no Streamlit durante esta sequência de trabalho.


## 4. Trabalho pendente

### Prioridade 1 — Consistência do plano e componentes partilhados

#### P1.1 — Duração coerente das sessões

- Corrigir diferenças de duração da mesma sessão entre Plan, Calendar, Today e
  Dashboard, incluindo o Long Run observado com `1h00` e `1h40`.
- Usar uma única duração estruturada em todas as páginas.
- Em Easy Runs e Long Runs, incluir Warm-up e Cooldown na duração total sem os
  destacar como blocos adicionais da corrida contínua.

#### P1.2 — Estado fisiológico consolidado

- Avaliar se a evolução parcial por hora de Estimated Recovery é válida para
  outras métricas, incluindo Training Load; não simular precisão inexistente.
- Reunir Estimated Recovery, Training Load e Form num componente reutilizável
  no Dashboard e em Development.
- Manter valor, unidade, instante de referência e estado textual.

#### P1.3 — Próximo evento partilhado

- Criar um único componente Next Event / Upcoming Events.
- Usar uma variante compacta no Dashboard e a variante completa, com gestão e
  lista de eventos, em Calendar.

### Prioridade 2 — Plan

- Fazer Plan Weeks abrir com a semana atual no topo, mantendo as anteriores
  acessíveis acima e sem interromper a navegação manual.
- Mostrar em Latest Adaptation a data da sessão alterada e distingui-la da data
  em que a adaptação foi aplicada.
- Mostrar curvas distintas para plano original, plano atual adaptado e treino
  realizado; suavizar apenas a curva realizada e explicar todas as séries.
- Dividir a área inferior entre Plan Weeks e Latest Adaptation; colocar o novo
  componente Next Event no espaço anteriormente ocupado por Latest Adaptation.
- Criar histórico de versões do plano, comparação e recuperação segura de uma
  versão anterior.

### Prioridade 3 — Today e aconselhamento

- Substituir Today's Recommendation pelo Daily Brief já guardado, sem provocar
  uma segunda geração.
- Criar **Planned Session Equivalents** com alternativas de running, cycling e
  swimming de impacto fisiológico aproximado, indicando diferenças mecânicas e
  de especificidade antes de qualquer substituição.
- Criar **Recovery Log** para registo histórico de dores, lesões e patologias.
  Antes do código, definir edição, retenção, exportação, eliminação, acesso e
  tratamento destes dados de saúde; não inferir diagnósticos.
- Criar **Strategy Adviser** para sugerir dias potencialmente adequados a certos
  exercícios com base no histórico, plano e recuperação, deixando explícitos os
  limites e sem apresentar garantias clínicas.

### Prioridade 4 — Dashboard

- Dar maior destaque ao Daily Brief.
- Compactar Activities Summary sem remover filtros, totais ou estados vazios.
- Corrigir qualquer sobreposição ainda observada na descrição inferior de
  Weekly Plan e validar textos de treino longos.

### Prioridade 5 — Guia de métricas e planos

- Inventariar e documentar as restantes métricas, coeficientes e regras usados
  na criação e adaptação de planos.
- Para cada conceito, indicar significado, entradas, unidades, período, fórmula,
  coeficientes, exemplo, interpretação, limitações e origem.
- Distinguir cálculos determinísticos de interpretações do Training Coach.
- Criar testes que comparem exemplos do guia com as funções reais.

## 5. Decisões necessárias antes da implementação

- **Recovery Log:** modelo, retenção e proteção de dados de saúde.
- **Strategy Adviser:** exercícios abrangidos, regras e relação com o Training
  Coach.
- **Plan recovery:** retenção e comparação das versões do plano.
- **Evolução horária da carga:** validade matemática e instante de referência.
- **Planned Session Equivalents:** métricas de equivalência e limites de uso.

## 6. Critério de conclusão

Um item só passa para a secção concluída depois de:

1. testes específicos e suite completa sem erros;
2. `git diff --check` sem problemas;
3. validação visual no Streamlit em desktop e móvel, nos temas claro e escuro,
   sempre que exista alteração de interface;
4. confirmação de estados vazios, textos longos e dados incompletos;
5. commit e push confirmados.

## 7. Próximo conjunto recomendado

Implementar primeiro **P1.1 — Duração coerente das sessões**, porque corrige uma
divergência de dados visível em várias páginas e cria a base necessária para as
futuras alternativas de sessão.
