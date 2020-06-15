# Stay Safe: Viaje com segurança, nós te ajudamos!

Projeto desenvolvido para o Hackathon CCR 2020 Shawee http://www.grupoccr.com.br/hackathonccr/.

O Stay Safe é um app que busca solucionar dois principais problemas encontrados no dia a dia de um caminhoneiro: o cansaço das viagens e o mapeamento de lugares para descanso. Dessa forma nosso aplicativo utiliza Facial Landmarks para detectar pontos de interesse do olho e assim estipular quando o usuário está sonolento, emitindo assim um alarme sonoro que o acordará e oferecerá os pontos de parada mais próximos. Adicionalmente os dados coletados (não o vídeo, dado a LGPD)  como localização mais comum de ocorrências, horário mais comuns, principais locais de descanso, etc, servirão de base para um Dashboard onde a CCR poderá usufruir para determinar a melhor abordagem de melhoria para cada caso.

Todo o app tem como base a linguagem python sendo o reconhecimento facial feito usando open-cv e landmarks da DLib. A interface visual foi feita utilizando o framework kivy e a localização de locais de parada com a API do google maps para python. O dashboard foi feito utilizando Power BI.

## Deliveries

Na pasta "deliveries" consta um vídeo do funcionamento do MVP que criamos em tempo de hackathon e o pdf explicativo da solução.

Para assistir ao Pitch Comercial, acesse o seguinte link: https://www.youtube.com/watch?v=O934DP1VZzk&rel=0

## Requisitos

Para as consultas na API do Google Maps, é necessário obter uma chave de acesso: 
- Acesse https://cloud.google.com/maps-platform?hl=pt-br para adquirir uma chave de acesso
- Selecione todos produtos disponíveis na API (Maps, Routes e Places)
- Após o cadastramento, crie dentro da pasta o arquivo <code>api_key.txt</code> somente com a chave de acesso

Essencialmente o que foi usado foi o Dlib, open-cv, googlemaps e o kivy, podendo ser instalados via Anaconda:

<code> conda install -c conda-forge opencv </code>

<code> conda install -c conda-forge dlib </code>

<code> conda install -c conda-forge kivy </code>

 <code> conda install -c conda-forge googlemaps </code>
 
 Também consta aqui o arquivo <code>environment.yaml</code> que já cria o env com as libs, para usar use o comando:
 
 <code> conda env create -f environment.yaml </code>
 
 <code> conda activate staysafer </code>
 
 Após instalado as dependências e ativado o env é só rodar o arquivo <code>StaySafeApp.py</code>:
 
 <code> python StaySafeApp.py</code>
 
 ## References
 
- [Apresentação Hackathon CCR - Live 09-06-2020:](https://docs.google.com/presentation/d/1Tq6isbnxlFaBfsNL5GHMRTTs1ilzb15JlrfnPtUhBFw/edit#slide=id.p5)
- [CNT Acidentes Rodoviários](https://cdn.cnt.org.br/diretorioVirtualPrd/34e78e55-5b3e-4355-9ebc-acf1b8e7b4a4.pdf)
- [Mais de 16% dos caminhoneiros dirigem no limite de sonolência](https://g1.globo.com/sp/sao-paulo/noticia/2019/05/31/mais-de-16percent-dos-caminhoneiros-dirigem-no-limite-de-sonolencia-diz-pesquisa.ghtml)
- [Falta de sono já causou algum tipo de acidente para 23% dos caminhoneiros](http://g1.globo.com/bom-dia-brasil/noticia/2015/09/falta-de-sono-ja-causou-algum-tipo-de-acidente-para-23-dos-caminhoneiros.html)
- [Saúde: Estudo inédito revela que é maior o risco de acidentes envolvendo caminhoneiros](https://www.saopaulo.sp.gov.br/eventos/saude-estudo-inedito-revela-que-e-maior-o-risco-de-acidentes-envolvendo-caminhoneiros/)
- [Detecção de piscar de olhos com python](https://www.pyimagesearch.com/2017/04/24/eye-blink-detection-opencv-python-dlib/)
- [Detecção de sonolência usando EAR e ECR](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3356401)
- [Tutorial Kivy para desenvolvimento de interface gráfica em python](https://www.youtube.com/watch?v=WiyF3VsL5dY&list=PLsMpSZTgkF5AV1FmALMgW8W-TvrfR3nrs)
