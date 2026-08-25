# PerformanceLab — Roadmap até à alpha privada

**Atualizado:** 14 de agosto de 2026  
**Fonte auditada:** branch `main`, commit `043bc343f010ed05464d202958236c3b77c5b9a5` (`Simplify plan generation modal`)  
**Objetivo:** disponibilizar uma primeira fase privada de testes a 3–5 atletas convidados, com dados reais isolados por utilizador, persistência remota e operação controlada.

## 1. Definição da alpha privada

A alpha privada não é apenas a aplicação Streamlit atual colocada online.

Para este roadmap, a alpha privada é uma aplicação que:

- só pode ser usada por pessoas convidadas;
- autentica cada pessoa através de um fornecedor de identidade;
- associa cada conta ao respetivo atleta;
- impede acesso aos dados de outros atletas;
- guarda os dados fora do sistema de ficheiros local da aplicação;
- suporta reinícios sem perda de dados;
- protege segredos e ficheiros importados;
- permite diagnosticar falhas sem expor dados pessoais;
- explica o caráter experimental das recomendações;
- possui um processo simples de suporte, exportação e eliminação;
- pode ser retirada ou revertida rapidamente se surgir um problema crítico.

A alpha privada não implica ainda:

- abertura anónima ao público;
- indexação em motores de pesquisa;
- integração automática com Apple, Garmin ou Strava;
- funcionalidades completas de treinador;
- pagamentos;
- garantias clínicas ou aconselhamento médico;
- escala para um número elevado de utilizadores.

## 2. Princípios de execução

- GitHub `main` é a única fonte da verdade.
- Um commit lógico de cada vez.
- Alterações pequenas, testáveis e reversíveis.
- A aplicação local deve continuar funcional durante a transição.
- O domínio não depende de Streamlit, autenticação, JSON ou base de dados.
- A UI apresenta e encaminha; casos de uso coordenam; repositórios persistem.
- Nenhuma identidade recebida do browser autoriza diretamente um recurso.
- Toda a leitura ou escrita de dados pessoais é limitada ao utilizador autenticado.
- Os ficheiros locais `data/` nunca são enviados para GitHub nem usados em produção.
- Segredos nunca são guardados no repositório ou apresentados em logs.
- Dados enviados ao Gemini são minimizados e identificados como processamento externo.
- Não se avança para convites reais enquanto existir um bloqueador de segurança ou integridade.

## 3. Auditoria confirmada do estado atual

### 3.1. Base funcional já existente

O produto já possui uma base adequada para continuar:

- domínio centrado em `Athlete`;
- identificadores persistentes para atleta, utilizador e atividades;
- histórico, eventos, plano, reconciliação e adaptações persistidos;
- modelos de VO₂max factual e interpretações do Training Coach;
- importação FIT, FIT.GZ, GPX e Strava CSV;
- serialização JSON versionada e testada;
- `User` com papéis `athlete` e `coach`;
- protocolos de repositório;
- testes extensos de domínio, apresentação, importação e armazenamento;
- separação parcial entre domínio, presenters e Streamlit.

Estas capacidades devem ser preservadas. A passagem à alpha é uma troca controlada das fronteiras de aplicação e infraestrutura, não uma reescrita do domínio.

### 3.2. Persistência

Estado confirmado:

- `app/app.py` instancia diretamente `JsonAthleteRepository` e `JsonUserRepository`;
- atletas são guardados em `data/athletes/<athlete_id>.json`;
- utilizadores são guardados em `data/users/<user_id>.json`;
- `JsonAthleteRepository` suporta `get`, `list`, `save` e `delete`;
- o protocolo `AthleteRepository` ainda descreve sobretudo o modo antigo de atleta único;
- a gravação do atleta ocorre em vários pontos da UI;
- parte da gravação depende de `st.session_state.notice`;
- histórico, plano e interpretações são guardados como um único agregado JSON;
- não existe transação entre operações concorrentes;
- duas sessões podem carregar a mesma versão e a última gravação substituir a anterior;
- o disco efémero de um alojamento Streamlit não constitui persistência durável.

Conclusão:

> O JSON local é adequado para desenvolvimento e migração, mas bloqueia a alpha privada com vários utilizadores.

