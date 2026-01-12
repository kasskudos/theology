// ==UserScript==
// @name         Add Indexar Button
// @namespace    http://tampermonkey.net/
// @version      1.7
// @description  Adiciona o botão "Indexar" que copia e formata o conteúdo de um texto específico, incluindo título e URL formatada
// @author       Você
// @match        https://www.bible.com/pt/bible/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=bible.com
// @grant        none
// ==/UserScript==

(function () {
    'use strict';

    // Função para encontrar elementos usando XPath
    function getElementByXPath(xpath) {
        return document.evaluate(
            xpath,
            document,
            null,
            XPathResult.FIRST_ORDERED_NODE_TYPE,
            null
        ).singleNodeValue;
    }

    // Função para remover parâmetros após o "?" de uma URL
    function cleanURL(url) {
        if (!url) return '';
        return url.split('?')[0]; // Remove tudo após o "?"
    }

    // Espera o DOM ser carregado completamente
    window.addEventListener('load', () => {
        // Seleciona a div-alvo onde o botão será inserido
        const targetDiv = document.querySelector('.flex.justify-between.items-center.mbe-1');

        if (targetDiv) {
            // Seleciona o botão existente e o clona
            const existingButton = targetDiv.querySelector('button');

            if (existingButton) {
                // Clona o botão existente
                const indexButton = existingButton.cloneNode(true);

                // Modifica o texto do botão para "Indexar"
                const buttonText = indexButton.querySelector('div.h-fill');
                if (buttonText) {
                    buttonText.textContent = 'Indexar';
                }

                // Adiciona funcionalidade no clique do botão
                indexButton.addEventListener('click', () => {
                    // XPath dos elementos
                    const textXPath = '/html/body/div/div[2]/main/div[1]/div/div/div[1]/div[1]/a/p';
                    const titleXPath = '/html/body/div/div[2]/main/div[1]/div/div/div[1]/div[1]/div[1]/h2';
                    const linkXPath = '/html/body/div/div[2]/main/div[1]/div/div/div[1]/div[1]/a';

                    // Localiza o elemento que contém o texto
                    const textElement = getElementByXPath(textXPath);
                    // Localiza o elemento que contém o título
                    const titleElement = getElementByXPath(titleXPath);
                    // Localiza o elemento que contém o link
                    const linkElement = getElementByXPath(linkXPath);

                    if (textElement && titleElement && linkElement) {
                        // Pega os conteúdos necessários
                        const originalText = textElement.textContent; // Texto principal
                        const titleText = titleElement.textContent; // Título a ser inserido nos colchetes
                        const url = cleanURL(linkElement.href); // URL antes do "?"

                        // Formata o texto no padrão solicitado
                        const formattedText = `>"*${originalText}*" [${titleText}](${url})`;

                        // Copia a formatação para a área de transferência
                        navigator.clipboard.writeText(formattedText)
                            .catch(err => {
                                console.error('Erro ao copiar texto: ', err);
                                alert('Não foi possível copiar o texto formatado.');
                            });
                    } else {
                        console.warn('Um ou mais elementos necessários não foram encontrados!');
                        alert('Não foi possível localizar todos os elementos necessários para formatação.');
                    }
                });

                // Cria o botão "QR Code"
                const qrButton = existingButton.cloneNode(true);
                
                // Modifica o texto do botão para "QR Code"
                const qrButtonText = qrButton.querySelector('div.h-fill');
                if (qrButtonText) {
                    qrButtonText.textContent = 'QR Code';
                }

                // Adiciona funcionalidade no clique do botão QR Code
                qrButton.addEventListener('click', () => {
                    // Pega a URL atual da página e limpa os parâmetros
                    const currentURL = cleanURL(window.location.href);
                    
                    // Monta a URL da API do QR Server
                    const qrApiURL = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(currentURL)}`;
                    
                    // Abre o QR code em uma nova aba
                    window.open(qrApiURL, '_blank');
                });

                // Insere os botões na div (Indexar e QR Code)
                targetDiv.appendChild(indexButton);
                targetDiv.appendChild(qrButton);
            } else {
                console.warn('Botão existente não encontrado dentro da div!');
            }
        } else {
            console.warn('Div alvo não encontrada!');
        }
    });
})();