# 1. Especifica a imagem base como Alpine Linux versão 3.19
FROM alpine:3.19

# 2. Instala Python 3 e cria um link simbólico para o executável 'python'
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python

# 3. Instala o navegador Chromium e o Chromedriver para automação com Selenium
RUN apk add --no-cache chromium chromium-chromedriver unzip

# 4. Instala o gerenciador de pacotes pip
RUN apk add --update --no-cache py3-pip

# 5. Define o diretório de trabalho dentro do container
WORKDIR /usr/src/app

# 6. Copia os arquivos da pasta 'src' (código do projeto) para dentro do container
COPY src .

# 7. Instala as dependências Python listadas no arquivo 'requirements.txt'
RUN pip install --no-cache-dir -r ./requirements.txt --break-system-packages

# 8. Define variáveis de ambiente padrão
ENV GRASS_USER=lui_zzzz@hotmail.com
ENV GRASS_PASS=Burro12@
ENV ALLOW_DEBUG=False

# 9. Define o comando de inicialização do container, que é a execução do arquivo main.py
CMD [ "python", "./main.py" ]

# 10. Expõe a porta 80, usada pelo servidor que será executado
EXPOSE 80
