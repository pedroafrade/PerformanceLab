# PerformanceLab — Visão de Produto

**Estado:** documento normativo  
**Produto:** PerformanceLab  
**Utilizador principal:** atleta amador de endurance  
**Horizonte:** primeira aplicação pública e evolução posterior

## 1. Propósito

O PerformanceLab existe para ajudar atletas amadores de endurance a compreender o seu treino e a tomar melhores decisões perante a realidade diária.

Treinar melhor não significa cumprir um plano de forma rígida. Significa compreender o propósito de cada sessão, interpretar a resposta do atleta e adaptar o futuro sem perder de vista o objetivo.

O PerformanceLab transforma dados de treino em conhecimento claro, contextualizado e acionável.

> Compreender o treino. Adaptar com confiança.

## 2. O problema

O atleta amador treina num contexto diferente do atleta profissional.

O atleta profissional pode organizar a vida em função do treino. O atleta amador precisa de integrar o treino com:

- trabalho;
- família;
- disponibilidade variável;
- fadiga acumulada;
- sono e stress;
- condições meteorológicas;
- terreno disponível;
- doença, desconforto ou lesão;
- provas e objetivos pessoais.

Muitas plataformas continuam a tratar o plano como uma sequência rígida de sessões ou limitam-se a apresentar grandes quantidades de dados depois de cada atividade.

Isso deixa três perguntas essenciais sem resposta:

1. O que significa o treino que realizei?
2. O que devo fazer agora?
3. O plano continua adequado depois do que realmente aconteceu?

O PerformanceLab pretende responder a essas perguntas.

## 3. Para quem construímos

### 3.1. Utilizador principal

O utilizador principal é o atleta amador de endurance que:

- treina com regularidade;
- possui um ou mais objetivos futuros;
- recolhe alguns dados de atividade;
- não consegue seguir sempre um plano ideal;
- quer compreender o treino sem precisar de interpretar dezenas de métricas técnicas;
- valoriza autonomia, transparência e controlo sobre os seus dados.

O atleta pode praticar corrida de estrada, trail running, ciclismo, natação ou outras modalidades de endurance. A primeira experiência pública não precisa de oferecer a mesma profundidade de planeamento em todas as modalidades, mas a arquitetura do produto deve permanecer multidesporto.

### 3.2. Utilizador secundário

O treinador é um utilizador secundário e futuro do produto.

O PerformanceLab deve poder ajudá-lo a:

- compreender rapidamente o estado de vários atletas;
- rever atividades e adaptações;
- identificar exceções que exigem atenção;
- confirmar, ajustar ou substituir decisões automáticas;
- explicar recomendações com base em dados verificáveis.

A experiência do treinador não faz parte do núcleo mínimo da primeira UI pública, exceto quando necessária para validar a arquitetura de permissões.

## 4. Proposta de valor

O PerformanceLab une quatro capacidades que normalmente aparecem separadas:

1. **Compreender o atleta** através do seu histórico, perfil e estado atual.
2. **Construir uma estratégia** através de um plano persistente orientado para provas e objetivos.
3. **Comparar intenção e realidade** depois de cada atividade realizada ou sessão falhada.
4. **Adaptar o futuro** de forma incremental, conservadora e explicável.

O produto não se limita a mostrar o que aconteceu. Usa o que aconteceu para avaliar se o que estava planeado para o futuro continua a ser apropriado.

## 5. Promessa do produto

Quando o atleta abre o PerformanceLab, deve conseguir compreender rapidamente:

1. o que deve fazer hoje;
2. como se encontra;
3. porque essa sessão é adequada;
4. qual é o próximo objetivo importante;
5. se o plano foi adaptado;
6. porque o plano mudou;
7. que dados sustentam essa decisão.

A complexidade matemática pertence ao software. A decisão pertence ao atleta.

## 6. Princípios do produto

### 6.1. O atleta é o centro

O produto é organizado em torno da pessoa, não de ficheiros, sensores, dispositivos ou algoritmos.

