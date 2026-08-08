Quero continuar o desenvolvimento do PerformanceLab.

Repositório GitHub, que deve ser sempre a única fonte da verdade:

https://github.com/pedroafrade/PerformanceLab

Usa o plugin GitHub para consultar diretamente os ficheiros atuais antes de sugerires qualquer alteração. Não assumas que o código descrito neste handover já está no repositório: confirma sempre a versão atual no GitHub.

Modo de trabalho

Eu não sou programador e faço manualmente as alterações no VSCode, usando PowerShell.

Por enquanto:

* Tu apenas consultas o GitHub.
* Não escrevas diretamente no repositório.
* Dá-me instruções claras e completas para editar no VSCode.
* Indica sempre o caminho exato do ficheiro.
* Especifica exatamente onde inserir, substituir ou remover código.
* Quando forem muitas alterações num ficheiro, envia o ficheiro completo.
* Um commit lógico de cada vez.
* Alterações pequenas e testáveis.
* Não avances para o commit seguinte até eu confirmar pytest e push.
* Usa linguagem simples e compreensível.
* A UI apenas apresenta informação; a lógica pertence ao domínio.
* Dataclasses de domínio devem ser imutáveis quando apropriado.

No final de cada commit indica sempre:

1. pytest específico;
2. pytest completo;
3. se é necessário reiniciar o Streamlit;
4. o que confirmar visualmente;
5. comandos exatos:

git add ...
git commit -m "..."
git push

Arquitetura

Event → TrainingPlan → WeeklyPlanBuilder → WeeklyPlan

Athlete → AthleteAnalytics → TrainingState / PerformanceProfile / Planner

O Planner trabalha sobre objetos de domínio, não diretamente sobre CTL/ATL/TSB.

O `TrainingPlan` é persistente e contém o plano completo. O `WeeklyPlan` é apenas uma janela móvel de sete dias sobre esse plano.

Objetivo principal atual

Descobrimos uma lacuna estrutural importante: depois de gerar o plano completo, importar uma atividade atualiza o histórico, o RPE, a carga e o `TrainingState`, mas não reajusta automaticamente os treinos futuros.

Atualmente:

* uma atividade é associada visualmente ao dia em que foi realizada;
* o `TrainingState` é invalidado e recalculado;
* o plano futuro permanece estático;
* o Planner só volta a executar quando o utilizador carrega manualmente em “Generate plan”.

O comportamento pretendido é:

1. O utilizador gera o plano completo uma única vez.
2. Quando uma atividade é importada, o sistema compara o treino realizado com o treino planeado desse dia.
3. Classifica o resultado como:

   * pending;
   * missed;
   * equivalent;
   * modified;
   * substitute.
4. Compara carga planeada e carga realizada.
5. Atualiza o estado fisiológico.
6. Adapta apenas os treinos futuros.
7. Preserva treinos passados, atividades realizadas, provas, taper e estrutura global do plano.
8. Um treino falhado também deve provocar adaptação.
9. Ao abrir a aplicação, deve existir uma reconciliação leve para detetar treinos falhados ainda não processados, mas não deve regenerar o plano completo em cada acesso.
10. O sistema terá de guardar até que data ou atividade o plano já foi reconciliado, para não aplicar repetidamente a mesma adaptação.

Estado confirmado antes da mudança de conversa

Foi criado e enviado para o GitHub o primeiro commit desta funcionalidade:

“Assess planned workout outcomes”

Deverão existir:

* `performancelab/training/planning/workout_outcome.py`
* alterações em `performancelab/training/planning/__init__.py`
* `tests/test_workout_outcome.py`

Esse código contém:

* `WorkoutOutcomeStatus`
* `WorkoutOutcome`
* `assess_workout_outcome()`
* tolerância de 20% para considerar cargas equivalentes;
* normalização das modalidades em famílias como running, cycling e swimming;
* cálculo de `load_difference`;
* distinção entre pending, missed, equivalent, modified e substitute.

Próximo commit que estava em preparação

O próximo commit chama-se aproximadamente:

“Assess training plan against history”

Objetivo:

Adicionar ao `TrainingPlan` um método:

```python
assess_outcomes(
    *,
    history: History,
    reference_day: date,
) -> tuple[WorkoutOutcome, ...]
```

Esse método deve:

