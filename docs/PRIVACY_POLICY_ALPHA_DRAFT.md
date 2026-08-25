# Política de Privacidade — Alpha Privada do PerformanceLab

**Versão do rascunho:** `privacy-alpha-v1`  
**Data do rascunho:** 25 de agosto de 2026  
**Estado:** RASCUNHO — NÃO PUBLICAR  
**Participantes:** exclusivamente pessoas com 18 anos ou mais

> Este documento ainda não está pronto para publicação ou para aceitação por participantes externos. Os campos assinalados como `[POR DEFINIR]` têm de ser preenchidos e o texto deve ser revisto antes do primeiro convite real.

## 1. Responsável pelo tratamento

O responsável pelo tratamento dos dados pessoais é:

- Nome ou entidade: `[POR DEFINIR — RESPONSÁVEL PELO TRATAMENTO]`
- Contacto de privacidade: `[POR DEFINIR — EMAIL DE PRIVACIDADE]`
- País de estabelecimento: Portugal

O PerformanceLab é, nesta fase, um projeto experimental disponibilizado apenas a participantes convidados.

## 2. Âmbito da alpha privada

A alpha privada destina-se exclusivamente a um grupo reduzido de 3–5 participantes convidados, todos com pelo menos 18 anos.

Não existe inscrição pública livre. O acesso depende de convite individual, autenticação externa e autorização para o perfil de atleta associado.

O PerformanceLab encontra-se em desenvolvimento. As funcionalidades, cálculos, planos e recomendações podem ser alterados e podem conter erros.

A participação é voluntária. O PerformanceLab não substitui aconselhamento médico, diagnóstico, tratamento clínico ou acompanhamento por profissionais de saúde.

## 3. Dados pessoais tratados

Consoante as funcionalidades utilizadas, o PerformanceLab pode tratar:

- identidade da conta, incluindo nome, email, identificador externo e emissor da identidade;
- informação relativa ao convite e à associação entre o utilizador e o atleta autorizado;
- dados do perfil de atleta, incluindo idade ou data de nascimento, peso, disponibilidade e preferências de treino;
- atividades desportivas, incluindo data, modalidade, duração, distância, ritmo, potência, cadência, frequência cardíaca e carga de treino;
- rotas, coordenadas geográficas, altitude, desnível e informação associada ao percurso;
- avaliações subjetivas fornecidas pelo participante, incluindo RPE, sensações, sono, stress, motivação, dor, rigidez ou soreness;
- objetivos, provas, planos de treino, sessões planeadas, reconciliações e adaptações;
- estimativas e indicadores de desempenho, recuperação, carga, forma e VO₂max;
- interpretações geradas pelo Training Coach;
- consentimento para participar na alpha e autorização opcional para utilizar o Training Coach;
- registos mínimos de utilização do Training Coach, incluindo data, resultado, fornecedor, modelo, código de erro, latência e limites restantes;
- informação técnica estritamente necessária para segurança, diagnóstico de erros e funcionamento da aplicação.

Alguns destes dados podem revelar informação relacionada com saúde ou condição física e, por isso, exigem proteção reforçada.

Os registos operacionais do Training Coach não devem conter prompts completos nem payload fisiológico.

## 4. Origem dos dados

Os dados podem ser:

- introduzidos diretamente pelo participante;
- importados de ficheiros FIT, FIT.GZ, GPX ou CSV;
- recebidos através da identidade Google usada no login;
- calculados pelo PerformanceLab a partir das atividades e informações fornecidas;
- gerados pelo Training Coach quando o participante pede explicitamente uma interpretação;
- produzidos automaticamente pelo funcionamento técnico da aplicação, por exemplo para aplicar limites de utilização ou registar consentimentos.

Os ficheiros originais de atividade são processados temporariamente para criar registos de treino e não são conservados depois do processamento.

## 5. Finalidades

Os dados são tratados para:

- autenticar a identidade do participante;
- confirmar que a conta foi previamente convidada;
- autorizar o acesso apenas ao perfil de atleta associado;
- criar e manter o perfil de atleta;
- importar, apresentar e analisar atividades;
- calcular carga, recuperação, forma e tendências;
- criar, apresentar, reconciliar e adaptar planos de treino;
- relacionar atividades realizadas com sessões planeadas;
- gerar interpretações opcionais através do Training Coach;
- guardar e respeitar consentimentos e preferências;
- aplicar limites de utilização por participante e limites globais;
- impedir gerações simultâneas duplicadas para a mesma atividade;
- proteger a aplicação e diagnosticar falhas;
- recolher feedback sobre a alpha e melhorar o produto;
- responder a pedidos de acesso, correção, exportação, limitação ou eliminação.

Os dados não serão utilizados para publicidade comportamental nem vendidos a terceiros.

## 6. Fundamento jurídico

