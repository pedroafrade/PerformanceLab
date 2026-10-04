# Apresentação móvel e adaptação dos templates Base

Referência anterior ao patch: `4559c4497d98511138496d2e10c5a2b9d746f83a`.

## Limites da alteração

As novas regras de apresentação usam `max-width: 700px`. A ordem de renderização,
as proporções das colunas e as prescrições antigas continuam a ser as mesmas.
Guide/Guia é o novo rótulo e título em todos os dispositivos; a chave de navegação
mantém-se estável. Activities, Calendar e Settings não são reformulados.

No Dashboard, a ordem móvel é Training Load & Recovery, Next Workout, Daily Brief,
Weekly Plan, Latest Activity, Upcoming Events e Activities Summary. Em Today,
a ordem é Daily Brief, Next Session (ou a atividade concluída, conforme o estado
atual), Session equivalent, Recovery Metrics, Recovery Log e restantes métricas.
A análise detalhada de uma atividade concluída fica depois destes cartões.

Em Development, os gráficos Load and form e Daily training load e as métricas
de recuperação aparecem antes das estatísticas comparativas e de Volume by sport.
As janelas de cálculo e a vista móvel existente dos últimos 60 dias são preservadas.

Os cartões do Dashboard deixam de ter alturas fixas nos ecrãs estreitos.
Os sete dias do Weekly Plan e as fases permitem deslocação horizontal, mantendo
as datas, a seleção do dia e os controlos de navegação. Os gráficos móveis do Plan
mantêm o horizonte completo, com maior altura e texto e deslocação horizontal.
As especificações dos gráficos de PC não são modificadas. A barra lateral recolhe
após um clique numa página ou no botão Journal home, apenas abaixo do breakpoint.

## Adaptação localizada

Continuous Tempo conserva o bloco contínuo e o RPE; Threshold Cruise Intervals
conserva as repetições near LT2 e a recuperação de 60–90 segundos; Aerobic Hill
Repeats conserva o esforço aeróbico e a recuperação de 90 segundos downhill;
Easy + Strides conserva as acelerações relaxadas de 20 segundos e recuperação
completa de 70–100 segundos. Não são convertidos em sessões genéricas de LT2
ou em repetições rápidas de 30 segundos.

A duração é orçamentada em segundos, usando o limite superior das recuperações.
Quando necessário, reduz-se o trabalho sem aumentar a intensidade ou a dose
original. As adaptações sucessivas reconhecem as prescrições já adaptadas.
Instruções personalizadas nos quatro novos templates excluem essas sessões da
substituição automática de duração/estrutura; continuam guardadas como editadas.
Os outros templates conservam o comportamento anterior. Não se alteram os limites
de carga, as regras de recuperação, a periodização ou as proteções de provas,
taper, regeneração, passado e fim do bloco.

## Cloud Run

O responsável confirmou que o carregamento no iPhone e iPad passou a funcionar
após aumentar a concorrência de 2 para 20. Os logs anteriores registavam respostas
429 em módulos JS/CSS. O Terraform passa a guardar 20, mantendo o máximo de duas
instâncias e a afinidade de sessão. Este patch não executa deployment nem modifica
o serviço ativo. A concorrência não substitui a monitorização de memória e erros.

## Validação e aceitação

Testes automatizados verificam os casos dos quatro templates, adaptações
sucessivas, edições do utilizador, proteções existentes, ordens móveis,
renderização real em Streamlit e igualdade dos dados/especificações dos gráficos
PC. A validação visual em Safari/iPhone e a comparação visual com PC estão
pendentes; o navegador local de teste não conseguiu arrancar neste ambiente.

Depois de publicar a nova imagem, verificar:

- PC: mesmas duas filas e proporções do Dashboard; mesma organização em Today e
  Development; mesmos gráficos no Plan. Só o nome Guide/Guia muda deliberadamente.
- iPhone: ordem dos cartões, texto legível, alturas ajustadas ao conteúdo e ausência
  de deslocação horizontal da página inteira.
- Weekly Plan: deslizar os dias, selecionar um dia e usar ambas as setas.
- Plan: deslizar os gráficos completos e consultar as datas e os tooltips.
- Today: verificar os estados com sessão seguinte, atividade concluída e sem plano;
  guardar/editar um registo de recuperação e confirmar persistência.
- Sidebar: abrir, escolher uma página e confirmar recolha no iPhone; em PC deve
  continuar aberta após a mesma operação.
- iPad: repetir refresh e confirmar carregamento consistente; consultar logs de
  módulos estáticos se reaparecer uma página branca.

É necessária uma nova imagem/deployment para atualizar a alpha online. Um refresh
no browser não publica alterações Python. Usar o processo de publicação existente.