### 3.3. Identidade e autorização

Estado confirmado:

- `AuthenticationService.login()` autentica apenas através do endereço de email;
- não existe prova de identidade, password, OIDC ou sessão de servidor validada;
- o objeto autenticado vive em `st.session_state`;
- quando não existem utilizadores, a aplicação cria automaticamente contas de demonstração;
- uma conta de atleta carrega o `athlete_id` associado;
- uma conta `coach` carrega implicitamente o primeiro atleta por ordem alfabética;
- a página Accounts lista utilizadores a qualquer conta com papel `coach`;
- não existe relação explícita e autorizada treinador–atleta;
- não existem testes end-to-end de isolamento entre dois utilizadores autenticados.

Conclusão:

> O modelo atual é uma simulação de autenticação local. Não pode proteger dados reais numa aplicação remota.

### 3.4. Casos de uso e gravação

Estado confirmado:

- `app/app.py` coordena autenticação, criação de demonstração, carregamento, reconciliação, navegação e persistência;
- `app/components/import_panel.py` coordena leitura, merge, RPE, reconciliação e mensagens;
- editar, eliminar, importar, gerar plano e reconciliar não passam por uma unidade de trabalho comum;
- a UI conhece repositórios concretos e decide quando guardar;
- ainda não existe controlo de concorrência otimista nem versão persistente do agregado.

Conclusão:

> Antes da base de dados, os fluxos que alteram vários elementos do atleta devem ser extraídos para casos de uso atómicos e testáveis sem Streamlit.

### 3.5. Uploads

Estado confirmado:

- o tipo do ficheiro é escolhido principalmente pela extensão;
- FIT.GZ é descomprimido integralmente em memória;
- não existe limite de tamanho descomprimido no domínio da aplicação;
- não existe validação explícita de assinatura ou conteúdo antes de importar;
- uma importação em lote captura `Exception` e apresenta apenas uma contagem genérica;
- os originais não são necessários depois da importação atual, mas esta política não está documentada;
- não existe teste de ficheiro comprimido malicioso, tamanho excessivo ou concorrência de imports.

Conclusão:

> A alpha deve processar uploads temporariamente, impor limites antes e depois da descompressão e eliminar os originais após o processamento, salvo decisão explícita em contrário.

### 3.6. Gemini e serviços externos

Estado confirmado:

- a chave é obtida através de `GEMINI_API_KEY` pelo SDK oficial;
- `gemini-3.5-flash` é o modelo configurado;
- a interpretação estruturada e a persistência já funcionam;
- diferentes falhas do provider são convertidas no mesmo estado genérico;
- não existe limite de utilização por utilizador;
- não existe registo operacional de latência, resultado ou consumo;
- o payload contém dados da atividade e contexto do atleta;
- ainda não existe consentimento ou informação de privacidade específica para este envio.

Conclusão:

> O Training Coach pode participar na alpha apenas com transparência, minimização, limites e possibilidade de ser desativado sem afetar o resto da aplicação.

### 3.7. Dependências, testes e operação

Estado confirmado:

- `requirements.txt` e `pyproject.toml` não contêm exatamente as mesmas dependências;
- as dependências críticas não possuem limites superiores ou lock reproduzível;
- não existe workflow em `.github/workflows/` para executar pytest;
- não existe mecanismo de migrações de base de dados;
- não existe logging estruturado nem monitorização externa;
- não existe health check;
- não existe procedimento testado de backup, recuperação ou rollback;
- `app/app_backup.py`, `.coverage` e `PLANO_DE_TREINO.txt` permanecem versionados;
- `.gitignore` ignora `data/athletes/` e `data/users/`, mas não define ainda uma política completa para secrets e artefactos locais.

Conclusão:

> O deployment só deve acontecer depois de a construção ser reproduzível, os testes correrem automaticamente e existir recuperação operacional mínima.

### 3.8. Privacidade e direitos do utilizador

Estado confirmado:

- não existe política de privacidade na aplicação;
- não existe consentimento de participação na alpha;
- não existe exportação completa da conta e dos dados do atleta;
- não existe eliminação integral de conta, atleta e dados relacionados;
- não existe política de retenção;
- não existe registo de aceitação de termos ou versão da política;
- alguns dados incluem localização, frequência cardíaca, desempenho, recuperação e feedback subjetivo.