Os fundamentos jurídicos aplicáveis a cada finalidade serão confirmados antes da publicação desta política.

A versão final deverá distinguir, pelo menos:

- o tratamento necessário para disponibilizar a conta e as funcionalidades solicitadas;
- o consentimento de participação na alpha;
- o consentimento específico e revogável para o Training Coach;
- o tratamento de dados relacionados com saúde ou condição física;
- a segurança, prevenção de abuso e diagnóstico operacional;
- o cumprimento de obrigações legais, quando aplicável.

**Decisão jurídica pendente:** `[POR DEFINIR — FUNDAMENTOS JURÍDICOS POR FINALIDADE]`

## 7. Fornecedores e destinatários

### Google — autenticação OIDC

O Google é utilizado como fornecedor de identidade através de OIDC.

O PerformanceLab recebe os dados necessários para reconhecer a identidade autenticada, incluindo o identificador externo, o emissor da identidade, o email verificado e, quando disponível, o nome.

A identidade recebida não autoriza diretamente o acesso a um atleta. O PerformanceLab confirma separadamente o convite e a associação entre o utilizador interno e o atleta autorizado.

### Google Gemini — Training Coach

O Google Gemini é utilizado como fornecedor externo do Training Coach.

Esta funcionalidade é opcional, pode ser globalmente desativada e exige uma autorização específica, separada da participação na alpha. Essa autorização pode ser retirada sem impedir a utilização das restantes funcionalidades.

Quando o participante solicita uma interpretação, o PerformanceLab envia ao Gemini um payload textual minimizado com contexto factual selecionado da atividade, treino recente, objetivos e informação adicional relevante.

O ficheiro original da atividade não é enviado ao Gemini.

O modelo configurado atualmente pela aplicação é `gemini-3.5-flash`. Esta identificação deve ser confirmada novamente antes da publicação, porque a configuração poderá mudar.

### PostgreSQL e alojamento

No ambiente alpha, o PerformanceLab exige uma base de dados PostgreSQL. A aplicação não pode utilizar os repositórios JSON locais como alternativa nesse ambiente.

Continuam por escolher ou confirmar:

- Fornecedor da aplicação: `[POR DEFINIR — ALOJAMENTO]`
- Fornecedor PostgreSQL: `[POR DEFINIR — BASE DE DADOS]`
- Região da aplicação: `[POR DEFINIR — REGIÃO DA APLICAÇÃO]`
- Região da base de dados: `[POR DEFINIR — REGIÃO DA BASE DE DADOS]`
- Localização dos backups: `[POR DEFINIR — LOCALIZAÇÃO DOS BACKUPS]`

A lista final de fornecedores, funções e localizações deverá ser confirmada antes da publicação.

## 8. Transferências internacionais

A autenticação Google e o processamento opcional pelo Google Gemini podem envolver tratamento de dados por um fornecedor internacional.

O repositório não determina, por si só, os países onde cada fornecedor tratará os dados nem as garantias jurídicas aplicáveis.

Antes da publicação deverão ser identificados e documentados:

- os países ou regiões envolvidos;
- o fornecedor e serviço correspondente;
- o mecanismo jurídico aplicável;
- as garantias utilizadas para a transferência;
- a informação de privacidade disponibilizada pelo fornecedor.

**Estado:** `[POR DEFINIR — TRANSFERÊNCIAS E GARANTIAS]`

Não se assume que os dados permanecem no Espaço Económico Europeu enquanto as configurações e condições dos fornecedores não forem confirmadas.

## 9. Conservação

Os dados serão conservados apenas durante o período necessário para a alpha, para prestar as funcionalidades solicitadas e para cumprir obrigações aplicáveis.

As seguintes regras já estão definidas:

- os ficheiros originais de atividade não são conservados depois do processamento;
- apenas a interpretação mais recente do Training Coach é conservada para cada atividade;
- ao eliminar uma atividade, a interpretação do Training Coach associada também é removida;
- a retirada da autorização do Training Coach fica registada através da data de retirada;
- a retirada do consentimento de participação fica registada através da data de retirada.

Continuam por definir prazos ou critérios concretos para:

- contas e perfis ativos;
- contas inativas;
- atividades, rotas, planos e indicadores;
- consentimentos e respetivos registos históricos;
- convites utilizados, expirados ou revogados;
- metadados de utilização do Training Coach;
- registos operacionais, de segurança e de erros;
- backups e respetivas cópias;
- pedidos de suporte e de exercício de direitos.

**Estado:** `[POR DEFINIR — PRAZOS DE CONSERVAÇÃO]`

## 10. Decisões automatizadas

O PerformanceLab utiliza regras e cálculos automáticos para produzir indicadores, planos, recomendações e adaptações de treino.

O Training Coach utiliza inteligência artificial generativa para produzir interpretações quando solicitado pelo participante.

Estas funcionalidades:

