# PerformanceLab — Roadmap até à primeira aplicação pública

**Data:** 2 de agosto de 2026  
**Ponto de partida:** branch `main` após conclusão da reconciliação e adaptação incremental do plano  
**Objetivo:** publicar uma primeira UI segura, compreensível e utilizável por atletas reais.

## 1. Definição de aplicação pública

Neste roadmap, “aplicação pública” significa uma aplicação online que:

- permite contas reais;
- guarda dados pessoais e atividades reais;
- apresenta um plano persistente;
- adapta o futuro após atividades realizadas ou falhadas;
- oferece autenticação, autorização, persistência e recuperação adequadas;
- possui uma experiência suficientemente clara para utilização sem acompanhamento técnico.

Não significa apenas disponibilizar publicamente a aplicação Streamlit de desenvolvimento.

## 2. Princípios de execução

- Um commit lógico de cada vez.
- Alterações pequenas, testáveis e reversíveis.
- GitHub `main` como única fonte de verdade.
- O domínio calcula; a UI apresenta.
- Objetos de domínio imutáveis quando apropriado.
- Métricas científicas devem ser explicáveis.
- Valores apresentados devem possuir unidade, período e precisão adequados.
- Nenhuma alteração visual deve esconder um problema científico ou arquitetural.
- Não avançar de fase sem cumprir os respetivos critérios de conclusão.

## 3. Fase 1 — Documentação e contrato do produto

### Objetivo

Estabelecer uma fonte de verdade coerente antes de novas alterações estruturais ou visuais.

### Trabalho

1. Adicionar a auditoria do estado atual.
2. Adicionar este roadmap.
3. Criar `docs/PRODUCT_VISION.md`.
4. Reescrever `docs/DOMAIN_MODEL.md`.
5. Reescrever `docs/ARCHITECTURE.md`.
6. Criar `docs/TRAINING_SCIENCE.md`.
7. Criar `docs/PLANNING.md`.
8. Reescrever `README.md`.
9. Substituir o roadmap antigo por um único roadmap normativo.
10. Mover documentos históricos para `docs/archive/`.
11. Registar decisões estruturais em `docs/decisions/`.

### Critérios de conclusão

- O estado documentado corresponde ao código existente.
- Não existem dois roadmaps normativos concorrentes.
- A primeira versão pública possui âmbito explícito.
- Estão documentadas as fronteiras entre domínio, apresentação e infraestrutura.
- Está documentada a diferença entre carga fisiológica e especificidade da modalidade.

## 4. Fase 2 — Auditoria de correção científica

### Objetivo

Garantir que métricas e adaptações publicadas não são enganadoras ou incompletas.

### Trabalho

1. Inventariar todas as intensidades geradas pelo Planner.
2. Garantir tradução de carga para todas as intensidades planeadas.
3. Rever cargas de Recovery, Easy, Endurance, Tempo, LT2, Threshold, Long, Pre-Race, Shakeout e Race.
4. Documentar a unidade e escala de CTL, ATL e TSB.
5. Documentar a construção do Recovery Score.
6. Documentar o Training Load Score e o ramp rate.
7. Definir precisão de apresentação para cada métrica.
8. Definir estados de dados insuficientes.
9. Rever transferência de carga entre modalidades.
10. Criar testes para invariantes científicos e semânticos.
11. Rever limites de progressão semanal.
12. Rever a resposta cumulativa a várias atividades tardias ou revistas.

### Critérios de conclusão

- Nenhum treino gerado fica sem carga por uma intensidade desconhecida.
- Cada métrica pública possui definição, unidade, período e limitação.
- Dados insuficientes não produzem falsa precisão.
- As regras entre modalidades preservam a especificidade da prova.
- Os testes cobrem as principais invariantes de segurança.

## 5. Fase 3 — Arquitetura de informação do dashboard

### Objetivo

Definir o que o atleta deve compreender ao abrir a aplicação, antes de alterar o aspeto visual.

### Perguntas principais

O dashboard deve responder, por esta ordem:

1. O que devo fazer hoje?
2. Como estou neste momento?
3. O meu plano foi adaptado? Porquê?
4. Qual é o meu próximo objetivo?
5. O que aconteceu recentemente?
6. Como estou a evoluir?

### Estrutura recomendada

#### Primeira linha

