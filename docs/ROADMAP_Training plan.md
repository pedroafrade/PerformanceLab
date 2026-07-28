1 - Janela móvel de 7 dias (sem alterar a lógica do plano).
2 - Setas de navegação e estado em session_state.
3 - Plano persistente associado a uma prova, substituindo a geração "por semana" por um plano completo que depois é apenas "recortado" para apresentação.
4 - Revisão do algoritmo de prescrição (distribuição de intensidade, dias de recuperação, duração mínima, progressão e taper).


Passo 1 — Corrigir o ciclo de vida do plano

Confirmar que o plano:
está associado a uma prova;
tem identidade própria;
é persistido;
não é regenerado por mudança de semana;
só é regenerado por uma ação explícita ou alteração relevante.

Passo 2 — Transformar o Weekly Plan numa janela móvel

Implementar:
hoje no centro;
três dias anteriores;
três dias seguintes;
setas esquerda e direita;
estado da janela em session_state.

Passo 3 — Corrigir as regras de prescrição

Começaria por regras pequenas e testáveis:
nunca gerar duas sessões intensas consecutivas;
permitir dias de descanso em qualquer dia da semana;
diferenciar Recovery, Easy, Endurance e Long;
remover o mínimo universal de 50 minutos;
limitar dias consecutivos;
controlar volume semanal e progressão.

Passo 4 — Só depois melhorar periodização

Depois podemos tratar:
fases do plano;
semanas de descarga;
taper;
especificidade para cada prova.