- destinam-se a apoiar decisões de treino;
- não produzem decisões com efeitos jurídicos;
- não substituem avaliação humana;
- não constituem aconselhamento médico;
- podem conter erros, omissões ou interpretações inadequadas.

## 11. Direitos dos participantes

Nos termos aplicáveis, o participante pode solicitar:

- confirmação de que os seus dados são tratados;
- acesso aos seus dados;
- correção de dados inexatos ou incompletos;
- exportação dos dados associados à sua conta e ao seu atleta;
- eliminação da conta e dos dados associados;
- limitação do tratamento, quando aplicável;
- oposição ao tratamento, quando aplicável;
- portabilidade dos dados, quando aplicável;
- retirada dos consentimentos prestados;
- informação sobre fornecedores, destinatários e transferências.

A retirada de consentimento não afeta a licitude do tratamento realizado antes da retirada.

Até existir um mecanismo automático completo, os pedidos serão tratados através de um procedimento manual documentado.

Continuam por definir:

- Contacto para os pedidos: `[POR DEFINIR — EMAIL DE PRIVACIDADE]`
- Procedimento de verificação da identidade: `[POR DEFINIR — VERIFICAÇÃO DO PEDIDO]`
- Prazo operacional de resposta durante a alpha: `[POR DEFINIR — PRAZO DE RESPOSTA]`

O participante pode também apresentar reclamação à Comissão Nacional de Proteção de Dados:

- Website: https://www.cnpd.pt/
- Morada: Av. D. Carlos I, 134, 1.º, 1200-651 Lisboa

## 12. Retirada da participação

A participação na alpha é voluntária.

O participante poderá retirar o consentimento de participação e solicitar a eliminação da conta e dos dados associados através do processo que será definido antes do início dos testes externos.

A retirada da autorização do Training Coach é independente da retirada da participação na alpha e não impede a utilização das restantes funcionalidades.

A retirada da participação não significa que todas as cópias de backup sejam necessariamente eliminadas de forma imediata. A regra e o prazo aplicáveis aos backups ainda têm de ser definidos.

## 13. Segurança

O PerformanceLab prevê medidas técnicas e organizativas adequadas ao âmbito da alpha, incluindo:

- autenticação externa;
- convites individuais;
- autorização por utilizador e atleta;
- separação dos dados entre participantes;
- gestão de segredos fora do repositório;
- PostgreSQL obrigatório no ambiente alpha;
- backups;
- limites de upload e utilização;
- processamento temporário dos ficheiros importados;
- minimização dos dados enviados ao Gemini;
- registos operacionais sem prompts completos nem payload fisiológico;
- procedimentos de incidente, restauro e recuperação.

A configuração operacional destas medidas e os respetivos testes têm de estar concluídos antes do primeiro convite externo.

Nenhum sistema é completamente isento de risco. Incidentes relevantes serão tratados de acordo com as obrigações aplicáveis.

## 14. Alterações à política

A política possui uma versão identificável.

Quando uma alteração material exigir nova informação ou nova aceitação, o participante será informado antes de continuar a utilizar a aplicação.

O registo de aceitação da participação guarda:

- identificador do utilizador interno;
- versão do aviso;
- data e hora da aceitação;
- eventual data e hora da retirada.

A autorização do Training Coach é registada separadamente e possui a sua própria versão, data de concessão e eventual data de retirada.

## 15. Contacto

Para questões sobre privacidade ou exercício de direitos:

- Responsável: `[POR DEFINIR — RESPONSÁVEL PELO TRATAMENTO]`
- Email: `[POR DEFINIR — EMAIL DE PRIVACIDADE]`

## 16. Bloqueadores de publicação

Este documento não pode ser publicado enquanto não estiverem concluídos:

- [ ] identificação do responsável pelo tratamento;
- [ ] endereço de email de privacidade;
- [ ] fundamentos jurídicos por finalidade;
- [ ] fornecedor de alojamento;
- [ ] fornecedor PostgreSQL;
- [ ] regiões de tratamento e armazenamento;
- [ ] localização e retenção dos backups;
- [ ] transferências internacionais e garantias;
- [ ] prazos de conservação;
- [ ] processo de acesso, correção, exportação e eliminação;
- [ ] procedimento e prazo de resposta aos participantes;
- [ ] processo de incidentes;
- [ ] revisão jurídica final;
- [ ] confirmação de que todos os participantes têm pelo menos 18 anos.

## 17. Fontes de referência

- Regulamento Geral sobre a Proteção de Dados: https://eur-lex.europa.eu/eli/reg/2016/679/oj
- Direitos dos titulares — CNPD: https://www.cnpd.pt/cidadaos/direitos/
- Consentimento — CNPD: https://www.cnpd.pt/organizacoes/areas-tematicas/consentimento/
- Comissão Nacional de Proteção de Dados: https://www.cnpd.pt/