# Implantação e Configuração do Dashboard Next.js para Chatwoot com Docker e Portainer

A aula detalha a instalação e o deploy de um aplicativo de dashboard avançado, construído com Next.js e Tailwind CSS, para o Chatwoot. Esta solução de frontend unifica e visualiza todas as conversas de um contato do Chatwoot em uma única linha do tempo cronológica, oferecendo funcionalidades de busca e exportação. O projeto é robusto, escalável e projetado para fácil customização, aproveitando o cache do Next.js e consumindo diretamente a API do Chatwoot sem interação com banco de dados. A sessão abrange desde a configuração local e a construção de imagens Docker até o deploy em produção utilizando Portainer e Cloudflare para gerenciamento de DNS, além de abordar a configuração de variáveis de ambiente e tokens de acesso.

## 📚 Pontos-Chave

• **Instalação e deploy de um dashboard Next.js para Chatwoot, unificando e visualizando conversas em uma timeline cronológica.**
• **Utilização de Docker para empacotamento e Portainer para orquestração e gerenciamento do deploy da aplicação.**
• **Configuração de variáveis de ambiente essenciais (URL do Chatwoot, token de administrador) e apontamento de domínio via Cloudflare (registro CNAME).**
• **O projeto é otimizado para baixo consumo de recursos, escalável e robusto, consumindo diretamente a API do Chatwoot.**
• **Demonstração prática da integração do dashboard com o Chatwoot, incluindo funcionalidades como exportação e responsividade.**

## 🛠️ Tecnologias Mencionadas

• **Next.js**
• **Tailwind CSS**
• **Docker**
• **Portainer**
• **Cloudflare**
• **Chatwoot**
• **Yarn**

## 💻 Comandos Utilizados

```bash
yarn build
yarn dev
docker build
docker login
Configuração de variáveis de ambiente (CHATWOOT_URL, CHATWOOT_ADMIN_TOKEN)
Criação de registro DNS CNAME no Cloudflare
Configuração de Docker Compose (Docker Swarm stack) no Portainer
```


## 💡 Conceitos Importantes

**Next.js**: Framework React para construção de aplicações web com renderização do lado do servidor (SSR) e geração de sites estáticos (SSG), otimizado para performance e escalabilidade.

**Tailwind CSS**: Framework CSS utilitário que permite construir designs personalizados rapidamente, compondo classes de baixo nível diretamente no HTML.

**Docker**: Plataforma para desenvolver, enviar e executar aplicações em contêineres, que são pacotes leves e portáteis de software.

**Portainer**: Ferramenta de gerenciamento de código aberto para Docker e Kubernetes, que simplifica a implantação e o gerenciamento de contêineres através de uma interface gráfica.

**Chatwoot API**: Interface de programação de aplicações do Chatwoot, utilizada pelo dashboard para consumir dados de conversas diretamente, sem acesso ao banco de dados.

**Docker Swarm**: Ferramenta de orquestração nativa do Docker para gerenciar um cluster de máquinas Docker como um único sistema virtual, permitindo deploy e escalabilidade de serviços.

**CNAME Record (DNS)**: Tipo de registro DNS que mapeia um nome de domínio (alias) para outro nome de domínio canônico, usado para apontar subdomínios para outros serviços.

**Variáveis de Ambiente**: Valores dinâmicos que afetam o comportamento dos processos em execução em um ambiente, usados para configurar aplicações sem modificar o código-fonte.



## 📋 Pré-requisitos

• Conhecimento básico de desenvolvimento web (HTML, CSS, JavaScript)
• Familiaridade com Next.js e React
• Noções de linha de comando (terminal)
• Conhecimento básico de Docker e contêineres
• Entendimento de conceitos de DNS e gerenciamento de domínios
• Conta e familiaridade com Chatwoot


## 🎯 Objetivos de Aprendizado

• Instalar e configurar o dashboard Next.js para Chatwoot localmente.
• Realizar o build de imagens Docker para diferentes arquiteturas (AMD/ARM).
• Implantar o dashboard em ambiente de produção utilizando Portainer e Docker Swarm.
• Configurar o DNS via Cloudflare para o acesso ao dashboard.
• Integrar o dashboard com a API do Chatwoot utilizando um token de administrador.
• Compreender a arquitetura e os recursos de escalabilidade do projeto.

## ⏱️ Duração
20-25 minutos

## 📊 Informações Técnicas
- **Nível de Dificuldade**: Intermediário
- **Palavras Transcritas**: 2,213
- **Segmentos de Áudio**: 238
- **Duração Real**: 20.6 minutos