Conclusão:

> A alpha necessita de informação clara, consentimento, minimização e processos de exportação e eliminação antes de aceitar dados reais.

## 4. Bloqueadores atuais da alpha

São bloqueadores absolutos:

1. login apenas por email;
2. seleção implícita do primeiro atleta para contas coach;
3. persistência em `data/` local;
4. ausência de autorização por recurso;
5. ausência de transações ou controlo de concorrência;
6. criação automática de dados e contas de demonstração;
7. uploads sem limites explícitos de segurança;
8. ausência de exportação e eliminação integral;
9. ausência de CI, backups testados e rollback;
10. ausência de informação e consentimento para dados pessoais e Gemini.

A melhoria visual, o pop-over de VO₂max e o arredondamento dos treinos para blocos de cinco minutos não removem estes bloqueadores. Podem continuar em paralelo apenas quando não atrasarem a sequência estrutural.

## 5. Arquitetura alvo mínima

```text
Browser
  → Streamlit UI
  → identidade OIDC validada
  → casos de uso da aplicação
  → autorização por user_id e athlete_id
  → repositórios abstratos
  → PostgreSQL transacional

Uploads
  → validação e limites
  → memória/ficheiro temporário
  → importador FIT/GPX
  → caso de uso transacional
  → eliminação do original temporário

Training Coach
  → consentimento e limite por utilizador
  → payload minimizado
  → Gemini
  → resultado ou erro classificado
  → persistência associada ao atleta autorizado
```

O domínio continua independente desta infraestrutura.

## 6. Fase A — Fechar contratos de aplicação

### Objetivo

Retirar da UI a responsabilidade de coordenar alterações persistentes.

### Commits previstos

1. Atualizar `AthleteRepository` para o contrato multiatleta realmente usado: `get`, `save`, `delete` e, apenas para administração autorizada, `list`.
2. Remover do contrato público `path`, `load()` sem identidade e `exists()` sem identidade.
3. Criar resultado explícito para `LoadActiveAthlete` e reconciliação idempotente.
4. Criar caso de uso `ImportActivities` com resultados por ficheiro.
5. Criar caso de uso `GenerateTrainingPlan`.
6. Criar casos de uso para editar e eliminar atividades.
7. Fazer cada caso de uso persistir apenas depois de todas as regras terminarem com sucesso.
8. Fazer os componentes Streamlit receberem callbacks/resultados, não repositórios concretos.

### Testes obrigatórios

- casos de uso com repositórios em memória;
- nenhuma gravação quando uma regra falha;
- uma gravação por alteração lógica;
- reconciliação idempotente;
- mensagens de resultado sem dependência de Streamlit.

### Critério de conclusão

Os principais fluxos de escrita podem ser executados e testados sem iniciar Streamlit e sem conhecer JSON ou PostgreSQL.

## 7. Fase B — Identidade externa e autorização

### Objetivo

Provar a identidade e autorizar cada recurso antes de o carregar.

### Decisão proposta

Usar autenticação OIDC suportada pelo Streamlit, inicialmente com Google, sem guardar passwords no PerformanceLab.

### Commits previstos

1. Introduzir um modelo imutável de identidade autenticada externa: `subject`, `issuer`, email verificado e nome opcional.
2. Separar identidade externa de `User` persistido.
3. Criar um serviço de provisão apenas para emails previamente convidados.
4. Associar de forma única `(issuer, subject)` a um `user_id` interno.
5. Substituir o formulário de email por `st.login()` e `st.logout()`.
6. Validar a sessão em cada execução antes de carregar o atleta.
7. Criar `AuthorizationService` ou políticas equivalentes para `user_id → athlete_id`.
8. Remover o acesso implícito do coach ao primeiro atleta.
9. Desativar o papel coach na primeira alpha, salvo relação treinador–atleta explicitamente persistida e testada.
10. Remover criação automática de utilizadores e atleta de demonstração em configuração alpha/produção.
11. Manter o modo de desenvolvimento local atrás de configuração explícita.

### Testes obrigatórios