As atividades são observações do atleta. O plano é uma estratégia para o atleta. As métricas existem para interpretar a sua evolução.

### 6.2. A realidade tem prioridade sobre o plano

Um plano representa intenção, não um contrato rígido.

Quando a realidade diverge do planeado, o PerformanceLab deve:

- preservar o que já aconteceu;
- interpretar a diferença;
- atualizar o estado do atleta;
- adaptar apenas o futuro;
- manter o objetivo global sempre que isso continuar a ser seguro e realista.

### 6.3. Carga comparável não significa estímulo equivalente

A carga fisiológica de diferentes modalidades pode contribuir para o estado global do atleta.

Contudo, modalidades diferentes não oferecem automaticamente o mesmo estímulo específico.

Por exemplo:

- ciclismo fácil pode substituir parcialmente uma corrida fácil;
- ciclismo Z2 pode contribuir para endurance;
- ciclismo Z2 não substitui automaticamente LT2 Run;
- um longo de bicicleta não reproduz toda a preparação musculoesquelética de um longo de trail;
- a modalidade da prova determina a especificidade principal do plano.

O PerformanceLab deve contabilizar a carga sem apagar a especificidade.

### 6.4. O contexto faz parte do treino

O significado de uma sessão depende de mais do que distância e duração.

Sempre que existirem dados fiáveis, a interpretação pode considerar:

- modalidade;
- terreno;
- elevação;
- altitude;
- temperatura;
- vento;
- intensidade;
- fadiga;
- recuperação;
- disponibilidade;
- experiência recente;
- proximidade da prova.

Dados ausentes devem reduzir a confiança da interpretação, não ser substituídos silenciosamente por falsa precisão.

### 6.5. Personalização progressiva

O produto deve funcionar com pouca informação e melhorar à medida que conhece o atleta.

Quando existirem dados individuais suficientes, devem ter prioridade sobre médias populacionais. Quando não existirem, os pressupostos utilizados devem ser conservadores e visíveis.

### 6.6. Ciência e transparência

Cada métrica ou recomendação relevante deve poder explicar:

- os dados utilizados;
- o método aplicado;
- os pressupostos;
- a janela temporal;
- as limitações;
- o nível de confiança, quando aplicável.

Nenhuma caixa negra deve substituir o pensamento crítico.

### 6.7. Independência de dispositivos

Os dados pertencem ao atleta.

Sensores, relógios e plataformas externas são fontes de informação, não o centro do produto. Nenhum fabricante deve ser indispensável para utilizar o PerformanceLab.

### 6.8. Simplicidade acionável

A interface deve começar pela interpretação e pela ação, não pela métrica bruta.

O atleta deve ver primeiro:

- o estado;
- a recomendação;
- a tendência;
- a razão principal.

Os detalhes técnicos devem estar disponíveis num segundo nível.

### 6.9. Segurança conservadora

Perante incerteza, o sistema deve preferir uma adaptação pequena, reversível e explicável.

O produto não deve:

- compensar cegamente um treino falhado;
- acumular sessões exigentes sem recuperação;
- alterar provas ou taper crítico por uma regra genérica;
- aumentar carga quando o estado do atleta indica fadiga;
- inferir equivalência específica apenas porque a carga é semelhante.

### 6.10. Arquitetura ao serviço do produto

A lógica pertence ao domínio. A interface apresenta resultados e recolhe decisões do utilizador.

As tecnologias de armazenamento, frameworks de UI, fornecedores de identidade e modelos de linguagem são detalhes substituíveis.

## 7. Experiência central

O ciclo principal do PerformanceLab é:

```text
Definir atleta e objetivo
          ↓
Gerar um plano persistente
          ↓
Apresentar o treino relevante
          ↓
Importar ou registar a atividade real
          ↓
Comparar realizado e planeado
          ↓
Atualizar o estado do atleta
          ↓
Adaptar apenas o futuro
          ↓
Explicar o que mudou e porquê
```

Este ciclo deve poder repetir-se sem regenerar o plano completo em cada acesso.

