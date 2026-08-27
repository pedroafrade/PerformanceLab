# Google Cloud Run — Alpha Privada

**Preparado em:** 25 de agosto de 2026  
**Estado:** CONFIGURAÇÃO PREPARADA — DEPLOYMENT PENDENTE

## 1. Decisão

O Google Cloud Run foi escolhido para alojar a aplicação durante a
alpha privada.

A ativação será feita apenas quando estivermos próximos dos testes
internos no ambiente alpha, para não iniciar prematuramente os
90 dias da avaliação Google Cloud.

## 2. Motivos

O Cloud Run permite:

- executar a aplicação através de um contentor;
- usar a mesma região europeia do Cloud SQL;
- reduzir o serviço a zero quando não está a ser utilizado;
- configurar segredos fora do repositório;
- limitar o acesso ao serviço;
- manter o código independente do fornecedor;
- utilizar `pyproject.toml` como fonte das dependências.

## 3. Contentor

O `Dockerfile`:

- utiliza Python 3.11;
- instala a aplicação através de `pyproject.toml`;
- não utiliza `requirements.txt`;
- executa com um utilizador sem privilégios administrativos;
- escuta no endereço e porta exigidos pelo Cloud Run;
- não inclui dados, testes, documentação ou segredos;
- possui uma verificação técnica do processo Streamlit.

O endpoint interno `/_stcore/health` confirma apenas que o processo
Streamlit está a responder.

A verificação própria do PerformanceLab confirma separadamente a
configuração e a comunicação com o PostgreSQL.

## 4. Segredos

Os valores reais serão guardados no Google Secret Manager e
disponibilizados ao contentor apenas durante a execução.

Existem dois métodos de configuração.

### 4.1. Variáveis de ambiente protegidas

Serão disponibilizados como variáveis de ambiente:

- `PERFORMANCELAB_ENV`;
- `DATABASE_URL`;
- `PRIVACY_CONTACT_EMAIL`;
- `GEMINI_API_KEY`;
- `BETTER_STACK_ERROR_DSN`;
- limites do Training Coach;
- prazos da política de retenção.

### 4.2. Ficheiro de autenticação do Streamlit

A autenticação OIDC do Streamlit necessita de um ficheiro
`secrets.toml`.

No Cloud Run, o conteúdo desse ficheiro será guardado como um segredo
no Google Secret Manager e montado no contentor em:

```text
/app/.streamlit/secrets.toml
```

O ficheiro montado deverá conter a secção `[auth]`, incluindo:

- endereço de retorno público da aplicação;
- segredo do cookie;
- identificador do cliente Google;
- segredo do cliente Google;
- endereço de metadados OIDC da Google.

O endereço de retorno só poderá ser preenchido depois de existir um
endereço interno confirmado para o serviço Cloud Run.

O exemplo versionado
`.streamlit/secrets.toml.example` contém apenas valores fictícios.
O ficheiro real `.streamlit/secrets.toml` permanece ignorado pelo Git.

### 4.3. Regras de segurança

Nunca serão incluídos na imagem ou no repositório:

- `DATABASE_URL` real;
- passwords;
- tokens ou segredos OIDC;
- chave do Gemini;
- DSN real do Better Stack;
- certificados;
- dados dos atletas;
- backups;
- exportações.

Os valores secretos não devem ser escritos nos comandos guardados,
documentação, logs, testes ou histórico do PowerShell.

Esta preparação não cria segredos no Google Cloud, não ativa serviços
e não inicia o período experimental de 90 dias.


## 5. Acesso privado

Antes de qualquer convite será obrigatório:

- impedir acesso público não autenticado;
- configurar autenticação OIDC;
- confirmar convites individuais;
- testar isolamento com duas contas internas;
- confirmar que nenhuma conta de demonstração é criada;
- testar logout e expiração da sessão.

A existência de um endereço Cloud Run não significa que a aplicação
esteja pronta para participantes.

## 6. Região

A região concreta ainda não está ativada.

Quando o ambiente for criado:

- Cloud Run e Cloud SQL deverão ficar na mesma região;
- a região deverá pertencer à União Europeia;
- a localização deverá ser registada na política de privacidade;
- não se deverá assumir uma região antes da confirmação na consola.