- utilizador não convidado é recusado;
- identidade externa repetida resolve sempre o mesmo utilizador;
- atleta A não consegue carregar, alterar ou eliminar atleta B;
- URL, estado de sessão ou parâmetros adulterados não mudam a autorização;
- sessão terminada deixa de aceder aos dados;
- conta sem atleta apresenta onboarding, não dados de outro atleta.

### Critério de conclusão

Nenhum atleta é carregado antes da autenticação e autorização, e não existe seleção implícita de outro atleta.

## 8. Fase C — Persistência PostgreSQL

### Objetivo

Substituir o disco local por persistência transacional e concorrente.

### Estratégia

Na primeira iteração, preservar `Athlete` como agregado e guardar uma representação versionada, juntamente com índices relacionais mínimos. Não decompor prematuramente todo o domínio em dezenas de tabelas.

### Estrutura mínima proposta

- `users`;
- `external_identities`;
- `athletes`;
- `user_athlete_access`;
- `athlete_snapshots` ou documento versionado equivalente;
- `schema_migrations`;
- `alpha_invitations`;
- `consents`;
- `ai_usage_events`;
- `audit_events` para operações sensíveis sem payload fisiológico.

### Commits previstos

1. Escolher biblioteca de base de dados e ferramenta de migrações.
2. Introduzir configuração `local`, `test` e `alpha`.
3. Implementar repositórios PostgreSQL através dos mesmos protocolos.
4. Adicionar versão do agregado ou `updated_at` para concorrência otimista.
5. Executar importação, edição, eliminação, reconciliação e geração dentro de transações.
6. Criar migração inicial e comando de aplicação/rollback de migrações.
7. Criar ferramenta explícita de migração de um atleta JSON para a base de dados.
8. Validar round-trip entre JSON atual, domínio e persistência PostgreSQL.
9. Impedir que o ambiente alpha arranque com repositórios JSON.

### Testes obrigatórios

- integração contra PostgreSQL de teste;
- migrações do zero e atualização entre versões;
- rollback de transação após falha;
- conflito entre duas edições concorrentes;
- isolamento por `athlete_id` em todas as consultas;
- migração de um atleta real anonimizado;
- reinício da aplicação sem perda de dados.

### Critério de conclusão

O ambiente alpha não lê nem escreve em `data/`, todas as alterações lógicas são transacionais e conflitos não causam substituição silenciosa.

## 9. Fase D — Uploads e dados externos

### Objetivo

Permitir importação sem conservar ficheiros desnecessários nem aceitar cargas perigosas.

### Commits previstos

1. Definir formatos, número máximo de ficheiros e tamanho máximo por upload.
2. Definir limite máximo depois da descompressão de FIT.GZ.
3. Validar extensão, assinatura e estrutura antes de construir `Workout`.
4. Processar uploads em memória ou diretório temporário isolado.
5. Eliminar sempre o original temporário após sucesso ou falha.
6. Devolver resultado individual: importado, atualizado, duplicado, ignorado ou inválido.
7. Não incluir caminhos, conteúdo bruto ou dados fisiológicos nos logs.
8. Adicionar proteção contra repetição rápida e importações concorrentes.
9. Documentar que os ficheiros originais não são conservados na alpha.

### Testes obrigatórios

- extensão falsa;
- formato não suportado;
- ficheiro vazio ou truncado;
- gzip excessivamente expandido;
- lote parcialmente inválido;
- duplicados;
- limpeza dos temporários;
- importações simultâneas do mesmo atleta.

### Critério de conclusão

Nenhum upload ultrapassa os limites definidos, os originais são eliminados e cada falha é explicável ao utilizador.

## 10. Fase E — Training Coach controlado

### Objetivo

Manter a funcionalidade de IA na alpha sem criar exposição ou custo ilimitado.

### Commits previstos

1. Apresentar informação clara antes da primeira geração sobre dados enviados e finalidade.
2. Registar consentimento versionado e permitir retirar consentimento.
3. Rever e minimizar o payload, removendo identificadores e factos desnecessários.
4. Introduzir limite diário por utilizador e limite global configurável.
5. Impedir pedidos duplicados enquanto uma geração está em curso.
6. Classificar erros de configuração, autenticação, quota, pedido, segurança e indisponibilidade.
7. Registar apenas metadados operacionais: utilizador interno, instante, modelo, estado, latência e contagem disponível de utilização.
8. Permitir desativar o provider por configuração sem impedir o uso de Activities.
9. Rever retenção das interpretações e respetivo processo de eliminação.

