# Backups da Base de Dados — Alpha Privada

**Preparado em:** 25 de agosto de 2026  
**Estado:** CONFIGURAÇÃO EXTERNA PENDENTE

## 1. Objetivo

Os backups permitem recuperar os dados da alpha privada se a base
de dados PostgreSQL for danificada, eliminada acidentalmente ou
ficar indisponível.

Um backup não substitui a base de dados usada diariamente. É uma
cópia protegida destinada apenas a recuperação.

## 2. Âmbito

Os backups devem abranger toda a base de dados PostgreSQL da alpha,
incluindo:

- utilizadores;
- identidades externas;
- convites;
- autorizações;
- atletas;
- atividades e rotas;
- planos e indicadores;
- consentimentos;
- interpretações e metadados do Training Coach.

Não devem ser criadas cópias locais manuais dentro do repositório,
da pasta `data/` ou do computador usado para desenvolvimento.

## 3. Requisitos aprovados

O serviço PostgreSQL escolhido para a alpha deverá fornecer:

- backups automáticos;
- armazenamento encriptado;
- comunicação encriptada;
- acesso limitado à pessoa responsável pela operação;
- localização na União Europeia;
- conservação de cada backup durante 14 dias;
- eliminação automática no final do prazo;
- possibilidade de restaurar para uma base de dados separada;
- informação sobre a data e o resultado de cada backup.

A retenção de 14 dias corresponde à configuração:

`RETENTION_BACKUP_DAYS=14`

## 4. Decisões externas pendentes

Antes de ativar a alpha ainda é necessário definir e confirmar:

- [ ] fornecedor PostgreSQL;
- [ ] país e região do alojamento;
- [ ] frequência dos backups automáticos;
- [ ] hora aproximada de execução;
- [ ] tipo de backup disponibilizado;
- [ ] encriptação confirmada pelo fornecedor;
- [ ] utilizadores autorizados a aceder aos backups;
- [ ] eliminação automática após 14 dias;
- [ ] alertas em caso de falha;
- [ ] custo do serviço;
- [ ] procedimento de recuperação.

Nenhum fornecedor, país, região ou frequência é assumido enquanto
estas escolhas não forem confirmadas.

## 5. Evidência necessária

Os backups só podem ser considerados ativos depois de existir
evidência factual de que o fornecedor criou pelo menos um backup.

O registo da evidência deverá indicar:

- fornecedor;
- projeto ou base de dados, sem credenciais;
- região;
- data e hora do backup;
- estado apresentado pelo fornecedor;
- prazo de conservação;
- pessoa que fez a verificação.

Não devem ser registados:

- passwords;
- tokens;
- chaves;
- `DATABASE_URL`;
- conteúdo dos dados pessoais;
- ficheiros de backup descarregados.

## 6. Dados eliminados

Os dados eliminados da base ativa podem continuar temporariamente
num backup até este atingir o prazo máximo de 14 dias.

Um restauro não pode reativar silenciosamente contas ou dados que
tenham sido eliminados depois da criação do backup.

O procedimento de restauro deverá reconciliar as eliminações antes
de a base restaurada poder substituir a base ativa.

## 7. Separação do restauro

Um backup nunca deverá ser restaurado diretamente por cima da base
de dados ativa durante um teste.

O teste deverá utilizar uma base de dados separada e descartável,
sem acesso de participantes.

A execução e documentação desse teste pertence ao passo G.8 da
fase G.

## 8. Estado operacional

Neste momento:

- os requisitos mínimos estão documentados;
- o prazo de conservação está aprovado;
- o fornecedor PostgreSQL ainda não foi escolhido;
- os backups automáticos ainda não estão ativos;
- ainda não existe um restauro testado.

Consequentemente, este requisito continua a bloquear os convites
para a alpha privada.