# PerformanceLab — Fundamentos Científicos do Treino

**Estado:** documento de referência  
**Âmbito:** princípios científicos, métricas atuais, heurísticas e limites de interpretação  
**Atualizado:** 2 de agosto de 2026

---

## 1. Objetivo

Este documento define como o PerformanceLab transforma dados de treino em métricas, interpretações e recomendações.

Serve para:

- tornar explícitas as fórmulas atualmente utilizadas;
- distinguir modelos científicos de heurísticas do produto;
- impedir que aproximações sejam apresentadas como medições diretas;
- estabelecer requisitos de validação para novas métricas;
- proteger o atleta de recomendações com falsa precisão;
- manter o motor científico independente da interface e de modelos de linguagem.

Este documento não substitui avaliação médica, diagnóstico, tratamento ou acompanhamento profissional. O PerformanceLab é uma ferramenta de apoio à compreensão e decisão de treino.

---

## 2. Princípios científicos

### 2.1. Medir, estimar e interpretar são operações diferentes

O sistema deve identificar claramente a natureza de cada valor:

| Natureza | Exemplo | Regra de comunicação |
|---|---|---|
| Medido | duração registada pelo dispositivo | Apresentar como observação, incluindo limitações do sensor. |
| Declarado | RPE introduzido pelo atleta | Apresentar como perceção subjetiva válida do atleta. |
| Calculado | carga `duração × RPE` | Apresentar fórmula e dados utilizados. |
| Estimado | RPE inferido da frequência cardíaca | Identificar como estimativa, nunca como resposta real do atleta. |
| Heurístico | prontidão derivada de TSB | Apresentar como orientação do produto, não como medição fisiológica. |
| Preditivo | risco ou desempenho futuro | Exigir validação adequada e incerteza explícita. |

### 2.2. O indivíduo tem prioridade sobre a população

Quando existirem dados individuais válidos, estes devem ter precedência sobre fórmulas populacionais.

Exemplos:

- zonas cardíacas manuais sobrepõem-se às zonas calculadas;
- limiar observado no histórico é preferível a uma percentagem genérica;
- ritmos devem evoluir com evidência do atleta;
- respostas a calor, altitude, desnível e recuperação devem ser personalizadas quando houver dados suficientes.

### 2.3. Nenhuma métrica isolada descreve o atleta

Carga, frequência cardíaca, ritmo, potência, sono, dor, contexto e perceção representam dimensões diferentes.

Uma recomendação não deve depender de um único número quando a decisão exige mais contexto. Em particular:

- TSB não mede recuperação completa;
- ACWR não prevê individualmente uma lesão;
- frequência cardíaca não descreve sozinha a intensidade de todas as sessões;
- ritmo perde comparabilidade em trail, calor, vento ou terreno técnico;
- RPE estimado não substitui o RPE declarado.

### 2.4. Ausência de dados não é normalidade

Quando um valor necessário está ausente, o resultado deve ser `None`, desconhecido ou indisponível sempre que possível.

O sistema não deve transformar automaticamente dados ausentes em:

- zero fisiológico;
- recuperação completa;
- ausência de fadiga;
- sessão fácil;
- recomendação segura.

### 2.5. Precisão visual deve corresponder à precisão científica

Resultados estimados ou heurísticos não devem ser apresentados com muitas casas decimais. A interface deve usar arredondamento, intervalos e linguagem proporcional à incerteza.

### 2.6. Explicabilidade é obrigatória

Para cada métrica ou recomendação relevante, o sistema deve conseguir responder:

1. Que dados foram utilizados?
2. Que fórmula ou regra foi aplicada?
3. Que período temporal foi considerado?
4. Que pressupostos foram feitos?
5. Que limitações existem?
6. O resultado é medido, calculado, estimado ou heurístico?

---

## 3. Os três motores

O PerformanceLab mantém a visão definida em `FOUNDATIONS.md`.

### 3.1. Motor científico

Responsável por cálculos determinísticos e reproduzíveis:

