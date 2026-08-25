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

Os valores reais serão configurados através do ambiente seguro do
deployment.

Nunca serão incluídos na imagem:

- `DATABASE_URL`;
- passwords;
- tokens OIDC;
- chave do Gemini;
- DSN do Better Stack;
- certificados;
- dados dos atletas;
- backups;
- exportações.

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

## 9. Estado atual

Neste momento:

- [x] Google Cloud Run escolhido;
- [x] `Dockerfile` preparado;
- [x] `.dockerignore` preparado;
- [x] instalação baseada em `pyproject.toml`;
- [x] execução sem privilégios administrativos;
- [x] verificação técnica do Streamlit preparada;
- [x] imagem construída e testada localmente;
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

Os convites permanecem bloqueados.