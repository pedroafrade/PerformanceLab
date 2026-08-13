# PerformanceLab — handout de continuidade

Atualizado em 13 de agosto de 2026.

## 1. Fonte da verdade

O repositório GitHub é sempre a única fonte da verdade:

https://github.com/pedroafrade/PerformanceLab

Antes de sugerir qualquer alteração:

1. usar o plugin GitHub;
2. confirmar o último commit da branch `main`;
3. ler diretamente no GitHub todos os ficheiros relevantes;
4. não assumir que uma alteração descrita neste handout está no repositório sem a confirmar.

Este handout resume o estado confirmado no momento da mudança de conversa, mas não substitui a consulta do GitHub.

Último commit confirmado:

```text
0e0a341 Ignore athlete backups during plan export
```

## 2. Modo de trabalho obrigatório

O utilizador não é programador e aplica manualmente as alterações no VSCode, utilizando PowerShell.

Por enquanto:

- consultar o GitHub, mas não escrever diretamente no repositório;
- fornecer instruções simples, completas e inequívocas;
- indicar sempre o caminho exato de cada ficheiro;
- especificar exatamente onde inserir, substituir ou remover código;
- quando existirem muitas alterações num ficheiro, entregar o ficheiro completo;
- fazer apenas um commit lógico de cada vez;
- manter as alterações pequenas e testáveis;
- não avançar até o utilizador confirmar pytest, commit e push;
- nunca usar `git add .`;
- nunca adicionar a pasta local `data/`;
- não adicionar ficheiros exportados, temporários ou não relacionados;
- preservar alterações locais do utilizador;
- a UI apresenta e encaminha informação;
- a lógica pertence ao domínio;
- usar dataclasses imutáveis quando apropriado.

No final de cada commit indicar sempre:

1. pytest específico;
2. pytest completo;
3. se é necessário reiniciar o Streamlit;
4. o que confirmar visualmente;
5. comandos exatos de `git add`, `git commit` e `git push`.

## 3. Arquitetura de referência

```text
Event → TrainingPlan → WeeklyPlanBuilder → WeeklyPlan

Athlete → AthleteAnalytics
        → TrainingState
        → PerformanceProfile
        → Planner
```

Regras importantes:

- o Planner trabalha sobre objetos de domínio;
- o Planner não deve tomar decisões diretamente sobre valores isolados de CTL, ATL ou TSB;
- `TrainingPlan` é persistente e contém o plano completo;
- `WeeklyPlan` é apenas uma janela móvel de sete dias;
- atividades concluídas atualizam histórico, carga e estado fisiológico;
- a reconciliação adapta apenas o futuro;
- provas, taper crítico, treinos passados e atividades realizadas são preservados;
- o estado fisiológico atual não deve ser projetado para semanas futuras como se continuasse invariável;
- decisões diárias não alteram automaticamente o plano persistente.

## 4. Estado funcional atual

O PerformanceLab consegue:

- gerar e persistir um plano completo;
- planear até à prova e recuperação posterior;
- trabalhar com várias provas;
- distinguir prova principal e provas secundárias;
- reconciliar atividades realizadas com sessões planeadas;
- classificar resultados como:
  - `pending`;
  - `missed`;
  - `equivalent`;
  - `modified`;
  - `substitute`;
- adaptar apenas sessões futuras;
- preservar provas, taper, passado e estrutura global;
- impedir a aplicação repetida da mesma reconciliação;
- calcular carga planeada e realizada;
- incluir atividades não planeadas no estado fisiológico;
- apresentar Today, Plan, Activities, Calendar, Development e Settings;
- importar FIT, FIT.GZ, GPX e Strava CSV;
- editar e eliminar atividades;
- abrir o editor de atividades numa caixa modal;
- mostrar hora de início da atividade nos detalhes;
- usar hora real do treino na estimativa de recuperação;
- atualizar recovery intradiário;
- mostrar recovery, form e carga coerentemente em Today e Development.

## 5. Training Coach

O Training Coach está implementado em Activities.

Inclui:

- contexto factual da atividade;
- sensores disponíveis;
- ambiente apenas quando existe no ficheiro;
- treino recente;
- fase do plano;
- próxima prova;
- especificidade de distância e desnível;
- sinais determinísticos;
- feedback subjetivo fornecido pelo atleta;
- contrato de geração estruturado;
- integração com Gemini;
- persistência da interpretação;
- regeneração explícita;
- tratamento de indisponibilidade ou erro;
- cartão com altura fixa e scroll interno;
- texto estruturado em parágrafos;
- secções de evidência e limitações;
- campo `Additional information`.

Regras preservadas:

- nunca inventar sintomas;
- nunca inventar dor, lesões, sono, rigidez, stress ou motivação;
- não inventar temperatura, humidade ou terreno;
- distinguir factos, sinais determinísticos e interpretação;
- readiness e recovery atuais só contextualizam a atividade mais recente;
- não atribuir estado fisiológico atual a atividades históricas.

Fornecedor atual:

```text
Google Gemini
```

Variável de ambiente:

```text
GEMINI_API_KEY
```