- frequência cardíaca e zonas;
- carga de treino;
- CTL, ATL e TSB;
- monotonia e strain;
- ritmo, potência e referências fisiológicas;
- estimativas de custo energético;
- hidratação e nutrição baseadas em regras explícitas.

O mesmo conjunto de entradas deve produzir o mesmo resultado.

### 3.2. Motor estatístico

Responsável por aprender padrões individuais quando existirem dados suficientes:

- evolução de ritmos;
- resposta habitual a carga;
- recuperação individual;
- deriva cardíaca;
- resposta a calor, altitude e desnível;
- variabilidade normal do atleta;
- incerteza das estimativas.

Um padrão estatístico não substitui uma relação fisiológica demonstrada. Deve indicar quantidade, qualidade e período dos dados utilizados.

### 3.3. Motor conversacional

Responsável por explicar resultados, resumir tendências e ajudar o atleta a compreender opções.

Não calcula a fonte científica, não inventa valores em falta e não altera diretamente o plano. Um modelo de linguagem pode explicar uma decisão já produzida pelos motores determinísticos ou estatísticos, mas nunca é a fonte dessa decisão.

---

## 4. Qualidade e proveniência dos dados

### 4.1. Hierarquia prática de origem

Não existe uma origem universalmente melhor para todas as métricas. A prioridade depende do conceito.

Exemplos:

- RPE manual tem prioridade sobre RPE estimado;
- zonas cardíacas manuais validadas têm prioridade sobre Karvonen;
- duração registada pode ser preferível a uma duração inferida;
- dados brutos plausíveis têm prioridade sobre resumos incompletos;
- uma medição laboratorial identificada deve manter a sua origem.

### 4.2. Validação mínima

Antes de entrar nos cálculos, um dado deve ser verificado quanto a:

- tipo e unidade;
- valores impossíveis ou negativos;
- data e ordem temporal;
- duração válida;
- duplicação;
- modalidade;
- origem manual, registada ou estimada.

### 4.3. Sensores

Sensores são fontes de observação, não autoridades absolutas.

Possíveis limitações incluem:

- falhas de contacto na frequência cardíaca;
- erros GPS e de desnível;
- potência não calibrada;
- pausas automáticas;
- amostragem irregular;
- diferenças entre fabricantes;
- ausência de contexto ambiental.

O sistema deve preservar os dados disponíveis e evitar inferências fortes a partir de séries manifestamente incompletas.

### 4.4. Contexto

O significado de uma sessão pode mudar com:

- terreno e superfície;
- inclinação e desnível;
- temperatura e humidade;
- altitude;
- vento;
- fadiga anterior;
- sono, dor e doença;
- equipamento;
- disponibilidade de tempo.

O contexto deve ser incorporado progressivamente, sem criar correções arbitrárias disfarçadas de ciência.

---

## 5. RPE e carga interna

### 5.1. RPE declarado

RPE representa a perceção global de esforço do atleta numa escala de 0 a 10.

É subjetivo, mas não é um dado inferior. Capta dimensões que sensores isolados podem não observar, incluindo esforço respiratório, fadiga muscular, calor, terreno e estado geral.

O sistema utiliza `AthleteFeedback.effective_rpe`, dando prioridade ao RPE manual quando existe.

### 5.2. Session-RPE

A carga real atual é calculada por:

```text
session-RPE load = duração em minutos × RPE efetivo
```

Esta unidade é arbitrária. Permite comparar carga interna entre sessões e modalidades, mas não significa que os estímulos sejam equivalentes.

Exemplo:

- 60 minutos a RPE 5 produzem 300 unidades;
- isto não prova que 60 minutos de corrida e 60 minutos de ciclismo tenham o mesmo efeito musculoesquelético ou técnico.

O método session-RPE foi proposto como forma prática de quantificar carga em diferentes tipos de exercício. Continua sujeito à qualidade e ao momento da perceção reportada.

### 5.3. RPE estimado automaticamente