### Testes obrigatórios

- ausência de consentimento impede geração;
- limite por utilizador;
- falhas não descontam indevidamente ou não duplicam consumo;
- payload não contém email nem identificadores externos;
- provider indisponível não corrompe a atividade;
- eliminação da conta remove interpretações persistidas.

### Critério de conclusão

O Training Coach é opcional, limitado, transparente e isolado das restantes funções.

## 11. Fase F — Privacidade e controlo do utilizador

### Objetivo

Dar ao participante informação e controlo adequados sobre os seus dados.

### Commits previstos

1. Criar aviso de alpha e consentimento informado, com versão e data.
2. Criar política de privacidade adequada ao âmbito real e aos fornecedores usados.
3. Indicar responsável, contacto, finalidade, categorias de dados, fornecedores, retenção e direitos.
4. Criar exportação completa e legível dos dados do utilizador.
5. Criar eliminação integral com confirmação forte e prazo definido.
6. Definir política de retenção para contas inativas, backups, logs e convites.
7. Criar procedimento manual documentado para pedidos de acesso, correção ou eliminação durante a alpha.
8. Identificar claramente recomendações como apoio ao treino, não aconselhamento médico.
9. Rever juridicamente os textos antes de convidar participantes.

### Testes obrigatórios

- consentimento obrigatório e versionado;
- exportação contém todos os dados associados;
- eliminação remove ou agenda de forma verificável todos os dados ativos;
- utilizador eliminado não consegue voltar a aceder sem novo convite;
- logs e backups seguem a política documentada.

### Critério de conclusão

Cada participante sabe o que é guardado e consegue obter ou eliminar os seus dados através de um processo testado.

### Estado atual da fase F

A fase F possui 8 de 9 passos concluídos.

O passo 9.2, correspondente à revisão jurídica externa dos textos e procedimentos da alpha privada, fica temporariamente pendente.

Esta decisão permite avançar com o trabalho técnico da fase G, mas não elimina o bloqueador jurídico. Antes do primeiro convite a participantes reais será obrigatório:

- obter uma revisão jurídica externa;
- registar o responsável pela revisão, a data e o resultado;
- aplicar as correções exigidas;
- confirmar a versão final da política de privacidade, retenção, consentimentos e procedimentos de exercício de direitos.

Enquanto estas condições não forem cumpridas, os documentos jurídicos permanecem rascunhos e a fase F não deve ser considerada integralmente concluída.

## 12. Fase G — Qualidade, segurança e operação

### Objetivo

Tornar a alpha reproduzível, observável e recuperável.

### Commits previstos

1. Tornar `pyproject.toml` a fonte única de dependências da aplicação.
2. Incluir Streamlit, Plotly, fitdecode e todas as dependências de runtime.
3. Definir versões suportadas e estratégia de atualização.
4. Criar GitHub Actions para pytest e verificações estáticas mínimas.
5. Criar testes dos fluxos críticos com dois utilizadores.
6. Introduzir logging estruturado com identificadores de correlação e sem dados sensíveis.
7. Adicionar captura e alerta de exceções no ambiente alpha.
8. Criar health check ou verificação equivalente da aplicação, base de dados e configuração.
9. Configurar backups automáticos da base de dados.
10. Executar e documentar um restauro real de backup.
11. Documentar deployment, migrações, rollback e resposta a incidente.
12. Remover `app/app_backup.py` e artefactos versionados não pertencentes ao produto num commit separado e confirmado.
13. Completar `.gitignore` para `data/`, secrets, `.env`, coberturas, backups e exportações locais.

### Critérios de conclusão

- cada push relevante é validado automaticamente;
- o ambiente é reconstruível a partir do repositório e secrets;
- uma falha possui correlação e diagnóstico sem expor dados pessoais;
- existe backup restaurado com sucesso;
- existe rollback documentado e ensaiado;
- nenhum dado de demonstração é criado no ambiente alpha.

## 13. Fase H — Deployment e convite