- sessão de hoje ou próxima sessão;
- estado atual e recomendação;
- próxima prova.

#### Segunda linha

- plano móvel de sete dias;
- aviso e explicação da última adaptação.

#### Terceira linha

- carga das últimas quatro semanas;
- atividade recente;
- resumo dos últimos sete dias.

#### Área detalhada

- tendências fisiológicas;
- performance;
- resumos mensais;
- histórico.

### Trabalho

1. Criar wireframe da nova hierarquia.
2. Escolher períodos explícitos para todos os resumos.
3. Decidir a relação entre Weekly Plan e Next Workout.
4. Definir apresentação da fase atual.
5. Definir estados vazios.
6. Definir apresentação das adaptações.
7. Definir navegação para detalhes.
8. Aprovar o wireframe antes de implementar CSS.

### Critérios de conclusão

- Cada cartão responde a uma pergunta concreta.
- Nenhuma métrica aparece sem período ou unidade.
- A ação principal é visível sem scroll.
- O plano adaptado é explicável.
- Não existe duplicação significativa de informação.

## 6. Fase 4 — Sistema de apresentação

### Objetivo

Construir uma UI coerente, reutilizável e independente da matemática do domínio.

### Trabalho

1. Criar formatadores comuns para duração, distância, ritmo, elevação, carga e percentagens.
2. Arredondar métricas segundo contratos explícitos.
3. Criar componentes comuns para cartões e estados vazios.
4. Unificar resumos semanais e mensais.
5. Reduzir CSS inline e duplicado.
6. Remover dependências Streamlit da camada `performancelab.presentation`.
7. Definir um modelo de cores semânticas acessível.
8. Definir tipografia e espaçamento.
9. Definir comportamento responsivo.
10. Escolher português, inglês ou internacionalização completa.
11. Remover componentes legados e `app/app_backup.py`.
12. Ocultar elementos técnicos do Streamlit na configuração de produção.

### Critérios de conclusão

- Não existem valores com precisão interna na UI.
- Os componentes principais são reutilizáveis.
- A apresentação não executa lógica de domínio.
- O dashboard funciona nos tamanhos de ecrã suportados.
- A terminologia é consistente.

## 7. Fase 5 — Fluxos essenciais do atleta

### Objetivo

Permitir que um atleta conclua sozinho as tarefas fundamentais.

### Fluxos

1. Criar ou completar perfil.
2. Configurar FC, zonas e dados fisiológicos.
3. Definir disponibilidade e preferências.
4. Criar uma prova.
5. Gerar o primeiro plano.
6. Consultar o treino de hoje.
7. Importar atividades.
8. Rever novas, atualizadas e duplicadas.
9. Compreender a adaptação aplicada.
10. Editar RPE ou corrigir atividade.
11. Consultar o plano completo e a janela semanal.
12. Exportar ou eliminar dados.

### Melhorias de importação

- mover a importação para um fluxo dedicado;
- validar ficheiros antes de persistir;
- mostrar atividades encontradas;
- identificar duplicados;
- apresentar resultados por atividade;
- explicar alterações aplicadas ao plano;
- não esconder erros atrás de uma contagem genérica.

### Critérios de conclusão

- Um atleta novo consegue chegar a um plano sem ajuda técnica.
- Uma importação falhada explica o problema.
- Uma adaptação indica o treino afetado e a razão.
- A correção de uma atividade volta a reconciliar apenas o necessário.

## 8. Fase 6 — Persistência, identidade e segurança

### Objetivo

Permitir utilização pública com dados pessoais reais.

### Trabalho

1. Escolher autenticação própria segura ou fornecedor externo.
2. Introduzir password com hash seguro quando aplicável.
3. Implementar sessões persistentes e expiração.
4. Implementar recuperação de conta.
5. Autorizar cada acesso ao atleta correto.
6. Definir relação entre treinador e atletas.
7. Migrar persistência pública para base de dados transacional.
8. Criar migrações de esquema.
9. Implementar backups e recuperação.
10. Proteger ficheiros de atividade.
11. Implementar exportação de dados.
12. Implementar eliminação de conta e dados.
13. Definir política de retenção.
14. Gerir segredos fora do repositório.
15. Garantir que logs não expõem dados sensíveis.

### Critérios de conclusão