Quando não existe RPE manual e há frequência cardíaca utilizável, o código atual pode estimá-lo a partir de:

- intensidade cardíaca;
- frequência cardíaca máxima;
- frequência cardíaca de repouso;
- duração da sessão.

A duração acrescenta atualmente até três pontos, à razão de um ponto por cada 30 minutos.

Esta é uma **heurística interna**. Não é uma medição validada do RPE individual. Pode ser especialmente frágil em:

- intervalos curtos;
- calor ou desidratação;
- deriva cardíaca;
- ciclismo versus corrida;
- medicação que altere a frequência cardíaca;
- falhas do sensor;
- atletas com respostas cardíacas atípicas.

O valor deve ser identificado como estimado e substituído pelo RPE manual quando o atleta o fornece.

---

## 6. Carga planeada

Antes de uma sessão acontecer não existe RPE sentido pelo atleta. O plano utiliza um RPE semântico associado à intensidade:

| Intensidade planeada | RPE atual |
|---|---:|
| `none` | 0 |
| `very easy` | 2 |
| `easy` | 3 |
| `easy to moderate` | 4 |
| `moderately hard` | 6 |
| `hard` | 7 |
| `race effort` | 8 |
| `very hard` | 9 |

A carga base planeada é:

```text
carga planeada = duração em minutos × RPE semântico
```

### 6.1. Correção atual por desnível

Para sessões planeadas da família de corrida:

- cada 100 m D+ acrescenta 5%;
- o acréscimo máximo é 30%;
- outras modalidades não recebem este fator.

Esta regra é uma **heurística conservadora do produto**. Não representa um modelo fisiológico individual validado e não considera distância, inclinação, tecnicidade, altitude, peso ou experiência do atleta.

Deve ser usada para evitar subestimar sistematicamente sessões com desnível, não para afirmar a carga fisiológica exata.

### 6.2. Comparação planeado–realizado

A comparação atual considera cargas equivalentes dentro de uma tolerância de 20% e normaliza modalidades em famílias.

A tolerância de 20% é uma regra operacional, não um limiar fisiológico universal. Deve permanecer testável e configurada num único local.

O resultado combina duas dimensões:

1. diferença de carga;
2. compatibilidade do estímulo e da modalidade.

---

## 7. CTL, ATL e TSB

### 7.1. Séries de carga diária

O histórico é convertido numa série cronológica de carga diária. Dias sem treino devem ser representados por zero para preservar a passagem do tempo.

Resultados dependem de:

- completude do histórico;
- qualidade do RPE;
- período anterior disponível;
- inclusão correta dos dias de descanso;
- consistência da unidade de carga.

**Unidade e escala atuais**

A carga diária utiliza unidades arbitrárias de session-RPE:

```text
unidades de carga = duração em minutos × RPE efetivo
```

Como CTL e ATL são médias móveis exponenciais desta carga diária, ambos mantêm uma unidade equivalente a **unidades de session-RPE por dia**:

- CTL representa carga diária habitual suavizada;
- ATL representa carga diária recente suavizada;
- TSB é a diferença entre essas duas médias e conserva a mesma unidade.

Estes valores:

- não são percentagens;
- não estão limitados ao intervalo de 0 a 100;
- não possuem um máximo fisiológico universal;
- não devem ser comparados diretamente entre atletas sem considerar histórico, modalidade e qualidade dos dados;
- devem ser interpretados principalmente pela evolução do próprio atleta.

Um CTL de 50 não significa “50% de fitness”. Um ATL de 70 não significa “70% de fadiga”. Um TSB de `+10` ou `-20` descreve apenas a diferença calculada entre carga habitual e carga recente segundo o modelo atual.

O código devolve atualmente `0.0` para CTL, ATL e TSB quando a série está vazia. Este comportamento é uma limitação conhecida: nesse contexto, zero pode significar ausência de dados e não uma medição real de carga nula. A apresentação pública deverá distinguir explicitamente estes estados.

### 7.2. CTL