A aplicação utiliza o serviço online. A inferência não é executada no dispositivo móvel.

## 6. Activities

A lista de atividades mantém o comportamento original de seleção da linha, mas apresenta os campos numa grelha visual alinhada.

Campos:

1. data;
2. modalidade;
3. título;
4. distância;
5. duração;
6. elevação;
7. RPE;
8. resultado.

Decisões visuais implementadas:

- sem cabeçalho de tabela;
- sem checkbox;
- toda a linha é selecionável;
- separadores apenas horizontais;
- a atividade abre entre as linhas;
- botão transparente sobre a grelha;
- altura das linhas compactada;
- título duplicado removido dos detalhes;
- botões Edit e Delete lado a lado;
- botões colocados no final do conteúdo aberto;
- edição numa caixa modal;
- eliminação com confirmação.

## 7. Recovery intradiário

Recovery deixou de ser apenas uma estimativa diária.

O estado pode ser calculado para uma hora de referência e considera:

- hora da última atividade;
- duração da atividade;
- tempo decorrido desde o fim;
- decaimento intradiário de ATL e CTL;
- evolução do balance ao longo do dia;
- horas desde a última sessão;
- fallback diário quando a atividade não possui hora fiável.

A UI apresenta:

- recovery score;
- recovery balance;
- horas desde a última sessão;
- hora da estimativa;
- indicação de fallback diário quando necessário.

Os valores são coerentes entre Today e Development.

Exemplo visual confirmado em 13/08/2026:

```text
Recovery: 19
Balance: +19.1
Hours since last session: 34
Form: -30.9
Recent/acute load: 329.9 / 330
```

## 8. Recomendação diária

Foi criada uma decisão diária determinística e independente do plano persistente.

Decisões disponíveis incluem:

- treino concluído;
- seguir o plano;
- reduzir volume;
- executar apenas treino fácil;
- executar apenas recuperação;
- preservar a recuperação planeada;
- descansar;
- rever explicitamente uma prova.

A recomendação diária:

- não modifica silenciosamente o `TrainingPlan`;
- pode fornecer uma adaptação temporária apenas para execução;
- não recomenda repetir uma sessão já realizada;
- protege provas de substituição automática;
- preserva uma Recovery Run curta e adequada;
- mantém o descanso como opção quando o feedback subjetivo o justifica.

Estado visual confirmado:

```text
Follow the recovery session
```

Para uma sessão planeada:

```text
Recovery Run
20 min
Very easy
```

A caixa redundante de substituição não aparece quando a sessão planeada já corresponde à necessidade de recuperação.

## 9. Plano de treino

Foram corrigidos vários problemas do gerador:

- Easy Runs deixaram de ultrapassar desproporcionalmente os Long Runs;
- volume fácil depende da fase;
- Long Runs usam duração e distância;
- distância dos Long Runs aparece no plano;
- alvos futuros usam histórico estável;
- fadiga atual não é projetada para semanas futuras;
- provas secundárias não substituem a fase da prova principal;
- recuperação após provas depende da importância e exigência;
- início do taper preserva alguma especificidade de trail;
- distribuição em semanas de prova foi melhorada;
- blocos de três dias consecutivos antes de provas são evitados;
- transição de Regeneration para Peak foi suavizada;
- intensidade é consciente do terreno;
- Tempo Run de trail inclui referência cardíaca numérica;
- nutrição de prova depende de tolerância testada;
- sessões de prova não usam TSB atual como previsão futura.

O plano atual apresenta as fases:

```text
Regeneration → Peak → Taper → Regeneration
```

A primeira semana contém:

```text
Recovery Run
Easy Run
```

O plano progride para a prova principal:

```text
III Trail Pé Firme
27 de setembro de 2026
```

## 10. Gráficos e adaptações do plano

A linha `Completed` do gráfico de carga:

- representa todas as atividades realizadas;
- não apenas treinos planeados concluídos;
- inclui atividades `Unplanned`;
- inclui atividades `Outside Plan`;
- inclui substituições;
- inclui atividades realizadas na semana inicial mesmo quando anteriores à data exata de início do novo plano.

Foi confirmado visualmente que a atividade de bicicleta de 12/08 aparece em verde antes do início do plano em 13/08.

`Latest adaptation`:

- mostra apenas a próxima adaptação ainda relevante;
- ignora adaptações de sessões passadas ou concluídas;
- apresenta estado vazio quando não existe uma adaptação futura aplicável.

Não assumir que um estado vazio é necessariamente um erro sem verificar primeiro os registos persistidos de adaptação.

## 11. Estratégias e fisiologia futura

`CoachContext` distingue:

- fisiologia atual válida;
- referências históricas estáveis;
- contexto de semanas futuras.

Quando `physiology_is_current` é falso:

- readiness atual não deve determinar a semana futura;
- TSB atual não deve reduzir automaticamente semanas futuras;
- referências históricas de volume, ritmo e tolerância continuam disponíveis.

`MaintenanceStrategy` usa agora `should_reduce_volume` de forma consistente para:

- volume;
- intensidade;
- dias de recuperação;
- `recovery_priority`.