- Um utilizador não consegue aceder aos dados de outro.
- Passwords nunca são guardadas em texto simples.
- Existe recuperação testada de backups.
- Existe processo de exportação e eliminação.
- A aplicação pode executar em mais de uma instância sem corrupção.

## 9. Fase 7 — Qualidade, entrega e operação

### Objetivo

Tornar a aplicação reproduzível, observável e segura para publicar.

### Trabalho

1. Unificar dependências em `pyproject.toml`.
2. Definir versões suportadas de Python.
3. Fixar ou limitar versões críticas de dependências.
4. Criar GitHub Actions para testes.
5. Adicionar lint e formatação.
6. Adicionar testes de migração.
7. Adicionar testes dos fluxos públicos principais.
8. Melhorar tratamento de erros de importação.
9. Criar logging estruturado.
10. Adicionar monitorização e alertas.
11. Criar página de erro adequada.
12. Separar configuração de desenvolvimento e produção.
13. Remover criação automática de contas de demonstração em produção.
14. Definir processo de deployment e rollback.

### Critérios de conclusão

- Cada push é validado automaticamente.
- O ambiente pode ser reconstruído a partir do repositório.
- Falhas importantes são detetadas e diagnosticáveis.
- Existe rollback documentado.
- Produção não cria nem expõe dados de demonstração.

## 10. Fase 8 — Alpha privada

### Objetivo

Validar o comportamento com atletas reais antes da abertura pública.

### Grupo inicial

- 3 a 5 atletas;
- diferentes volumes de histórico;
- diferentes modalidades;
- provas de distâncias diferentes;
- atividades completas, tardias, revistas e falhadas.

### Validação

1. Rever manualmente os planos gerados.
2. Rever cada adaptação inesperada.
3. Confirmar proteção de provas e taper.
4. Confirmar ausência de adaptações repetidas.
5. Medir compreensão do dashboard.
6. Medir sucesso da importação.
7. Recolher dúvidas recorrentes.
8. Registar problemas de confiança nas recomendações.

### Critérios de conclusão

- Nenhum plano é corrompido.
- Nenhuma adaptação é aplicada repetidamente.
- Provas e sessões críticas permanecem protegidas.
- Os atletas compreendem a ação principal do dashboard.
- A importação é confiável.
- Os problemas críticos da alpha estão resolvidos.

## 11. Fase 9 — Primeira UI pública

### Funcionalidades incluídas

- conta de atleta;
- perfil;
- eventos;
- disponibilidade e preferências;
- geração inicial do plano;
- plano persistente;
- dashboard orientado ao dia atual;
- importação FIT, FIT.GZ e GPX;
- histórico;
- reconciliação;
- adaptação incremental;
- apresentação da adaptação;
- explicação básica das métricas;
- exportação e eliminação dos dados.

### Funcionalidades excluídas

- interface conversacional;
- recomendações geradas por IA;
- comparação científica avançada de sensores;
- marketplace de planos;
- funcionalidades completas de treinador;
- previsões complexas de performance;
- integrações automáticas com todas as plataformas externas.

### Critérios de publicação

- autenticação e autorização seguras;
- persistência transacional;
- backups testados;
- CI sem erros;
- fluxos essenciais testados;
- dashboard compreensível;
- métricas documentadas;
- política de privacidade e termos adequados;
- monitorização ativa;
- processo de suporte e resposta a incidentes.

## 12. Sequência imediata de documentos

Antes de qualquer redesign visual, executar:

1. `AUDIT_CURRENT_STATE.md`;
2. `ROADMAP_PUBLIC_UI.md`;
3. `docs/PRODUCT_VISION.md`;
4. `docs/DOMAIN_MODEL.md`;
5. `docs/ARCHITECTURE.md`;
6. `docs/TRAINING_SCIENCE.md`;
7. `docs/PLANNING.md`;
8. `README.md`;
9. arquivo dos roadmaps históricos.

## 13. Regra de avanço

Cada fase deve resultar em commits pequenos e verificáveis. Não se deve iniciar a fase seguinte enquanto permanecer um bloqueador estrutural da fase atual.

O primeiro trabalho após a aprovação destes documentos será:

> Reescrever `docs/PRODUCT_VISION.md` para definir de forma inequívoca o produto, o atleta-alvo e os limites da primeira aplicação pública.