O Chronic Training Load atual é uma média móvel exponencial da carga diária com constante temporal de 42 dias.

No produto, CTL funciona como indicador de exposição habitual a carga. O rótulo “fitness” é uma simplificação semântica: CTL não mede diretamente capacidade aeróbia, desempenho ou adaptação.

### 7.3. ATL

O Acute Training Load atual é uma média móvel exponencial da carga diária com constante temporal de 7 dias.

No produto, ATL funciona como indicador de exposição recente a carga. O rótulo “fatigue” é uma simplificação: ATL não mede diretamente fadiga neuromuscular, sono, dor, doença ou recuperação psicológica.

### 7.4. TSB

O Training Stress Balance é:

```text
TSB = CTL − ATL
```

Um valor positivo significa apenas que a carga habitual calculada excede a carga recente calculada. Um valor negativo significa o inverso.

TSB não é uma medição direta de frescura ou prontidão e não garante desempenho.

### 7.5. Limiares semânticos atuais

`TrainingState` usa atualmente regras como:

- TSB inferior a -20: necessidade de recuperação;
- TSB superior a -10: capacidade para absorver mais volume;
- TSB igual ou superior a 0: tolerância a intensidade;
- score de recuperação: `TSB + 50`, limitado entre 0 e 100.

Estas são **heurísticas do produto**. Devem ser tratadas como regras conservadoras de decisão, não como limiares clínicos ou fisiológicos universais.

O dashboard deve apresentar linguagem prudente, arredondamento adequado e explicação da informação em falta.

### 7.6. Recovery Score

O Recovery Score atual é calculado diretamente a partir do TSB:

`Recovery Score = TSB + 50`

O resultado é limitado ao intervalo de 0 a 100:

- valores inferiores a 0 são apresentados como 0;
- valores superiores a 100 são apresentados como 100;
- um TSB de 0 produz um Recovery Score de 50;
- um TSB de -20 produz um Recovery Score de 30;
- um TSB de +20 produz um Recovery Score de 70.

Esta transformação não acrescenta nova informação fisiológica ao TSB. Apenas converte o mesmo valor para uma escala visual mais familiar.

O Recovery Score atual não considera diretamente:

- sono;
- HRV;
- frequência cardíaca de repouso;
- dor ou desconforto;
- doença;
- stress psicológico;
- fadiga muscular;
- perceção subjetiva de recuperação;
- tempo decorrido desde a última sessão;
- contexto ambiental.

Por isso, o nome “Recovery Score” é uma simplificação do produto. O valor deve ser apresentado como uma estimativa heurística baseada em carga, nunca como medição completa da recuperação do atleta.

Um valor elevado também pode resultar de pouca carga recente ou de um período sem treino. Não significa automaticamente preparação para intensidade, adaptação positiva ou capacidade máxima de desempenho.

Quando o histórico necessário para CTL, ATL e TSB for insuficiente, o sistema deverá apresentar um estado de dados insuficientes em vez de comunicar o Recovery Score com falsa confiança.
---

## 8. ACWR, monotonia e strain

### 8.1. Acute:Chronic Workload Ratio

O cálculo atual é:

```text
ACWR = carga aguda ÷ carga crónica
```

Só é calculado quando a carga crónica é positiva.

As bandas atuais são:

| ACWR | Rótulo interno |
|---:|---|
| inferior a 0,8 | `Low` |
| 0,8 a 1,3 | `Moderate` |
| superior a 1,3 | `High` |

Estas bandas descrevem a relação entre carga recente e habitual. **Não devem ser apresentadas como previsão individual de lesão.**

O risco de lesão é multifatorial e a utilização causal ou preditiva do ACWR é cientificamente contestada. No PerformanceLab, ACWR pode contribuir para uma descrição de mudança de carga, nunca para um diagnóstico ou garantia de segurança.

### 8.2. Monotonia

O cálculo atual segue:

```text
monotonia = média da carga diária ÷ desvio-padrão da carga diária
```