## 7. Custos e duração

A configuração no repositório não inicia custos.

Quando a avaliação Google começar serão aplicados:

- limite de 300 USD;
- alertas a 150, 225 e 270 USD;
- fim da alpha com participantes no Dia 60;
- conclusão da migração ou encerramento até ao Dia 85;
- Dia 90 como limite absoluto.

O Cloud Run possui uma franquia mensal gratuita, mas o consumo deverá
ser acompanhado e não se assume custo zero.

## 8. Verificações antes do deployment

Antes de criar o serviço:

- [ ] revisão jurídica externa concluída;
- [ ] contacto de privacidade definido;
- [ ] conta Google Cloud preparada;
- [ ] orçamento e alertas configurados;
- [ ] região europeia escolhida;
- [ ] Cloud SQL criado;
- [ ] backups automáticos ativos;
- [ ] restauro real testado;
- [ ] Better Stack ativo;
- [ ] CI sem erros;
- [ ] commit de deployment registado.

### 8.1. Verificação segura da configuração

Depois de os valores alpha terem sido disponibilizados ao contentor e
antes de iniciar a aplicação, deverá ser executado:

```powershell
python scripts/check_alpha_configuration.py
```

O resultado esperado é:

```text
Alpha runtime configuration is structurally valid.
```

O comando confirma:

- ambiente definido como `alpha`;
- existência e formato do `DATABASE_URL`;
- contacto de privacidade;
- valores obrigatórios da política de retenção;
- coerência dos limites configurados.

O comando não apresenta os valores configurados e não deve imprimir
passwords, endereços da base de dados ou outros segredos.

Esta verificação é apenas estrutural. Não confirma:

- ligação real ao PostgreSQL;
- aplicação das migrações;
- conteúdo do ficheiro OIDC `secrets.toml`;
- funcionamento do login Google;
- Better Stack;
- backups ou restauro;
- disponibilidade pública da aplicação.

Uma falha deste comando bloqueia o arranque do ambiente alpha.

### 8.2. Bloqueio automático do arranque alpha

O contentor executa automaticamente a verificação segura antes de
iniciar o Streamlit quando `PERFORMANCELAB_ENV=alpha`.

Se a configuração estiver incompleta ou for inválida:

- o preflight termina com erro;
- o Streamlit não é iniciado;
- o contentor termina;
- nenhuma configuração secreta é apresentada.

Nos ambientes `local` e `test`, o preflight alpha não é executado.

A CI confirma separadamente que:

- o contentor local inicia e responde no endpoint de saúde;
- um contentor alpha sem configuração obrigatória é recusado;
- a recusa contém a mensagem segura produzida pelo preflight.

Esta prova utiliza apenas uma configuração alpha deliberadamente
incompleta. Não contém segredos reais e não testa a ligação ao Cloud SQL.

### 8.3. Verificação da configuração OIDC

No ambiente alpha, o segundo preflight valida o ficheiro montado em:

```text
/app/.streamlit/secrets.toml
```

Antes de iniciar o Streamlit, confirma a existência da secção `[auth]`
e de todos os campos obrigatórios:

- `redirect_uri`;
- `cookie_secret`;
- `client_id`;
- `client_secret`;
- `server_metadata_url`.

A validação não apresenta os valores destes campos. Se o ficheiro não
existir, não for TOML válido ou estiver incompleto, o contentor termina
antes de iniciar o Streamlit.

A CI verifica os dois resultados:

- ausência do ficheiro OIDC bloqueia o arranque alpha;
- o exemplo fictício pode ser montado como readonly e é aceite
  estruturalmente pelo preflight dentro da imagem.

Esta validação não confirma que as credenciais Google são reais, que o
endereço de retorno está registado ou que o login funciona no serviço
Cloud Run.

### 8.4. Verificação da ligação PostgreSQL

No ambiente alpha, o terceiro preflight é executado depois das
verificações runtime e OIDC e antes de iniciar o Streamlit.

O preflight:

- constrói a configuração alpha validada;
- cria o bundle de repositórios PostgreSQL;
- executa a verificação de saúde existente com `SELECT 1`;
- confirma que a base de dados responde;
- encerra sempre as ligações e o engine utilizados no teste;
- não apresenta o `DATABASE_URL`, credenciais, host ou erro interno.