## 8. Capacidades essenciais

### 8.1. Compreender

- consolidar o histórico do atleta;
- interpretar carga, fadiga, forma, recuperação e consistência;
- construir um perfil fisiológico progressivo;
- distinguir dados observados, configurados, estimados e indisponíveis;
- mostrar tendências relevantes.

### 8.2. Planear

- escolher um objetivo ou prova principal;
- considerar outras provas do calendário;
- gerar um plano completo e persistente;
- periodizar até à prova e recuperação posterior;
- respeitar disponibilidade, modalidade, progressão e recuperação;
- apresentar o plano através de janelas móveis.

### 8.3. Reconciliar

- associar atividades ao dia planeado;
- reconhecer sessões equivalentes, modificadas ou substitutas;
- reconhecer sessões falhadas;
- comparar carga planeada e realizada;
- processar atividades tardias ou corrigidas sem duplicação.

### 8.4. Adaptar

- atualizar apenas sessões futuras;
- preservar passado, atividades realizadas e estrutura global;
- proteger provas e preparação crítica;
- responder de forma proporcional e conservadora;
- manter a especificidade necessária para o objetivo;
- explicar a alteração ao atleta.

### 8.5. Comunicar

- responder primeiro à decisão mais importante;
- apresentar métricas com unidade, período e precisão adequados;
- explicar dados insuficientes;
- permitir aprofundamento sem sobrecarregar a vista principal;
- usar linguagem consistente e compreensível.

## 9. O papel da ciência, estatística e linguagem

O PerformanceLab pode evoluir através de três capacidades complementares.

### 9.1. Motor científico

Responsável por cálculos determinísticos, reproduzíveis e explicáveis, incluindo:

- fisiologia;
- zonas;
- carga de treino;
- fadiga;
- recuperação;
- limiares;
- eficiência;
- modelos de performance.

Este motor constitui a fonte de verdade para métricas científicas.

### 9.2. Motor estatístico

Responsável por aprender padrões individuais, incluindo:

- resposta à carga;
- recuperação habitual;
- tolerância ao volume;
- adaptação ao calor ou altitude;
- evolução de performance;
- consistência e interrupções.

Os modelos estatísticos personalizam a interpretação, mas não substituem princípios científicos nem ocultam incerteza.

### 9.3. Motor conversacional

Responsável por explicar, resumir e ajudar o utilizador a explorar informação.

Um modelo de linguagem pode:

- explicar uma sessão;
- resumir tendências;
- responder a perguntas;
- preparar relatórios;
- apresentar alternativas já avaliadas pelo domínio.

Não deve calcular métricas fisiológicas, inventar dados ou decidir sozinho alterações ao plano.

O PerformanceLab não deve depender de um fornecedor específico de inteligência artificial.

## 10. O que o PerformanceLab não é

O PerformanceLab não é:

- um substituto obrigatório de um treinador;
- um calendário rígido de sessões;
- uma coleção de gráficos sem interpretação;
- um agregador de distâncias incompatíveis entre modalidades;
- uma caixa negra que produz recomendações sem explicação;
- um produto dependente de um relógio ou fabricante;
- um diagnóstico médico;
- uma garantia de performance ou de ausência de lesão;
- uma plataforma de inteligência artificial que inventa decisões fisiológicas.

## 11. Limites de responsabilidade

O PerformanceLab apoia decisões de treino, mas não presta aconselhamento médico.

O produto deve comunicar claramente quando:

- os dados são insuficientes;
- uma métrica é estimada;
- existe incerteza elevada;
- o comportamento observado pode justificar avaliação profissional;
- uma recomendação automática deve ser revista por atleta ou treinador.

Sinais de doença, dor, lesão ou risco clínico não devem ser tratados apenas através de alterações automáticas de carga.

## 12. Dados, privacidade e controlo

O atleta deve poder:

- saber que dados são guardados;
- compreender para que são utilizados;
- exportar os seus dados;
- corrigir informação;
- eliminar a sua conta e dados;
- controlar quem lhes pode aceder.