Só existe quando o desvio-padrão é positivo. Valores elevados indicam baixa variabilidade relativa, mas não provam treino inadequado.

### 8.3. Strain

O cálculo atual é:

```text
strain = carga semanal total × monotonia
```

É um indicador composto dependente do método de carga e da janela utilizada. Deve ser interpretado em conjunto com contexto e evolução individual.

---

## 9. Frequência cardíaca

### 9.1. Valores configurados

O atleta pode fornecer:

- frequência cardíaca máxima;
- frequência cardíaca de repouso;
- frequência cardíaca de limiar;
- zonas manuais.

O sistema deve distinguir valores medidos, estimados e introduzidos manualmente sempre que essa proveniência estiver disponível.

### 9.2. Reserva cardíaca

```text
HRR = FC máxima − FC de repouso
```

A percentagem de reserva é:

```text
%HRR = (FC observada − FC de repouso) ÷ HRR × 100
```

### 9.3. Zonas Karvonen

Quando não existem zonas manuais e há FC máxima e de repouso válidas, o sistema constrói cinco zonas por percentagem da reserva cardíaca:

| Zona | Reserva cardíaca |
|---|---:|
| Z1 | 50–60% |
| Z2 | 60–70% |
| Z3 | 70–80% |
| Z4 | 80–90% |
| Z5 | 90–100% |

As zonas manuais têm prioridade.

Karvonen é uma aproximação populacional. As zonas podem não coincidir com limiares metabólicos individuais. FC máxima ou de repouso incorretas deslocam todas as zonas.

### 9.4. Utilização prática

A frequência cardíaca deve ser usada como guia, não como número a perseguir mecanicamente.

Devem ser considerados:

- atraso da resposta em intervalos;
- deriva cardíaca;
- calor e desidratação;
- altitude;
- cafeína, stress e sono;
- medicação;
- diferenças entre modalidades;
- precisão do sensor.

Em estratégias de prova, esforço, respiração, terreno e técnica podem ter prioridade sobre o valor instantâneo.

---

## 10. Potência e FTP

O sistema pode construir zonas de potência a partir de FTP:

| Zona | Percentagem atual de FTP |
|---|---:|
| Z1 | 0–55% |
| Z2 | 55–75% |
| Z3 | 75–90% |
| Z4 | 90–105% |
| Z5 | 105–120% |

Estas bandas são referências operacionais. A validade depende de:

- FTP atual e corretamente determinado;
- medidor calibrado;
- modalidade e posição;
- duração da sessão;
- condições ambientais;
- consistência entre dispositivos.

FTP não deve ser tratado como constante permanente nem como equivalente direto a limiar fisiológico em todas as circunstâncias.

---

## 11. Ritmo, limiar e perfil de desempenho

### 11.1. Ritmo de limiar

`PerformanceProfile` pode conter um ritmo de LT2 derivado do histórico. Este valor deve evoluir lentamente e depender de sessões suficientemente representativas.

Um ritmo observado em descida, vento favorável, distância curta ou GPS impreciso não deve redefinir sozinho o perfil.

### 11.2. Ritmo Tempo

O ritmo Tempo atual é calculado como:

```text
ritmo Tempo = ritmo LT2 × 1,03
```

e arredondado ao múltiplo de cinco segundos definido pelo domínio.

O fator de 3% é uma **regra prática do produto**. Deve ser validado individualmente e nunca confundido com a determinação laboratorial de um limiar.

### 11.3. Ritmo fácil

O ritmo fácil derivado do histórico é uma referência individual. Em trail e terreno variável, ritmo absoluto deve perder peso em favor de esforço, frequência cardíaca, inclinação e técnica.

### 11.4. Zonas de ritmo

As zonas atuais são fatores aplicados ao ritmo de limiar. Servem como intervalos operacionais e dependem totalmente da qualidade do limiar de entrada.

---

## 12. VO₂, VO₂max e economia de corrida

### 12.1. Teste de Cooper

