# Instalação online da alpha privada

Esta pasta é o **manual de montagem automático** da infraestrutura Google
Cloud. Aplicar apenas a primeira fase cria a base de dados, os cofres vazios
para os segredos e o local onde será guardada a imagem. Não convida
participantes nem publica a aplicação.

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

## Fase 2 — publicar a aplicação

Só depois de todos os cofres terem pelo menos uma versão válida:

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
