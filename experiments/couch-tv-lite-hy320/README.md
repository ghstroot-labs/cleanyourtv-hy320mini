# Couch TV Lite — HY320 Mini (experimento isolado)

Preparação experimental aprovada em 12/11/2026 para o projetor HY320 Mini (Android 13, API 33, armeabi-v7a, cerca de 2 GB de RAM, WebView 101).

## Objetivo
Gerar **somente** um APK Android de teste do launcher Couch TV, favorecendo a resposta do controle remoto em hardware limitado. Esta branch **não modifica** o projetor, não altera a branch `main` e não substitui o CleanYourTV nem o Couch TV oficial.

## Origem e licença
- Projeto de origem: https://github.com/Seagey/couch-tv (MIT).
- Commit fixado: `e8efc55965d7f029f898538d7029758a4281a00b`.
- Código-fonte da origem é obtido durante o GitHub Actions. Esta branch armazena apenas a receita da compilação, sem copiar o projeto inteiro.

## Alterações do APK experimental
1. `home.lighter=true`: reduz efeitos de blur, sombra, movimento e tamanho de imagens conforme implementação original.
2. `home.glass=off`, `home.moving_tiles=false`, `home.hi_res=false`.
3. Uma cena estática (`night`) e nenhuma animação de vídeo.
4. `applicationId=studio.ghstroot.couchtvlite.hy320`, diferente do app oficial `app.couchtv.launcher`, para teste **lado a lado**.
5. Nome visível `Couch TV Lite - HY320`, atualização automática do repositório oficial desabilitada para a compilação personalizada.

A versão inicial contém configurações demonstrativas da origem; não copia dados nem preferências do Couch TV já instalado.

## Execução na nuvem
Apenas um push da receita na branch `experiment/couch-tv-lite-hy320` inicia o workflow `.github/workflows/couch-tv-lite-hy320.yml`, que prepara o SDK Android e o JDK 21, compila só o módulo `tv-home/android/app`, valida o identificador e os ajustes no APK e publica o arquivo como artefato de teste.

**Assinatura:** a compilação usa a chave de teste gerada pelo runner. Não serve para atualizar o APK oficial e novas compilações podem exigir reinstalação da versão experimental. Não é um APK de produção.

**Restrições de segurança:** nenhum ADB ou conexão com o HY320, nenhuma instalação/remoção, nenhuma seleção de launcher e nenhuma ação sobre a `main`. A instalação e o teste real dependerão de aprovação separada.

## Critérios de aceitação
- Workflow verde e artefato `couch-tv-lite-hy320.apk` validado.
- Identificador distinto e conteúdo `home.lighter=true` comprovados.
- Depois de autorização: instalação isolada, teste de navegação e comparação contra Couch TV 0.12 com os mesmos ícones.
- Se não houver ganho real, desfazer somente a instalação da versão experimental.

**Nota:** otimizações gráficas são uma hipótese, não uma garantia de melhoria. O WebView 101 e o hardware podem continuar limitando a fluidez.