* indexar os treinos realizados pela data;
* associar cada `PlannedWorkout` ao treino realizado no mesmo dia;
* chamar `assess_workout_outcome`;
* devolver uma coleção imutável de resultados;
* marcar treinos passados sem atividade como `MISSED`;
* manter treinos futuros como `PENDING`.

As alterações previstas eram:

* `performancelab/training/planning/training_plan.py`
* `tests/test_workout_outcome.py`

Ainda não sei se este segundo commit estará no GitHub quando começares. Verifica primeiro:

* se `TrainingPlan.assess_outcomes()` já existe;
* o último commit da branch `main`;
* os conteúdos atuais dos dois ficheiros.

Se não existir, retoma este commit. Se já existir e os testes estiverem enviados, avança para o passo seguinte.

Sequência planeada depois disso

Commit seguinte — Adaptação incremental do futuro:

Criar um objeto de domínio dedicado, por exemplo `TrainingPlanAdapter`, que receba:

* plano atual;
* resultados da reconciliação;
* `TrainingState`;
* data de referência.

Deve devolver ou aplicar uma revisão apenas aos treinos futuros.

Primeiras regras devem ser pequenas e conservadoras:

* treino equivalente: não alterar o futuro;
* treino modificado com carga inferior: não copiar cegamente o treino perdido; distribuir uma fração limitada da diferença pelas semanas seguintes;
* treino com carga superior: reduzir prudentemente a próxima sessão exigente ou introduzir recuperação;
* treino substituído: contabilizar a carga, mas preservar a especificidade necessária da prova;
* treino falhado: não o mover automaticamente para o dia seguinte se isso criar sessões seguidas ou violar recuperação;
* nunca alterar provas, shakeout, taper crítico ou treinos já realizados;
* nunca criar mais de dois dias consecutivos de treino;
* respeitar limites de progressão semanal.

Depois:

* ligar o adaptador à importação em `app/components/import_panel.py`;
* guardar o atleta e o plano adaptado;
* implementar reconciliação de treinos falhados ao entrar na aplicação;
* persistir uma marca de reconciliação para impedir adaptações repetidas;
* só depois mostrar na UI se a sessão foi equivalente, modificada ou substituída.

Contexto adicional já implementado

O projeto já possui, entre outras coisas:

* plano completo persistente até à prova e recuperação posterior;
* Weekly Plan como janela móvel;
* periodização Build, Peak, Taper, Race, Transition e Regeneration;
* calendário com várias provas;
* seleção da prova mais exigente através de prioridade e km-esforço;
* modalidade específica da prova;
* longos preferencialmente ao fim de semana;
* separação de sessões exigentes;
* limites de dias consecutivos;
* progressão de duração semanal;
* progressão de D+ nos longos;
* títulos e subtítulos semânticos;
* Easy Run, Long Run, Hill Run, Tempo Run, LT2 Run, Technique Run, Pre-Race Run, Shakeout, Recovery e Race;
* zonas cardíacas editáveis e persistentes;
* ritmos LT2, Tempo e Easy derivados do histórico;
* estratégia de prova por ritmo, FC, hidratação e nutrição;
* RPE automático;
* importação FIT, FIT.GZ, GPX e Strava CSV;
* carga planeada baseada em duração × RPE semântico;
* aumento conservador da carga planeada de corrida por D+, com 5% por cada 100 D+ e limite máximo de 30%.

Regra importante sobre carga e modalidade

A carga real de qualquer modalidade já entra no estado fisiológico através da duração e do RPE.

Contudo, carga equivalente não significa necessariamente estímulo equivalente:

* Cycling fácil pode substituir parcialmente Easy Run;
* Cycling Z2 pode contribuir para endurance;
* Cycling Z2 não substitui automaticamente LT2 Run;
* um longo de bicicleta não oferece toda a especificidade musculoesquelética de um Long Trail Run;
* modalidade principal continua a ser a modalidade da prova.

Primeira ação na nova conversa

1. Abre o GitHub.
2. Confirma o último commit da branch `main`.
3. Lê diretamente:

   * `performancelab/training/planning/workout_outcome.py`
   * `performancelab/training/planning/training_plan.py`
   * `performancelab/training/planning/__init__.py`
   * `tests/test_workout_outcome.py`
   * `app/components/import_panel.py`
4. Diz-me resumidamente qual foi o último commit concluído.
5. Dá-me apenas as instruções para o próximo commit pequeno.