O código inclui a estimativa:

```text
VO₂max = (distância em 12 minutos − 504,9) ÷ 44,73
```

Só deve ser usada quando a distância provém realmente de um teste de 12 minutos executado em condições adequadas.

### 12.2. Custo de oxigénio da corrida

Para corrida em plano, o código usa:

```text
velocidade em m/min = velocidade em km/h × 1000 ÷ 60
custo de oxigénio = 0,2 × velocidade em m/min + 3,5
```

Este resultado estima a exigência de oxigénio à velocidade indicada. **Não estima, por si só, o VO₂max do atleta.**

### 12.3. Funções legadas

`vo2max_from_speed()` e `vdot()` são atualmente aliases históricos ou aproximações simplificadas do custo de oxigénio.

Não devem ser apresentadas na UI como VO₂max ou VDOT completo. Devem ser removidas, renomeadas ou isoladas quando a compatibilidade deixar de ser necessária.

### 12.4. Economia de corrida

O cálculo atual expressa consumo de oxigénio por quilómetro:

```text
economia = VO₂ em ml/kg/min ÷ quilómetros por minuto
```

Só é significativo quando o VO₂ e a velocidade provêm de observações compatíveis. Um valor produzido apenas por duas estimativas dependentes não constitui medição independente de economia.

---

## 13. Desnível, terreno e distância de esforço

Para provas de corrida, o código atual utiliza:

```text
distância de esforço = distância em km + D+ em metros ÷ 100
```

Também classifica a exigência média de subida por metros de D+ por quilómetro.

Estas regras são úteis para ordenar provas e dimensionar o planeamento, mas são simplificações. Não representam adequadamente:

- inclinação máxima;
- descidas técnicas;
- altitude;
- tipo de piso;
- distribuição do desnível;
- condições meteorológicas;
- competência técnica do atleta.

A distância de esforço é uma heurística de comparação, não uma previsão universal de duração.

---

## 14. Recuperação e prontidão

Recuperação é multidimensional. Idealmente inclui:

- carga recente;
- RPE;
- sono;
- dor e rigidez;
- stress;
- doença;
- frequência cardíaca de repouso;
- HRV, quando disponível e interpretável;
- desempenho recente;
- perceção subjetiva.

O código atual contém scores simples baseados em RPE ou TSB e sugestões de dias de recuperação por bandas de RPE.

Estas funções são **heurísticas**, não previsões individualizadas. O sistema deve evitar frases absolutas como “totalmente recuperado” quando não dispõe das dimensões necessárias.

Um score de 0 a 100 deve ser apresentado como índice interno, com arredondamento e explicação, não como percentagem biológica de recuperação.

---

## 15. Especificidade e transferência entre modalidades

A carga interna permite reunir modalidades numa descrição global de stress. A transferência do estímulo é, contudo, parcial.

| Sessão realizada | Contribuição provável | Limite principal |
|---|---|---|
| Ciclismo fácil | carga aeróbia e recuperação ativa | menor impacto e especificidade de corrida |
| Ciclismo Z2 | endurance cardiovascular | não reproduz toda a exigência musculoesquelética da corrida |
| Caminhada em subida | endurance e trabalho de subida | mecânica e velocidade diferentes |
| Natação | carga aeróbia com baixo impacto | baixa especificidade para corrida e ciclismo |
| Corrida em trail | endurance, impacto, subida e técnica | ritmo pouco comparável entre terrenos |

Consequências para o planeamento:

- uma modalidade alternativa pode contabilizar carga;
- não deve apagar automaticamente uma necessidade específica;
- a proximidade da prova aumenta a importância da especificidade;
- sessões LT2, longos específicos e técnica exigem avaliação própria;
- substituições devem ser conservadoras e explicáveis.

---

## 16. Progressão, recuperação e periodização

O PerformanceLab utiliza princípios conservadores:

- progressão gradual de volume e carga;
- separação de sessões exigentes;
- limitação de dias consecutivos;
- recuperação após provas exigentes;
- redução de volume antes da prova;
- preservação de estímulos específicos;
- recuperação posterior à prova.