Se a ligação não estiver disponível, o contentor termina com a mensagem:

```text
Alpha database connection is unavailable.
```

A CI confirma que uma configuração runtime completa e um ficheiro OIDC
estruturalmente válido chegam ao preflight PostgreSQL. A base de dados
fictícia permanece indisponível e o Streamlit não é iniciado.

Esta prova confirma o bloqueio seguro, mas não valida ainda uma ligação
real ao Google Cloud SQL, migrações aplicadas, backups ou restauro.

### 8.5. Verificação das migrações

No ambiente alpha, o quarto preflight é executado depois da verificação
da ligação PostgreSQL e antes de iniciar o Streamlit.

O preflight:

- lê as revisões de topo definidas pelas migrações do repositório;
- consulta as revisões atualmente aplicadas na base de dados;
- aceita a base de dados apenas quando os dois conjuntos coincidem;
- suporta mais do que uma revisão de topo;
- encerra sempre a ligação e o engine;
- não apresenta o `DATABASE_URL`, credenciais, host ou erro interno.

Se a base de dados não tiver revisões, estiver desatualizada ou não
corresponder às migrações da imagem, o contentor termina com:

```text
Alpha database migrations are not current.
```
Quando todas as revisões estão aplicadas, o resultado é:

Alpha database migrations are current.

Esta verificação não aplica migrações automaticamente. As migrações
devem ser executadas como uma operação controlada antes de iniciar a
nova revisão do serviço.

A validação local utiliza implementações fictícias e confirma a lógica
de comparação sem contactar uma base de dados real. A confirmação no
Google Cloud SQL permanece dependente da criação do ambiente alpha.

## 9. Estado atual

Neste momento:

- [x] Google Cloud Run escolhido;
- [x] `Dockerfile` preparado;
- [x] `.dockerignore` preparado;
- [x] instalação baseada em `pyproject.toml`;
- [x] execução sem privilégios administrativos;
- [x] verificação técnica do Streamlit preparada;
- [x] imagem construída e testada localmente;
- [x] construção e verificação de saúde automáticas na CI;
- [x] preflight alpha integrado e recusa automática validada na CI;
- [x] configuração OIDC estruturalmente validada antes do arranque;
- [x] ligação PostgreSQL obrigatória antes do arranque alpha;
- [x] revisões da base de dados validadas antes do arranque alpha;
- [ ] serviço Cloud Run criado;
- [ ] acesso privado confirmado;
- [ ] segredos configurados;
- [ ] aplicação ligada ao Cloud SQL;
- [ ] deployment interno validado.

### Verificação local do contentor

A imagem foi construída e executada localmente com Docker Desktop.

Foi confirmado que:

- o processo Streamlit inicia na porta `8080`;
- a verificação de saúde do contentor responde;
- a aplicação funciona sem incluir segredos na imagem;
- o ficheiro local `secrets.toml` pode ser montado apenas durante a execução;
- a autenticação Google identifica o utilizador;
- um email sem convite é recusado antes de carregar dados de atleta.

Esta verificação não constitui um deployment no Google Cloud e não
inicia o período experimental de 90 dias.

O teste local não valida ainda:

- ligação ao Google Cloud SQL;
- segredos fornecidos pelo Google Secret Manager;
- acesso privado ao serviço Cloud Run;
- backups ou restauro;
- alertas externos;
- funcionamento com duas contas internas convidadas.

### Verificação automática do contentor

Em cada push para a `main` e em cada pull request, a CI:

- constrói a imagem a partir do `Dockerfile`;
- inicia um contentor temporário sem segredos;
- aguarda pelo arranque do Streamlit;
- confirma o endpoint `/_stcore/health`;
- remove sempre o contentor temporário.

A imagem usada nesta verificação não é publicada num registo e não é
enviada para o Google Cloud.

Esta verificação prova que o contentor pode ser construído e iniciado.
Não substitui a futura validação da autenticação, PostgreSQL, segredos,
backups e alertas no ambiente alpha.

Os convites permanecem bloqueados.