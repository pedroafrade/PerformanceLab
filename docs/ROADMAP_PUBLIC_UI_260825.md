# PerformanceLab — Roadmap até à alpha privada

**Atualizado:** 21 de setembro de 2026

**Fonte auditada:** branch `main`, commit `c0788c4` (`Align Today spacing and improve Recovery Log visibility`)

**Objetivo:** disponibilizar uma alpha privada a 3–5 participantes convidados, todos com 18 anos ou mais.

## 1. Regras da alpha

- Sem inscrição pública livre.
- Convites individuais e revogáveis.
- Autenticação externa por OIDC.
- Cada utilizador acede apenas ao atleta autorizado.
- PostgreSQL obrigatório no ambiente alpha.
- Gemini opcional, explicado, consentido e limitado.
- Política de privacidade, exportação e eliminação disponíveis antes dos convites.
- Backups, restauro, logs seguros e resposta a incidentes testados.
- Entrada gradual: contas internas, um participante e só depois o restante grupo.

## 2. Estado global

| Fase | Progresso | Estado |
|---|---:|---|
| A — Contratos de aplicação | 8/8 | concluída |
| B — Identidade e autorização | 11/11 | concluída |
| C — Persistência PostgreSQL | 9/9 | concluída |
| D — Uploads e dados externos | 9/9 | concluída |
| E — Training Coach controlado | 9/9 | concluída |
| F — Privacidade e controlo | **8/9** | revisão jurídica pendente |
| G — Qualidade, segurança e operação | **10/13** | ativação externa e Cloud SQL pendentes |
| H — Deployment e convite | **10/15** | infraestrutura reproduzível preparada; ativação externa pendente |

## 3. Fases concluídas

### Fase A — Contratos de aplicação

Os fluxos essenciais deixaram de depender diretamente da UI. Foram estabilizados contratos de repositório multiatleta e casos de uso para carregar, reconciliar, importar, criar, editar e eliminar dados.

### Fase B — Identidade e autorização

Foram introduzidos identidade OIDC, convites, associação entre utilizador e atleta, autorização central e testes de isolamento. Não devem existir atalhos de demonstração no ambiente alpha.

### Fase C — Persistência PostgreSQL

Foram criados schema, migrações e repositórios PostgreSQL para as entidades necessárias, mantendo implementações em memória/JSON para desenvolvimento e testes. O PostgreSQL deve ser obrigatório no deployment da alpha.

### Fase D — Uploads e dados externos

Foram implementados limites de quantidade e tamanho, validação de conteúdos, processamento temporário, libertação do uploader, mensagens persistentes e divulgação de que os originais não são retidos.

### Fase E — Training Coach controlado

Concluído:

1. divulgação antes da geração;
2. consentimento versionado e revogável;
3. minimização do payload;
4. limites diários por utilizador e globais;
5. bloqueio de pedidos simultâneos duplicados;
6. classificação de erros do fornecedor;
7. metadados operacionais mínimos;
8. interruptor global de configuração;
9. retenção apenas da interpretação mais recente e remoção com a atividade.

## 4. Fase F — Privacidade e controlo do utilizador

### Objetivo

Dar ao participante informação compreensível e controlo verificável sobre os seus dados.

### Passos

- [x] **1. Consentimento de participação na alpha.** Versionado, datado, obrigatório após login e limitado a maiores de 18 anos.
- [x] **2. Rascunho da política de privacidade.** Criado como `RASCUNHO — NÃO PUBLICAR`, com campos pendentes explícitos.
- [ ] **3. Completar factos da política.** Responsável, contacto, finalidades, categorias, fornecedores, alojamento/região, transferências, retenção e direitos. **Próximo passo.**
- [ ] **4. Exportação completa e legível.** Incluir todos os dados associados ao utilizador/atleta.
- [ ] **5. Eliminação integral.** Confirmação forte, prazo definido e cobertura de todos os dados ativos.
- [ ] **6. Política de retenção.** Contas inativas, backups, logs, convites e metadados de IA.
- [ ] **7. Procedimento manual de direitos.** Acesso, correção, portabilidade e eliminação durante a alpha.
- [ ] **8. Limites das recomendações.** Apoio ao treino, não aconselhamento médico.
- [ ] **9. Revisão jurídica.** Obrigatória antes do primeiro convite externo.

### Decisões ainda pendentes

O responsável e o email de privacidade podem ser preenchidos mais tarde, mas têm de estar definidos antes da publicação da política e dos convites.

Ainda é necessário escolher e documentar factualmente:

- alojamento da aplicação;
- fornecedor PostgreSQL e região dos dados;
- localização de backups;
- eventuais transferências internacionais;
- prazos de retenção;
- procedimento e prazo de resposta aos pedidos dos participantes.

Não preencher estes campos por suposição.

### Critério de conclusão

Cada participante sabe o que é recolhido, porquê, onde é tratado, durante quanto tempo, com quem é partilhado e como pode obter, corrigir ou eliminar os seus dados.

## 5. Fase G — Qualidade, segurança e operação