Os valores concretos e a sequência das fases pertencem a `PLANNING.md`.

Nenhuma percentagem de progressão deve ser tratada como segura para todos os atletas. Histórico, idade de treino, disponibilidade, sintomas, modalidade e resposta individual devem prevalecer.

---

## 17. Nutrição e hidratação

As orientações atuais de prova produzem intervalos de líquidos, sódio e hidratos de carbono a partir da duração estimada e de um perfil nutricional.

Devem ser comunicadas como pontos de partida a testar em treino.

Limitações relevantes:

- taxa de suor individual;
- concentração de sódio no suor;
- temperatura e humidade;
- tolerância gastrointestinal;
- intensidade e duração;
- disponibilidade nos abastecimentos;
- historial médico;
- produtos e concentrações utilizados.

O sistema não deve incentivar ingestão forçada de água nem estrear estratégias nutricionais em prova. Situações médicas, sintomas ou necessidades especiais exigem aconselhamento profissional.

---

## 18. Linguagem de comunicação

### 18.1. Formulações preferidas

- “A carga recente está acima da carga habitual calculada.”
- “O indicador sugere uma abordagem prudente.”
- “O RPE foi estimado a partir da frequência cardíaca e duração.”
- “Os dados disponíveis são insuficientes para calcular este valor.”
- “A sessão contribuiu para carga aeróbia, mas não substitui toda a especificidade.”

### 18.2. Formulações a evitar

- “Tem 83,2% de recuperação.”
- “O seu risco de lesão é alto.”
- “O CTL prova que está em boa forma.”
- “O ATL mede a sua fadiga real.”
- “Este valor de VO₂max foi medido”, quando foi estimado.
- “Está pronto para intensidade”, sem contexto ou incerteza.

---

## 19. Classificação das regras atuais

| Regra ou métrica | Classificação no PerformanceLab |
|---|---|
| Duração registada | medição/observação |
| RPE manual | declaração subjetiva |
| Session-RPE | cálculo com base metodológica |
| RPE automático | heurística estimada |
| CTL 42 dias | modelo operacional |
| ATL 7 dias | modelo operacional |
| TSB = CTL − ATL | cálculo do modelo |
| Readiness por limiares de TSB | heurística do produto |
| ACWR e bandas | indicador descritivo heurístico |
| Monotonia e strain | indicadores derivados |
| Zonas manuais | configuração individual |
| Zonas Karvonen | estimativa populacional |
| Ritmo Tempo = LT2 × 1,03 | heurística do produto |
| 20% de tolerância de carga | regra operacional |
| +5% por 100 m D+, máximo 30% | heurística do produto |
| 100 m D+ = 1 km de esforço | heurística de comparação |
| Cooper 12 minutos | estimativa condicionada ao protocolo |
| Custo de oxigénio por velocidade | equação metabólica estimada |
| Score de recuperação 0–100 | índice heurístico de apresentação |

Esta tabela deve ser atualizada quando a implementação ou o nível de validação mudar.

---

## 20. Requisitos para uma nova métrica

Uma nova métrica só deve entrar no núcleo quando tiver:

1. nome e definição inequívocos;
2. unidade;
3. dados de entrada e respetiva proveniência;
4. fórmula ou algoritmo reproduzível;
5. população e contexto de aplicação;
6. pressupostos;
7. limitações;
8. comportamento perante dados ausentes;
9. precisão de apresentação;
10. referências adequadas;
11. testes com casos normais e limites;
12. classificação como medida, cálculo, estimativa, heurística ou predição;
13. explicação de como pode influenciar uma decisão;
14. regra que impeça a UI ou o motor conversacional de exagerar o seu significado.

### 20.1. Requisitos adicionais para modelos estatísticos

- dimensão mínima da amostra individual;
- separação entre treino e validação;
- avaliação fora da amostra;
- intervalo de incerteza;
- deteção de mudança de comportamento;
- comparação com uma baseline simples;
- possibilidade de desativação ou fallback.