### Objetivo

Disponibilizar a aplicação apenas ao grupo inicial e aprender com utilização real.

### Estratégia proposta

- Streamlit Community Cloud ou alojamento equivalente para a primeira alpha;
- aplicação privada;
- repositório privado ou acesso de deployment devidamente limitado;
- secrets configurados no alojamento;
- PostgreSQL gerido com backups;
- domínio `streamlit.app` inicialmente suficiente;
- 3–5 participantes convidados por email;
- uma conta interna de administração separada das contas de atleta;
- deployment alpha derivado de um commit confirmado da `main`;
- sem indexação pública e sem inscrição livre.

### Checklist antes do primeiro convite

- [ ] pytest completo e CI sem erros;
- [ ] autenticação OIDC funcional;
- [ ] allowlist de convites funcional;
- [ ] teste de isolamento com atleta A e atleta B;
- [ ] PostgreSQL obrigatório no ambiente alpha;
- [ ] migrações aplicadas e rollback disponível;
- [ ] backup e restauro confirmados;
- [ ] uploads limitados e temporários;
- [ ] Gemini limitado, opcional e explicado;
- [ ] política de privacidade e consentimento disponíveis;
- [ ] exportação e eliminação testadas;
- [ ] logs e alertas ativos;
- [ ] dados de demonstração desativados;
- [ ] contacto de suporte visível;
- [ ] plano de incidente e suspensão da aplicação disponível;
- [ ] teste em desktop, Android e iOS nos fluxos essenciais.

### Plano de entrada

1. Testar com duas contas internas e dados descartáveis.
2. Importar um conjunto anonimizado e validar cálculos e plano.
3. Convidar um participante durante alguns dias.
4. Rever erros, custos, compreensão e integridade dos dados.
5. Convidar os restantes participantes gradualmente.
6. Suspender novos convites sempre que surgir um problema crítico.

### Feedback mínimo a recolher

- sucesso ou falha do onboarding;
- tempo até criar o primeiro plano;
- sucesso das importações;
- compreensão de Today, Plan, Activities, Calendar e Development;
- recomendações consideradas inesperadas;
- adaptações não compreendidas;
- erros e perdas de estado;
- desempenho em telemóvel;
- utilização e custo do Gemini;
- confiança e dúvidas sobre privacidade.

### Critério de conclusão da alpha inicial

- nenhuma fuga ou mistura de dados;
- nenhuma perda ou corrupção de dados;
- nenhum plano alterado repetidamente pela mesma reconciliação;
- backups recuperáveis;
- fluxos essenciais concluídos sem assistência constante;
- problemas críticos corrigidos antes de aumentar o grupo.

## 14. Ordem dos primeiros commits

Depois deste documento, a sequência inicial recomendada é:

1. alinhar o protocolo `AthleteRepository` com operações multiatleta;
2. criar repositório em memória para testes de casos de uso;
3. extrair `LoadActiveAthlete` e reconciliação de `app/app.py`;
4. extrair `ImportActivities` de `app/components/import_panel.py`;
5. extrair geração, edição e eliminação para casos de uso;
6. introduzir identidade externa e autorização;
7. só depois implementar PostgreSQL através dos contratos estabilizados.

Não se deve começar pelo deployment nem pelo botão de login isolado. Primeiro é necessário garantir que carregar e alterar um atleta passa por uma fronteira autorizável e transacional.

## 15. Trabalho funcional mantido na calha

Não pertence ao caminho crítico da alpha, mas permanece registado:

- corrigir durações planeadas para blocos de cinco minutos;
- adicionar pop-over com histórico de VO₂max;
- continuar a auditoria científica do plano;
- investigar adaptações futuras ausentes;
- completar feedback subjetivo diário;
- continuar a uniformização visual e responsiva.

Estes itens devem manter commits separados dos commits de identidade, persistência e segurança.

## 16. Regra de avanço

Cada fase só termina quando os respetivos testes e critérios forem confirmados.

Uma funcionalidade visualmente pronta não compensa uma lacuna de autenticação, autorização, persistência, privacidade ou recuperação. Se surgir dúvida sobre isolamento ou integridade dos dados, a alpha não avança até existir prova através de testes.