Os dados não devem ser usados para finalidades incompatíveis com o produto sem consentimento explícito.

## 13. Primeira aplicação pública

A primeira UI pública deve concentrar-se num ciclo de valor completo para o atleta.

### Incluído

- conta segura de atleta;
- perfil e configuração fisiológica;
- disponibilidade e preferências;
- eventos e prova principal;
- geração inicial do plano;
- plano persistente;
- treino de hoje e janela de sete dias;
- importação FIT, FIT.GZ e GPX;
- histórico;
- avaliação do treino realizado;
- adaptação incremental;
- explicação básica das adaptações;
- estado atual e tendências essenciais;
- exportação e eliminação de dados.

### Não incluído

- interface completa para treinadores;
- conversação por inteligência artificial;
- previsões avançadas de resultado em prova;
- comparação científica avançada de sensores;
- marketplace de planos;
- integrações automáticas com todas as plataformas;
- suporte profundo e equivalente para todas as modalidades.

Estas exclusões protegem o foco do produto. Podem ser revistas depois de o ciclo principal estar validado.

## 14. Como medimos sucesso

O sucesso da primeira aplicação pública não deve ser medido pelo número de métricas disponíveis.

Deve ser medido pela capacidade do atleta para:

- perceber o treino que deve realizar;
- compreender o estado atual;
- importar uma atividade sem dificuldade;
- perceber se o plano mudou;
- compreender a razão principal da alteração;
- confiar que a aplicação não altera repetidamente o mesmo treino;
- manter controlo sobre os seus dados;
- continuar a utilizar o plano perante imprevistos reais.

Indicadores úteis incluem:

- conclusão do onboarding;
- geração bem-sucedida do primeiro plano;
- taxa de sucesso da importação;
- percentagem de adaptações compreendidas;
- número de correções manuais necessárias;
- retenção após a primeira semana e o primeiro mês;
- incidência de planos ou dados inconsistentes;
- satisfação e confiança reportadas pelo atleta.

## 15. Filtro de decisão

Cada nova funcionalidade deve responder afirmativamente às seguintes perguntas:

1. Ajuda o atleta a tomar uma decisão melhor?
2. Está alinhada com o ciclo compreender, planear, reconciliar e adaptar?
3. A decisão é explicável com os dados disponíveis?
4. Comunica corretamente incerteza e limitações?
5. Respeita a propriedade e privacidade dos dados?
6. Preserva as fronteiras entre domínio, apresentação e infraestrutura?
7. É necessária para o produto atual ou pertence a uma fase posterior?

Se a resposta for negativa, a funcionalidade provavelmente não pertence ao núcleo atual do PerformanceLab.

## 16. Relação com os restantes documentos

Este documento define **porquê**, **para quem** e **que valor** o PerformanceLab pretende criar.

Os restantes documentos devem responder a perguntas diferentes:

- `DOMAIN_MODEL.md`: que conceitos existem no domínio;
- `ARCHITECTURE.md`: como as responsabilidades e dependências são organizadas;
- `TRAINING_SCIENCE.md`: como métricas e modelos científicos são definidos;
- `PLANNING.md`: como o plano é gerado, reconciliado e adaptado;
- `ROADMAP_PUBLIC_UI.md`: em que ordem o produto evolui até à publicação;
- `AUDIT_CURRENT_STATE.md`: qual era o estado do projeto no início deste ciclo documental.

Em caso de conflito sobre a intenção do produto, `PRODUCT_VISION.md` é a referência principal.

## 17. Visão de longo prazo

O PerformanceLab pretende evoluir para uma representação digital coerente do atleta de endurance:

- quem é;
- o que realizou;
- o que pretende alcançar;
- como está a responder;
- o que deve fazer a seguir;
- porque essa decisão faz sentido.

O plano ideal raramente sobrevive ao primeiro imprevisto. Um sistema que compreende o atleta deve conseguir adaptar-se.
