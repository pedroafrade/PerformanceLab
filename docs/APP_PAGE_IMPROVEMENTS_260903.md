# PerformanceLab — Melhorias das páginas

**Atualizado em:** 10 de setembro de 2026

**Estado:** resumo consolidado do trabalho concluído e da fila prioritária

**Destino:** `docs/APP_PAGE_IMPROVEMENTS_260903.md`

## 1. Objetivo

Manter uma lista curta e atualizada das melhorias da interface. Este documento
complementa `ROADMAP_PUBLIC_UI_260825.md` e não altera os requisitos de
segurança, privacidade ou deployment.

## 2. Regras comuns

- Evitar scroll desnecessário no desktop e não cortar conteúdo para reduzir a
  altura das páginas.
- Permitir empilhamento e scroll normal no móvel.
- Validar os temas claro e escuro e não comunicar estados apenas através da cor.
- Reutilizar componentes e a mesma fonte de dados entre páginas.
- Não alterar fórmulas ou dados guardados através de mudanças apenas visuais.
- Preservar consentimento, isolamento, exportação e eliminação dos dados.
- Uma alteração ao plano só está concluída quando célula, gráfico, histórico,
  eventos e armazenamento persistente representam o mesmo estado.
- Sessões concluídas e dias anteriores à data atual são visíveis, mas não podem
  ser alterados retroativamente no Plan Builder.

## 3. Estado atual confirmado

Os conjuntos seguintes foram implementados, validados por testes e confirmados
visualmente no Streamlit.

### 3.1 — Dados e componentes partilhados

- A duração das sessões contínuas foi normalizada entre Plan, Calendar, Today e
  Dashboard, incluindo Warm-up e Cooldown no total.
- Estimated Recovery, Training Load e Form usam uma apresentação fisiológica
  consolidada e indicadores específicos por métrica.
- Upcoming Events tem uma apresentação partilhada, com variante compacta no
  Dashboard e gestão a partir de Calendar e Plan.
- O Daily Brief ganhou maior destaque no Dashboard.

### 3.2 — Plan e Plan Progression

- Plan Weeks abre na semana atual e preserva o acesso às semanas anteriores.
- Plan Adaptation compara a sessão planeada com a ajustada, incluindo datas e
  explicação.
- Plan Progression distingue plano original em azul, treino realizado em verde
  contínuo, projeção adaptada em verde tracejado, totais semanais e provas.
- A curva realizada liga-se à projeção adaptada na data atual.
- Plan Adaptation e Upcoming Events são apresentados lado a lado.
- Manage Events pode ser aberto em Plan através de um botão de edição alinhado
  com o botão de ajuda de Plan Adaptation.
- Criar, alterar ou eliminar eventos atualiza o plano e as projeções; eliminar
  exige confirmação em diálogo.

### 3.3 — Plan Builder

- O diálogo usa o espaço disponível sem scroll residual nem corte dos botões
  inferiores no desktop e suporta os temas claro e escuro.
- A timeline completa reutiliza a lógica de Plan Progression.
- As semanas começam à segunda-feira e abrangem o horizonte original.
- Sessões realizadas são mostradas nos dias passados com opacidade reduzida e
  sem possibilidade de edição.
- Sessões futuras podem ser movidas, adicionadas, editadas, duplicadas no mesmo
  dia ou eliminadas.
- A edição ocorre em pop-up e suporta duração, distância, desnível, intensidade,
  alvo e estrutura do exercício.
- Trail Run tem estrutura própria, distinta de Hill Reps.
- A carga pode ser estimada a partir de duração, distância e desnível sem exigir
  esforço explícito.
- Alterações do rascunho atualizam células e timeline e são persistidas por
  Generate Plan.
- O impacto fisiológico é calculado imediatamente e acompanhado por uma
  recomendação.
- A revisão antes de guardar apresenta a carga anterior e nova por semana,
  diferenças absolutas e percentuais, precauções, bloqueios e recomendações.
- Reset changes, Cancel e Generate plan mantêm a mesma altura e alinhamento no
  rodapé do diálogo.
- Dias concluídos, sessões realizadas e provas não podem ser tratados como
  sessões futuras editáveis.

### 3.4 — Versões, restore e adaptação

- Plan recovery apresenta revisões recuperáveis do plano.
- Plan recovery mantém as dimensões de Build Plan, usa scroll interno e mostra
  inicialmente apenas as seis revisões distintas mais recentes da linhagem
  ativa; snapshots repetidos e ramos abandonados não poluem a lista.
- O Restore apresenta previamente sessões adicionadas, removidas, movidas ou
  editadas, alterações de eventos, horizonte e versões posteriores afetadas.
- Restore preserva o horizonte original, sessões, plano original e snapshots
  dos eventos associados e remove versões posteriores ao ponto restaurado.
