# Couch TV Slim Night BR sem saudação — HY320 Mini (experimento isolado)

Preparação experimental para o projetor HY320 Mini (Android 13, API 33, armeabi-v7a, cerca de 2 GB de RAM e WebView 101).

## Objetivo

Gerar um APK Android de teste do launcher Couch TV, mantendo a receita isolada nesta branch. Ela não modifica o projetor, não altera a branch `main` e não substitui o CleanYourTV nem o Couch TV oficial.

## Origem e licença

- Projeto de origem: https://github.com/Seagey/couch-tv (MIT).
- Commit fixado: `e8efc55965d7f029f898538d7029758a4281a00b`.
- O código-fonte de origem é obtido durante o GitHub Actions. Esta branch armazena apenas a receita da compilação, sem copiar o projeto inteiro.

## Alterações do APK experimental

1. Mantém o modo leve: `home.lighter=true`, vidro e movimento desativados, sem vídeo de fundo e com uma única paisagem estática.
2. Remove o seletor circular de perfis e a seção **Pessoas** das configurações. A lógica interna compartilhada é preservada para não quebrar a seção Continuar assistindo.
3. Transforma os cartões **Wi-Fi** e **Entradas** em pílulas com bordas totalmente arredondadas, mantendo os ícones, textos e estados existentes.
4. Fixa a meteorologia no centro municipal de Palhoça, SC (latitude `-27.64500046`, longitude `-48.66799927`), fuso `America/Sao_Paulo`. Usa Open-Meteo, valida a resposta, evita cache HTTP local e consulta novamente a cada 15 minutos por padrão.
5. Adia a primeira consulta meteorológica por 1,2 segundo para permitir que a tela inicial seja desenhada antes da atividade de rede. Desativa também a consulta recorrente de troca de perfil, pois os perfis foram removidos.
6. Corrige textos visíveis em português brasileiro e define corretamente o idioma do documento como `pt-BR`.
7. Mantém o identificador separado `studio.ghstroot.couchtvslimnogreeting.hy320.test`, diferente do app oficial `app.couchtv.launcher`, para instalação lado a lado.

A meteorologia usa a coordenada municipal, não a posição exata do imóvel. A precisão local continua limitada à resolução e à atualização dos modelos meteorológicos.

## Inicialização segura

O APK continua usando a atividade Android declarada como tela inicial (HOME). Esta receita não adiciona outro receiver para forçar a abertura do launcher, não cria serviço em segundo plano e não altera permissões de sistema, acessibilidade, energia ou a tela inicial de fábrica. A otimização é conservadora: primeiro desenha a interface e só depois inicia a consulta do clima. Não promete alterar o tempo de inicialização do Android ou eliminar limitações do hardware.

## Execução na nuvem

Um push na branch `experiment/couch-tv-lite-hy320` inicia `.github/workflows/couch-tv-lite-hy320.yml`. O workflow prepara o SDK Android e o JDK 21, obtém a versão fixa do Couch TV, aplica os ajustes, compila somente `tv-home/android/app`, valida o identificador e as alterações e publica o artefato `couch-tv-slim-night-br-sem-saudacao`.

**Assinatura:** a compilação usa a chave de teste do runner. Não serve para atualizar o APK oficial e novas compilações podem exigir reinstalação da versão experimental. Não é um APK de produção. O identificador `.test` permite instalá-lo ao lado do pacote experimental anterior, sem substituir nem apagar os dados dele.

**Restrições:** nenhum ADB ou conexão com o HY320 durante a compilação, nenhuma instalação ou remoção, nenhuma seleção de launcher e nenhuma ação sobre a branch `main`. A instalação e o teste real continuam separados.

## Critérios de aceitação

- Workflow verde e artefato de teste validado.
- Identificador do pacote e configurações do APK conferidos.
- Verificação da remoção do seletor de perfis, das pílulas e da localização meteorológica de Palhoça.
- Só depois da validação do APK: instalação isolada e conferência visual no projetor, preservando o launcher atual como alternativa.

As otimizações visuais podem melhorar a resposta em hardware limitado, mas o resultado deve ser confirmado no próprio HY320.
