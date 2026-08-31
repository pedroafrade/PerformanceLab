# Registo de Deployment da Alpha Privada

**Estado:** MODELO — NÃO REPRESENTA UM DEPLOYMENT EXECUTADO

Criar uma cópia deste modelo para cada operação. Não substituir este
ficheiro pelo registo de uma operação real.

## 1. Identificação

- Data e hora UTC:
- Pessoa responsável:
- Ambiente: `alpha`
- Decisão: avançar / suspender / rollback
- Motivo da decisão:

## 2. Código e imagem

- Commit completo da `main`:
- URL da execução da CI:
- Resultado da CI:
- Referência da imagem:
- Digest imutável da imagem:
- Label OCI `org.opencontainers.image.revision`:
- Revisão do Cloud Run:
- Região do Cloud Run:

O commit, o label OCI e o commit associado ao digest devem coincidir.

## 3. Base de dados

- Instância Cloud SQL:
- Região Cloud SQL:
- Revisões Alembic antes da operação:
- Revisões Alembic esperadas:
- Revisões Alembic depois da operação:
- Identificador do backup anterior:
- Estado do backup:
- Restauro disponível: sim / não
- Migração aplicada: sim / não

Não registar o `DATABASE_URL`, utilizadores, passwords, endereços
privados ou outros valores de ligação.

## 4. Preflights

- Referência imutável da imagem: passou / falhou
- Configuração runtime: passou / falhou
- Configuração OIDC: passou / falhou
- Ligação PostgreSQL: passou / falhou
- Revisões das migrações: passou / falhou

Uma falha da referência imutável bloqueia o deployment.
Qualquer falha dos restantes preflights bloqueia o arranque da
aplicação.

## 5. Verificação interna

- Endpoint de saúde: passou / falhou
- Login da primeira conta interna: passou / falhou
- Login da segunda conta interna: passou / falhou
- Isolamento entre contas: passou / falhou
- Importação com dados descartáveis: passou / falhou
- Exportação com dados descartáveis: passou / falhou
- Eliminação com dados descartáveis: passou / falhou
- Alertas operacionais: passou / falhou

Não incluir emails, nomes, identificadores OIDC ou dados dos atletas.

## 6. Rollback

- Commit anterior confirmado:
- Digest anterior confirmado:
- Revisão Cloud Run anterior:
- Alteração incompatível da base de dados: sim / não
- Procedimento de recuperação escolhido:
- Resultado do rollback, se executado:

Nunca registar aqui passwords, tokens, chaves, cookies, DSN, conteúdos
de `secrets.toml` ou valores reais de `DATABASE_URL`.

## 7. Resultado

- Aplicação mantida suspensa: sim / não
- Convites mantidos bloqueados: sim / não
- Operação concluída: sim / não
- Incidente aberto: sim / não
- Referência não sensível do incidente:
- Observações sem dados pessoais:

Este modelo não ativa serviços, não publica imagens, não executa
migrações e não inicia custos.