## 🏷️ Tags
`Chatwoot`, `Dashboard`, `Next.js`, `Docker`, `Portainer`, `Cloudflare`, `Frontend`, `Deploy`, `Web Development`, `API Integration`, `Containerization`, `DevOps`

<details>
<summary>📝 Transcrição Completa</summary>

Olá pessoal tudo bem vamos lá eu vou apresentar aqui para vocês como vocês vão instalar o app de dashboard do chat útil tá e também vou dar algumas dicas para que vocês possam aí evoluir esse projeto para outras coisas né criar novas páginas e etc então é uma solução avançada que completa para você visualizar e analisar e até exportar as conversas do chat útil então você uma timeline unificada com a cronologia, conforme as mensagens foram criadas dentro do chat-out. O chat-out tem uma peculiaridade que é criar várias conversas e elas ficam atreladas a esse contato. Então, eu criei essa possibilidade de você unificar todas essas conversas e trazer ali todo o histórico em uma forma cronológica e unificada, onde você consegue exportar, você consegue ter ali todas essas informações e fazer uma busca também dentro dessas conversas. Então, é uma plataforma de front-end, onde ela usa a tecnologia de Next.js com o teu Indy e você pode estar fazendo suas customizações e evoluindo esse projeto. É um projeto robusto, escalável, ele usa até o próprio cache do Next. Então, é um projeto que está bem desenhado, bem arquitetado para que você possa evoluir ele. E assim você construir sua aplicação de forma mais eficiente. Então, aqui tem uma documentação simples para você subir o seu deploy. Você pode subir lá no Docker, você pode ter sua imagem customizada. E eu vou apresentar aqui agora um pouquinho dele, beleza? Então, vamos lá, direto aqui no Docker, vocês podem ver que vocês podem subir a imagem tanto como AMD quanto ARM, tá? Então, eu vou apresentar aqui o repositório local, beleza? Então, no deploy, ele já está pronto para você fazer o build da imagem como padrão para essas OS. Então, tem todos aqui os comandos, como você vai subir, como você vai fazer o deploy da máquina. Tem toda a instrução necessária, as variáveis de ambiente que você vai fazer aqui o deploy da máquina, né? Tem toda aqui a instrução necessária, as variáveis de ambiente que você vai usar, tá bom? Ele também roda localmente, beleza? Então, se eu der um comando aqui para rodar local, vocês vão ver que ele vai rodar local, tá? Então, eu vou aqui, arn build, né? Para buildar o projeto, mas ele já está buildado, só para exemplificar para vocês, beleza? ou poderia ser deve também tá tá ele fica um pouco mais rápido então eu vou acessar aqui para vocês verem e ele aqui não vai aparecer nada né um esqueleto aqui para só exemplificar né mas a por exemplo ele vai rodar dentro do seu chat útil tá de forma otimizada forma escalável consumindo ali a pele do chat útil e dentro desse processo aqui ele não consome o banco de dados ele consome diretamente a api tá então a gente vai fazer instalação aqui agora beleza eu vou ensinar vocês a instalar a fazer o deploy usar aqui de forma eficiente a plataforma beleza então vamos Primeiro ponto, beleza? É vocês darem um comando de instalação, né? Assim que vocês baixarem lá o repositório, vocês vão dar um comando de instalação, né? Então, primeiro ponto é vocês virem aqui, né? E vocês vão ter aqui todos os comandos necessários, beleza? Então, exemplo, se você for rodar local, né? Você vai puxar aqui, vai instalar o Arne e configurar o Envy, beleza? beleza colocar as credenciais aqui a sua URL do chat o seu Tolkien do administrador tem um ponto aqui muito importante que o usuário ele precisa ser o usuário administrador de cada conta tá então ideal é você criar um usuário administrador que ele possa acessar todas as contas do seu chat útil então toda vez que você criar uma conta uma caute dentro do chat útil você adiciona esse usuário que vai ser usuário padrão né que ele vai gerar ali um token e você vai consumir esse token diretamente aqui então todo usuário que você criar vai ser o mesmo token é toda empresa né toda conta que você criar vai ser o mesmo token tá E aí você pode adicionar aqui beleza então feito isso você pode iniciar em modo deve para você visualizar ali dentro do seu chat você pode fazer um build ou e depois de estar tá né rodar aqui no docker localmente você pode rodar o docker local ou em produção né você pode rodar em produção também eu vou mostrar para vocês como vai subir do seu próprio portainer ali, tá? Então, vamos lá, pessoal. Vou adiantar aqui, beleza? Se você quer subir a sua imagem, você tem os comandos certos aqui, para você rodar aqui o seu build. Então, exemplo, tá? Você vai dar um docker build. Aqui, eu estou usando esse comando, por quê? Porque eu estou buildando para as duas OS, tá? Então, vocês vão ver que eu posso rodar aqui esse comando para ele rodar tanto no ARM quanto no AMD, beleza? Então, eu vou subir aqui a AMD, tá? E esse comando vai fazer o build, beleza? Eu vou mostrar aqui para vocês que vocês precisam ter esse container aqui já pré-definido, pré-instalado, tá? Para ele fazer os builds. Eu vou deixar os comandos também para vocês instalarem ele, o meu já está instalado. e eu não vou dar o comando aqui porque vai demorar demais, vai travar aqui o PC, ele demora um pouco então não vou dar esse comando mas a princípio vocês dariam esse comando aqui e ele faria o build e já subiria ali para o para o docker de vocês o docker hub, vocês vão fazer o docker login antes para acessar ali o docker de vocês beleza? mas aqui aqui eu não preciso tá beleza pessoal vamos lá avançando depois que vocês fizerem aqui o deploy subir a imagem de vocês aí tá vocês também podem usar a minha imagem não tem problema tá a minha imagem vai estar disponível aqui também beleza ela tá pública tá vocês podem usar minha imagem aqui Beleza? Então vamos avançar aqui, deixa eu dar uma atualizada aqui. Pronto. Beleza. Então vamos fazer a instalação aqui direto já no Portainer. Então primeiro ponto, vocês precisam ter um domínio, né? Então, eu vou lá no Cloudflare, vou subir esse domínio. Eu vou subir um domínio para poder colocar essa aplicação, esse app, dentro do Chatute. Deixa eu sair dessa conta. Então vamos lá. Vou acessar aqui. Eu vou fazer um exemplo direto na minha conta. Acessar minha conta aqui diretamente. Eu vou fazer lá o apontamento para o domínio. Beleza? Então, acessando aqui agora, eu vou escolher um domínio. Então, eu vou pegar aqui o setup automatizado. E aí, eu pego o meu domínio, beleza? Vou criar um registro aqui. E vou apontar para o domínio do servidor, beleza? Então, eu já tenho o servidor aqui com portene. Eu vou verificar o DNS, que eu preciso fazer o apontamento. É do tipo CNAME mesmo? Poderia pegar do tipo A aqui, que ele viria o IP, tá? Mas eu vou pegar do tipo CNAME. E eu vou colocar aqui, sem status de proxy, do tipo C. name e vou colocar aqui app.chatoot, beleza? app.chatoot, posso colocar qualquer domínio ali que eu quiser, tá? Só um exemplo, então criei aqui, beleza? Então é o meu domínio mais o app.chatoot, vou lá no portainer, crio um novo stack, beleza? E aqui eu vou colar o nosso o nosso docker suarme aqui, beleza? Deixa eu só alterar aqui é deixa eu alterar aqui só um instante eu não vou conseguir alterar aqui, depois eu vou mudar a senha, tá? Então eu vou acessar aqui, vou copiar esse compose, vou alterar a senha ali, beleza? Então eu tenho aqui já a role configurada, ok? Os apontamentos aqui eu vou colocar no meu domínio. E aqui eu vou botar app.chat.ult. Beleza? Feito isso aqui Eu vou criar o nome do Serviço Ok? Essa senha aqui eu vou alterar já Porque eu vou criar uma nova senha E aí eu tenho a minha imagem aqui que já está pronta, né? Eu vou apontar lá para o domínio do chatute Beleza? Então eu vou pegar aqui, ó No chatute eu vou pegar o domínio ok esse é o usuário administrador como eu tinha falado, eu preciso ter um usuário que ele esteja em todas as contas, né? Então, esse usuário está em todas as contas. Eu vou lá no perfil desse usuário e copio a senha também, tá? A senha aqui do token. E aí, eu volto lá no Portainer. Adiciono esse token. Adiciono aqui a URL do Shotshoot. Tirar essa barrinha aqui. Eu não quero ter os logs aqui de debug, beleza? Eu já tenho todas as informações aqui já pré-requisitos, né? Você pode botar uma réplica também, né? Deixei duas aqui, não tem problema, ele pode replicar. Então, está tudo bem configurado aqui para você poder utilizar, tá? Então, eu só vou fazer aqui o deploy. E aí, se eu observar aqui... Opa! Tem um probleminha aqui. Deixa eu pegar do outro que eu tinha acabado de fazer. O outro vai estar certinho. Deixa eu pegar aqui. E aí eu já atualizo. Lá dentro do stack. Deixa eu atualizar aqui. Pronto. Ok. Deixa eu pegar, eu preciso pegar esses pontos aqui de ajuste. Só isso. Lembrando que essa senha vai ser alterada, então sem prejuízo. é só alterar aqui ó e essas lêem dos aqui suas informações pronto aqui ele vai estar no eu vou colocar é o rolê a roça name é porque ele vai rodar no orque tá deixou só verificar se essa máquina, ah, essa máquina ela não tem aqui outras máquinas, ela é um manager mesmo. Então se você for rodar aí em outras máquinas, você adicione aí o role da sua máquina, tá? Então, aqui vai rodar no manager. Beleza? Vou botar aqui só 2 GB, 1 CPU. Pode rodar bem pouco, tá? Mas vou botar 2 réplicas. Poderia até ser menor aqui, tá? Não tem problema. Poderia botar 1 GB, 1 CPU ou até menos. Ele vai rodar muito bem. Então, feito isso, ó. Deploy já prontinho, ó. Bem rápido, fácil pra você subir aí na sua máquina. Então, vou dar um Deploy aqui E aí ele já está preparando Deixa eu só dar uma limpeza aqui para ficar bonitinho E aí eu faço o redeploy aqui Pronto E eu quero o domínio, tá? Então eu vou pegar o domínio aqui Pronto Já está startando Se eu observar aqui, ele já subiu, tá? E aí eu vou acessar aqui a URL para vocês verem. Ele ainda está preparando ali a certificação SSL, mas vocês já veem que ele já está disponível ali. Vou lá no chatute. Basicamente, eu venho em configurações na conta que eu quero configurar. Vocês podem configurar em todas as contas. Lembrando que é necessário que o usuário, o usuário administrador, seja o mesmo em todas as contas para que você não precise ali ter que criar várias... Opa, não é aqui. Não, é aqui mesmo. Então, vocês não vão precisar criar várias contas para acessar ali o chat útil, tá? Então, app. Timing. Line. Eu não vou adicionar barra lateral. Se o seu tivesse opção, eu acho que é desnecessário. Conversas. Então, eu vou pegar uma conversa aqui. Eu vou pegar uma conversa minha mesmo. Então, vou pegar aqui. Deixa eu ver se eu tenho histórico. Pior que eu não tenho histórico de conversa. Deixa eu mandar uma mensagem aqui. Pronto, mandei uma mensagem para mim mesmo Oi e aí eu venho na timeline e pronto timeline já tá pronto aqui vou abrir e tá aí pessoal tá instalado rápido prático beleza e aí eu posso mudar aqui o tema e ele acompanha tá E aí eu já algumas conversas aqui provavelmente a foto do usuário tá quebrada né porque não tem aqui beleza a foto do agente né E aí tá implementado aqui se eu colocar ele já achou aqui ó Beleza pessoal? Então bem tranquilo, bem de boa utilizar aqui tá? Exportação, para você exportar aqui as conversas, bem legal, otimizado, responsivo, então ele tem responsividade, você consegue utilizar aí de forma eficiente o app beleza então se eu pegar outra conversa aqui ó eu vou pegar essa daqui ele tem a timeline só eu só não tem foto você vê toda toda conversa aqui tá Esse aqui é um tipo de conteúdo que não abriu, mas todo tipo de conteúdo ele abre, áudio, vídeo, imagem. Deixa eu ver se tem alguma outra aqui. Esse aqui era uma imagem, era para ele abrir ali. Mas vamos voltar aqui. E pegar outra conversa. Beleza, esse aqui não tem. Acho que vai ser difícil ter alguma outra conversa aqui aberta. Deixa eu criar outra aqui. O meu mesmo contato. Vou enviar aqui. Então ele já criou duas E aí sim, ele me traz aqui as duas conversas. Beleza? É isso, pessoal. E muito fácil de instalar aí, né? De você ter a sua aplicação rodando. Beleza? De forma eficiente e bem prática. Pode ver que ele vai consumir bem pouco recurso. Então, deixa eu dar uma olhada aqui. Consome bem pouco. Quase nada. beleza e tá aí rodando para vocês

</details>