1. Tornar `pyproject.toml` a fonte única das dependências.
2. Incluir todas as dependências de runtime.
3. Definir versões de Python e dependências suportadas.
4. Criar GitHub Actions para pytest e verificações estáticas.
5. Testar fluxos críticos com dois utilizadores.
6. Adicionar logging estruturado sem dados sensíveis.
7. Adicionar captura e alerta de exceções.
8. Criar health check da aplicação, base de dados e configuração.
9. Configurar backups automáticos.
10. Executar e documentar um restauro real.
11. Documentar deployment, migrações, rollback e incidentes.
12. Remover backups de código e artefactos não pertencentes ao produto num commit isolado.
13. Completar `.gitignore` para dados, secrets, ambientes, coberturas, backups e exportações.

### Critério de conclusão

O ambiente é reproduzível, observável e recuperável; uma falha pode ser diagnosticada sem expor dados pessoais; existe backup restaurado e rollback ensaiado.

## 6. Fase H — Deployment e convite

### Estratégia confirmada

- Google Cloud Run para executar a imagem versionada;
- Google Cloud SQL PostgreSQL para persistência;
- Google Secret Manager para configuração protegida e OIDC;
- aplicação privada;
- deployment derivado de commit confirmado da `main`;
- sem indexação pública;
- conta interna separada das contas dos atletas;
- 3–5 participantes convidados gradualmente;
- região da União Europeia para Cloud Run e Cloud SQL;
- suspensão imediata dos convites perante um problema crítico.

### Checklist antes do primeiro convite

- [x] pytest completo e CI sem erros;
- [ ] OIDC e convites funcionais no Cloud Run — implementação e teste
  local concluídos, validação externa pendente;
- [x] isolamento testado com dois utilizadores;
- [x] PostgreSQL obrigatório;
- [x] migrações e rollback testados;
- [ ] backup e restauro confirmados;
- [x] uploads limitados e temporários;
- [x] Gemini limitado, opcional e explicado;
- [ ] política de privacidade e consentimento publicados — implementação
  concluída, revisão jurídica externa pendente;
- [x] exportação e eliminação testadas;
- [ ] logs e alertas ativos — logging concluído, Better Stack externo
  pendente;
- [x] dados de demonstração desativados;
- [x] contacto de suporte visível;
- [x] procedimento de incidente disponível;
- [ ] testes essenciais em desktop, Android e iOS.

### Estado atual

Estado confirmado na `main` em 21 de setembro de 2026, após o commit
`c0788c4` (`Align Today spacing and improve Recovery Log visibility`).

O arranque alpha valida agora, por ordem, a configuração runtime, a
configuração OIDC, a ligação PostgreSQL e as revisões das migrações antes
de iniciar o Streamlit.

Dos 15 requisitos anteriores:

- **10 estão tecnicamente concluídos**;
- **3 estão implementados, mas aguardam validação externa**;
- **2 permanecem pendentes**.

Aguardam validação externa:

- OIDC e convites no endereço real do Cloud Run;
- publicação dos textos após revisão jurídica externa;
- ativação, retenção e alerta real do Better Stack.

Permanecem pendentes:

- backup automático e restauro real no Google Cloud SQL;
- testes essenciais em desktop, Android e iOS.

A configuração reproduzível em `infra/google-alpha/` prepara duas fases. A
primeira cria a infraestrutura base e os cofres vazios. A segunda permanece
bloqueada até existirem segredos válidos, uma imagem fixada pelo respetivo
digest e confirmação humana do plano. A configuração versionada não cria
recursos por si só e não contém valores secretos.

A revisão jurídica externa pendente não impede a continuação do trabalho
técnico das fases G e H, mas impede a publicação final dos textos e
qualquer convite a participantes reais.

Os convites permanecem bloqueados. A preparação atual não cria recursos
Google Cloud, não inicia custos e não inicia o período experimental de
90 dias.

### Entrada gradual

1. Duas contas internas com dados descartáveis.
2. Conjunto anonimizado para validar cálculos e plano.
3. Um participante durante alguns dias.
4. Revisão de erros, custos, compreensão e integridade.
5. Convite gradual dos restantes participantes.

## 7. Próxima sequência recomendada

1. Validar localmente `infra/google-alpha/` com Terraform ou OpenTofu, sem
   executar `apply`.
2. Criar ou escolher o projeto Google Cloud e confirmar a avaliação, o
   orçamento e os alertas.
3. Escolher e registar a região europeia e os contactos reais.
4. Rever o custo apresentado e criar apenas a infraestrutura base.
5. Configurar PostgreSQL, OIDC, Better Stack e os segredos fora do Git.
6. Publicar uma imagem fixada por digest e executar as migrações através do
   job separado.
7. Testar internamente login, isolamento, backup, restauro e rollback.
8. Concluir a revisão jurídica e os testes em desktop, Android e iOS.
9. Convidar primeiro um único participante e só depois o restante grupo.

## 8. Trabalho funcional mantido na calha

- arredondar durações planeadas para blocos de cinco minutos;
- pop-over do histórico de VO₂max;
- auditoria científica do plano;
- adaptações futuras ausentes;
- feedback subjetivo diário;
- uniformização visual e responsiva;
- diferenciação factual entre corrida de estrada e trail através de `sub_sport`.

Estes itens devem usar commits independentes e não ser misturados com privacidade, segurança ou deployment.

## 9. Regra de avanço

Executar um único commit lógico de cada vez. Só avançar depois de pytest específico, pytest completo, confirmação visual quando aplicável, commit e push confirmados pelo utilizador.