- Eventos restaurados recuperam a identidade e os dados originais; sessões de
  preparação não são promovidas a Upcoming Events.
- A aplicação deteta diferenças entre o estímulo planeado e o realizado.
- As sugestões de reequilíbrio ficam limitadas ao bloco competitivo ativo e
  respeitam recuperação e proximidade das provas.
- Plan Adaptation e Plan Progression resolvem a sessão a partir da mesma revisão.
- Adaptações aplicadas são guardadas como revisões recuperáveis.
- A ligação entre treino realizado e projeção usa diretamente as sessões reais
  adjacentes, sem criar uma carga ou inflexão artificial na data atual.
- Bloqueios e recomendações do Plan Builder são apresentados integralmente num
  pop-up temporário na camada superior do diálogo, sem alterar o layout.
- Cada gesto do quadro recebe confirmação explícita; se o Streamlit não
  responder, o estado de espera é libertado automaticamente para não bloquear
  as ações seguintes.
- A gravação rejeita rascunhos desatualizados ou sem diferenças, mantém o
  rascunho quando o repositório falha e apresenta uma revisão resumida antes da
  confirmação.
- O Restore apresenta também a lista concreta de sessões e eventos afetados,
  num pop-up compacto com expansão apenas para alterações longas.
- Alterações ao plano, histórico, eventos e Restore invalidam centralmente as
  vistas derivadas e identificam a revisão ativa, evitando dados antigos entre
  Plan, Calendar, Today e Daily Brief.

### 3.5 — Recomendações fisiológicas acionáveis

- A avaliação considera o plano completo após mover, criar, editar ou eliminar
  sessões: carga semanal, intensidade consecutiva, recuperação, sessão longa,
  taper e proximidade de prova.
- Resultados distinguem informação, precaução e bloqueio e identificam a regra,
  semana, sessões, AU e percentagem responsáveis.
- Limites percentuais são combinados com diferenças absolutas para não bloquear
  artificialmente semanas de carga baixa.
- Bloqueios de movimentos apresentam uma alternativa determinística segura,
  aplicável diretamente no aviso com um clique.
- Recomendações mantêm caráter informativo e não constituem garantia clínica.

## 4. Trabalho pendente

### Prioridade 1 — Integridade transacional do Plan Builder

- Criar testes de fluxo completo para mover, adicionar, editar e eliminar uma
  sessão, verificando na mesma execução célula, curvas, rascunho, persistência
  após Generate Plan e estado após rerun/refresh.
- Completar testes integrados de navegação entre Plan Builder, Plan
  Progression, Plan Weeks, Calendar e Today após cada tipo de alteração.

### Prioridade 3 — Histórico e restore transparentes

- Acrescentar testes integrados para restore de sessões, eventos, horizonte,
  curva original e projeção adaptada.

### Prioridade 4 — Today e aconselhamento

- Substituir Today's Recommendation pelo Daily Brief guardado, sem uma segunda
  geração.
- Criar **Planned Session Equivalents** com alternativas de running, cycling e
  swimming de impacto aproximado, explicitando diferenças e limites.
- Definir modelo, retenção, exportação, eliminação e proteção de dados antes de
  implementar **Recovery Log**.
- Criar **Strategy Adviser** com limites explícitos e sem garantias clínicas.

### Prioridade 5 — Guia de métricas e planos

- Documentar métricas, coeficientes e regras usados na criação e adaptação.
- Indicar entradas, unidades, período, fórmula, exemplo, interpretação,
  limitações e origem.
- Distinguir cálculos determinísticos de interpretações do Training Coach.
- Testar os exemplos do guia contra as funções reais.

## 5. Decisões necessárias

- **Recovery Log:** modelo, retenção e proteção de dados de saúde.
- **Strategy Adviser:** regras e relação com o Training Coach.
- **Planned Session Equivalents:** métricas e limites de equivalência.
- **Recomendações automáticas:** definir aviso, aplicação direta e bloqueio.
- **Retenção de revisões:** decidir se versões removidas após restore devem ter
  recuperação técnica temporária.

## 6. Critério de conclusão

Um item só passa para concluído depois de:

1. testes específicos e `pytest -q` sem erros;
2. `git diff --check` sem problemas;
3. validação visual no Streamlit em desktop e móvel, nos temas claro e escuro;
4. confirmação de estados vazios, textos longos e dados incompletos;
5. confirmação de que células, gráficos, eventos e armazenamento apresentam a
   mesma revisão;
6. commit e push confirmados.

## 7. Próximo conjunto recomendado

Implementar num único commit a **Prioridade 1 — Integridade transacional do Plan
Builder**. É a fundação para recomendações fisiológicas e histórico seguros:
nenhuma destas funcionalidades deve depender de ações repetidas nem divergir
depois de rerun ou refresh.