O fallback para TSB existe apenas para contextos antigos ou objetos de teste que não fornecem o sinal atual.

## 12. Exportação do plano

O script:

```text
export_training_plan.py
```

ignora ficheiros de backup em:

```text
data/athletes/
```

Exclui nomes como:

```text
athlete.backup.json
athlete.backup-adaptation.json
```

e escolhe apenas o ficheiro principal:

```text
athlete.json
```

Existem testes que:

- confirmam que backups são ignorados;
- confirmam que o ficheiro principal é exportado;
- impedem fallback silencioso para um backup;
- executam o exportador numa pasta temporária;
- não alteram o `PLANO_DE_TREINO.txt` local.

## 13. Dados locais e Git

Nunca adicionar:

```text
data/
PLANO_DE_TREINO.txt
alteracoes_planning.txt
ficheiros de patch temporários
backups locais
```

Nunca usar:

```powershell
git add .
```

Antes de cada commit:

```powershell
git status --short
git diff --check
```

Adicionar apenas os ficheiros explicitamente pertencentes ao commit.

## 14. Estado dos testes

No fim da sequência, o utilizador confirmou repetidamente:

- pytest específico sem erros;
- pytest completo sem erros;
- commit e push concluídos;
- Streamlit visualmente correto.

Não assumir o número exato atual de testes sem executar novamente o pytest ou consultar CI.

## 15. Trabalho pendente

### Prioridade 1 — continuar a auditoria científica do plano

O plano melhorou significativamente, mas ainda não deve ser declarado “perfeito”.

Próximas verificações:

1. confirmar progressão semanal de carga, duração, distância e D+;
2. verificar espaçamento entre sessões exigentes;
3. verificar relação entre provas secundárias e prova principal;
4. rever o último Long Run antes da prova;
5. rever redução de volume no taper;
6. confirmar ausência de períodos excessivamente longos sem treino;
7. validar sessões de recuperação posteriores às provas;
8. verificar se as prescrições são executáveis por FC, duração, terreno e RPE;
9. confirmar que regenerar o mesmo contexto produz estrutura estável;
10. validar o plano com diferentes disponibilidades e históricos.

Fazer uma correção de domínio por commit, sempre acompanhada de testes.

### Prioridade 2 — feedback subjetivo diário

`Additional information` já permite complementar uma atividade específica.

Ainda pode ser avaliada uma entrada diária em Today para dados anteriores ao treino:

- sono;
- rigidez;
- dor;
- stress;
- motivação;
- soreness;
- disponibilidade subjetiva.

Antes de implementar, definir:

- modelo de domínio;
- validade temporal;
- persistência;
- relação com `AthleteFeedback`;
- diferença entre feedback diário e feedback pós-atividade;
- regras que impedem inferências médicas.

### Prioridade 3 — adaptações futuras visíveis

Investigar, sem assumir erro, por que motivo `Latest adaptation` pode estar vazio.

Verificar:

- se existem adaptações persistidas;
- se pertencem a sessões futuras;
- se a sessão adaptada ainda existe;
- se o resultado está `pending`;
- se a regeneração do plano removeu registos anteriores;
- se uma recomendação diária temporária deveria ou não criar adaptação persistente.

### Prioridade 4 — primeira aplicação pública

Depois da correção funcional e científica:

- rever autenticação e autorização;
- rever persistência multiutilizador;
- remover dependência da pasta local `data/`;
- definir armazenamento seguro;
- definir gestão de segredos;
- preparar comportamento responsivo;
- testar Android e iOS;
- definir limites e custos do fornecedor de IA;
- criar monitorização e recuperação de erros;
- rever privacidade e eliminação de dados.

Consultar também:

```text
docs/ROADMAP_PUBLIC_UI.md
```

## 16. Primeira ação obrigatória numa nova conversa

1. usar o plugin GitHub;
2. confirmar o último commit da `main`;
3. verificar se `0e0a341 Ignore athlete backups during plan export` continua a ser o último commit;
4. ler diretamente no GitHub os ficheiros relevantes para o pedido atual;
5. executar apenas verificações não destrutivas;
6. resumir o estado encontrado;
7. propor apenas um commit lógico;
8. não avançar até o utilizador confirmar pytest, commit e push.

Se o objetivo continuar a ser a auditoria do plano, começar por ler:

```text
performancelab/coaching/context.py
performancelab/coaching/analyzer.py
performancelab/coaching/structure_generator.py
performancelab/coaching/workout_generator.py
performancelab/training/planning/planner.py
performancelab/coaching/strategies/
tests/coaching/
```

Também solicitar ou gerar uma exportação atual do plano para analisar:

- semanas;
- fases;
- sessões;
- distâncias;
- durações;
- D+;
- cargas;
- provas;
- intervalos entre treinos.

## 17. Formato obrigatório de cada entrega

Começar com um título claro do commit ou passo.

Terminar sempre com:

1. pytest específico;
2. pytest completo;
3. indicação sobre reinício do Streamlit;
4. confirmação visual esperada;
5. comandos exatos de `git add`;
6. comando de `git commit`;
7. `git push`.

Não misturar commits e não avançar automaticamente para o seguinte.