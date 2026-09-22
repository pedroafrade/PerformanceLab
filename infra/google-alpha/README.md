# Instalação online da alpha privada

Esta pasta é o **manual de montagem automático** da infraestrutura Google
Cloud. Aplicar apenas a primeira fase cria a base de dados, os cofres vazios
para os segredos e o local onde será guardada a imagem. Não convida
participantes nem publica a aplicação.

O ficheiro de controlo do Terraform é guardado no bucket privado
`performancelab-private-alpha-terraform-state`, na região `europe-west1`.
Esse bucket foi criado separadamente, com acesso público bloqueado, acesso
uniforme e histórico de versões. Não guarde uma segunda cópia do estado no Git.

## Antes de começar

Não execute ainda estes passos sem confirmar:

1. conta Google Cloud e avaliação disponíveis;
2. projeto dedicado à alpha;
3. avisos de orçamento configurados na consola;
4. região europeia escolhida;
5. emails reais de privacidade e suporte;
6. CI verde no commit que será publicado.

É necessário instalar o Google Cloud CLI e Terraform ou OpenTofu. Os comandos
abaixo usam `terraform`; pode substituir a palavra por `tofu`.

## Fase 1 — criar a casa vazia

No PowerShell, a partir da raiz do repositório:

```powershell
Copy-Item infra/google-alpha/alpha.auto.tfvars.example infra/google-alpha/alpha.auto.tfvars
notepad infra/google-alpha/alpha.auto.tfvars
gcloud auth login
gcloud auth application-default login
gcloud config set project SEU_PROJECT_ID
terraform -chdir=infra/google-alpha init
terraform -chdir=infra/google-alpha fmt -check
terraform -chdir=infra/google-alpha validate
terraform -chdir=infra/google-alpha plan -out=alpha-base.plan
```

Leia o resumo do `plan`. Nesta fase, `deploy_application` deve continuar como
`false`. Só depois de confirmar os recursos e o custo previsto:

```powershell
terraform -chdir=infra/google-alpha apply alpha-base.plan
```

O primeiro `apply` cria recursos Google Cloud e pode consumir crédito. Não
prossiga sem rever a estimativa na consola.

A base PostgreSQL fixa explicitamente a edição Cloud SQL `ENTERPRISE`. Isto
é necessário para utilizar o tipo partilhado e económico `db-f1-micro`;
PostgreSQL 16 ou posterior escolheria `ENTERPRISE_PLUS` por defeito, que rejeita
esse tipo de máquina.

O comando `init` deve confirmar o backend `gcs`. Se indicar que o bucket não
existe, que o acesso foi recusado ou que pretende usar apenas estado local,
interrompa o processo. Não execute `apply` sem o backend remoto confirmado.

## Paragem obrigatória entre as duas fases

Depois da primeira fase ainda faltam operações deliberadamente manuais:

- criar o utilizador PostgreSQL e uma password forte;
- colocar o `DATABASE_URL` no Secret Manager;
- criar as credenciais OIDC depois de conhecer o endereço final;
- colocar o `secrets.toml` no Secret Manager;
- configurar e testar Better Stack;
- publicar uma imagem identificada pelo seu digest `sha256`;
- testar um backup e um restauro numa base separada.

Os valores secretos nunca são colocados em ficheiros Terraform, argumentos
guardados no histórico, outputs, commits ou screenshots. As instruções da
segunda fase serão usadas apenas depois desta validação.

### Configurar o acesso da aplicação à base de dados

Depois de a Fase 1 terminar sem alterações pendentes, execute na raiz do
repositório:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/configure_google_alpha_database.ps1
```

O assistente confirma o projeto ativo e pede duas vezes uma password com pelo
menos 24 caracteres. Os caracteres ficam ocultos. Em seguida cria o utilizador
`performancelab_app` e adiciona uma versão ao segredo
`performancelab-alpha-database-url`, usando o socket gerido do Cloud SQL. A
password e o `DATABASE_URL` existem apenas em memória durante a operação.

Se o utilizador já existir, o assistente para sem o alterar. Uma recuperação
deliberada pode definir uma password nova e uma nova versão do segredo com:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/configure_google_alpha_database.ps1 -RotateExisting
```

Não utilize `-RotateExisting` durante a primeira execução normal.

## Fase 2 — publicar a aplicação

Só depois de todos os cofres terem pelo menos uma versão válida:

### Publicar uma imagem candidata

Com a `main` limpa, sincronizada e com a CI verde, execute na raiz do
repositório:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/publish_google_alpha_image.ps1
```

O assistente confirma que o commit local coincide com `origin/main`, envia
apenas o contexto permitido por `.gcloudignore`, constrói a imagem no Cloud
Build europeu e publica-a no Artifact Registry. A tag identifica o commit e o
resultado final apresenta uma referência imutável `@sha256:...`.

Este passo publica a imagem mas não cria o serviço Cloud Run. Guarde a
referência imutável para a revisão do plano de deployment; ela não é um
segredo.

### Obter o endereço para configurar o login Google

O endereço de retorno OIDC só é conhecido depois de o serviço Cloud Run
existir. Para quebrar esta dependência sem publicar prematuramente a aplicação,
defina temporariamente no ficheiro privado `alpha.auto.tfvars`:

```hcl
bootstrap_application = true
deploy_application    = false
```

O plano cria o serviço com a imagem oficial vazia do Cloud Run, sem montar a
base de dados ou qualquer segredo. Depois do `apply`, obtenha `service_url` nos
outputs e acrescente `/oauth2callback` para configurar o cliente Google OIDC.
Durante este intervalo pode existir uma página pública de demonstração, mas
não existe PerformanceLab, login ou acesso a dados nesse contentor.

Depois de guardar o OIDC real no Secret Manager, volte a definir:

```hcl
bootstrap_application = false
deploy_application    = true
```

Os dois modos nunca podem estar ativos em simultâneo. A transição atualiza o
mesmo serviço e preserva o seu endereço permanente.

### Ativar o serviço

1. fixe `container_image` com o digest completo `@sha256:...`;
2. altere `deploy_application` para `true`;
3. execute novamente `plan`;
4. confirme que a imagem, região e contactos estão corretos;
5. aplique o plano;
6. execute o job de migrações;
7. confirme o health check e o login com contas internas.

A morada fica tecnicamente acessível para permitir o login Google num browser.
O PerformanceLab continua fechado: uma identidade sem convite individual é
recusada antes de aceder a dados de atleta.

## O que este código não faz

- não guarda valores secretos no estado Terraform;
- não cria versões dos segredos;
- não cria nem envia convites;
- não executa migrações automaticamente;
- não transforma alertas de orçamento num limite automático de despesa;
- não prova que backups e restauro funcionam;
- não elimina a proteção contra remoção da base de dados.

A instância recebe um endereço técnico necessário ao conector gerido do Cloud
SQL, mas não autoriza redes externas. A aplicação liga-se através do conector
do Cloud Run, com identidade própria e tráfego cifrado; a base não é publicada
como um servidor PostgreSQL aberto à Internet.

Consulte também `docs/ALPHA_OPERATIONS_RUNBOOK.md` antes de qualquer convite.