### 20.2. Requisitos adicionais para recomendações de segurança

Recomendações relacionadas com lesão, doença, dor ou retorno ao treino exigem revisão especializada e linguagem de encaminhamento. O produto não deve diagnosticar.

---

## 21. Governação científica

### 21.1. Evidência

A prioridade é:

1. consensos e orientações profissionais relevantes;
2. revisões sistemáticas e meta-análises;
3. estudos originais adequados à população e à pergunta;
4. modelos fisiológicos reconhecidos;
5. heurísticas transparentes quando a evidência não resolve a decisão prática.

Uma heurística pode ser útil. Deve apenas ser identificada como tal.

### 21.2. Mudanças de fórmula

Alterar uma fórmula ou limiar exige:

- motivo documentado;
- referência ou justificação de produto;
- avaliação do impacto em dados existentes;
- atualização dos testes;
- atualização deste documento;
- decisão sobre migração ou recálculo;
- confirmação de que a UI continua a comunicar o significado correto.

### 21.3. Validação

O módulo científico poderá incluir comparação de métodos, repetibilidade, erro, concordância e calibração. Ferramentas como Bland–Altman ou ICC devem ser escolhidas de acordo com a pergunta e não usadas como decoração estatística.

---

## 22. Limitações atuais assumidas

O estado atual tem limitações conhecidas:

- vários limiares de prontidão são heurísticos;
- o RPE automático não está personalizado nem validado por atleta;
- CTL e ATL usam constantes fixas para todos;
- recuperação não integra ainda sono, dor, stress ou HRV;
- ACWR é apenas descritivo;
- desnível e distância de esforço usam regras simplificadas;
- algumas funções legadas têm nomes cientificamente imprecisos;
- o perfil de desempenho depende da quantidade e qualidade do histórico;
- diferenças entre modalidades são apenas parcialmente modeladas;
- recomendações nutricionais são intervalos genéricos configuráveis;
- não existe ainda uma camada completa de incerteza e proveniência visível na UI.

Estas limitações não devem ser escondidas. Formam parte do roadmap científico.

---

## 23. Referências iniciais

Estas referências são pontos de partida para os métodos implementados. Não validam automaticamente todos os limiares ou adaptações específicas do PerformanceLab.

- Foster, C. et al. (2001). *A new approach to monitoring exercise training*. Journal of Strength and Conditioning Research, 15(1), 109–115. [PubMed](https://pubmed.ncbi.nlm.nih.gov/11708692/)
- Yabe, H. et al. (2021). *The Karvonen and heart rate reserve formulas*. International Journal of Sports Medicine, 42(6), 553–559. [PubMed](https://pubmed.ncbi.nlm.nih.gov/33511760/)
- Goldberg, L. et al. (1988). *Assessment of exercise intensity formulas by use of ventilatory threshold*. Chest, 94(1), 95–98. [PubMed](https://pubmed.ncbi.nlm.nih.gov/3383662/)

Referências futuras devem ser associadas à métrica concreta que suportam e revistas quando a implementação mudar.

---

## 24. Relação com os restantes documentos

- `MANIFESTO.md` define o compromisso com o atleta, a transparência e a adaptação à vida real.
- `FOUNDATIONS.md` define os motores científico, estatístico e conversacional.
- `PRODUCT_VISION.md` define o produto e o público.
- `DOMAIN_MODEL.md` separa factos, interpretações e decisões.
- `ARCHITECTURE.md` protege o motor científico das camadas externas.
- `TRAINING_SCIENCE.md` define métricas, evidência, heurísticas e limites.
- `PLANNING.md` definirá como estes resultados influenciam o plano.

O PerformanceLab deve aproximar ciência e prática sem transformar incerteza em falsa certeza. O valor do sistema não está em produzir mais números, mas em ajudar o atleta a compreender o que esses números podem — e não podem — dizer.
