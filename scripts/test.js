// Mapeamento de colaboradores para seus e-mails
const colaboradoresEmails = {
    "@Ananda Gurgel": "ananda.gurgel@mercadolivre.com",
    "@Bruno Luiz Viana": "bruno.viana@mercadolivre.com",
    "@Edviges": "edviges.lima@mercadolivre.com",
    "@Leonardo Gudaitis Leite": "leonardo.gudaitis@mercadolivre.com",
    "@Murilo Araujo Casmala": "murilo.casmala@mercadolivre.com",
    "@Rogerio Aguiar": "rogerio.aguiar@mercadolivre.com",
    "@Gabriel Furtado Neves": "gabriel.fneves@mercadolivre.com"
};

// Mapear os meses do inglês para o português
const meses = {
    "january": "janeiro",
    "february": "fevereiro",
    "march": "março",
    "april": "abril",
    "may": "maio",
    "june": "junho",
    "july": "julho",
    "august": "agosto",
    "september": "setembro",
    "october": "outubro",
    "november": "novembro",
    "december": "dezembro"
};

function getCurrentMonth() {
    const dataAtual = new Date();
    const mesIngles = Utilities.formatDate(dataAtual, Session.getScriptTimeZone(), "MMMM yyyy").toLowerCase(); // Mês e ano atual em formato "novembro 2024"

    // Converter o mês atual para português
    const [mesInglesPalavra, ano] = mesIngles.split(" ");
    const mesAtual = `${meses[mesInglesPalavra]} ${ano}`;
    return mesAtual;
}

function parseCollaboratorData(dados, i) {
    const colaborador = dados[i][0];
    const dataMesColuna = dados[i][1].toString(); // Converte a data em string

    // Extrai o mês e ano do formato "1º de novembro de 2024"
    const regex = /de (\w+) de (\d{4})/; // Expressão para extrair o mês e o ano
    const match = dataMesColuna.match(regex);

    if(!match) return ({colaborador, match: null});
    const mesColuna = `${match[1]} ${match[2]}`.toLowerCase();
    return {colaborador, mesColuna};
}

function verificarRegistrosColaboradores() {
    // Configurações e variáveis iniciais
    const planilha = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Página1"); // Substitua com o nome da sua planilha
    const dados = planilha.getDataRange().getValues();
    const mesAtual = getCurrentMonth();

    // Armazenar colaboradores com registro no mês atual
    const registrosNoMesAtual = new Set();

    // Verifica os registros existentes
    for (let i = 1; i < dados.length; i++) { // Começa em 1 para ignorar o cabeçalho
        const {colaborador, mesColuna} = parseCollaboratorData(dados, i);

        if (mesColuna) {
            // Se o registro é do colaborador e do mês atual, adiciona ao set
            if (colaboradoresEmails.hasOwnProperty(colaborador) && mesColuna === mesAtual) {
                registrosNoMesAtual.add(colaborador);
            }
        }
    }

    // Verifica colaboradores ausentes e faz o POST para cada um
    Object.keys(colaboradoresEmails).forEach(colaborador => { // Usa Object.keys para iterar sobre os colaboradores
        if (!registrosNoMesAtual.has(colaborador)) {
            fazerPostAusencia(colaboradoresEmails[colaborador], colaborador); // Passa o e-mail e o nome do colaborador
        }
    });
}

// Função para fazer o POST caso o colaborador esteja ausente no mês
function fazerPostAusencia(email, colaborador) {
    const url = "https://hooks.slack.com/triggers/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"; // Endpoint Slack

    const payload = {
        "Colaborador": email // Usa o e-mail do colaborador
    };

    const options = {
        method: "post",
        contentType: "application/json",
        payload: JSON.stringify(payload)
    };

    try {
        UrlFetchApp.fetch(url, options);
        Logger.log(`E-mail enviado para: ${colaborador} (${email})`); // Loga para quem foi enviado
    } catch (error) {
        Logger.log(`Erro ao fazer POST para ${email}: ${error.message}`);
    }
}


function verificarRegistrosColaboradores() {
    // Configurações e variáveis iniciais
    const planilha = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Página1"); // Substitua com o nome da sua planilha
    const dados = planilha.getDataRange().getValues();

    const dataAtual = new Date();
    const mesIngles = Utilities.formatDate(dataAtual, Session.getScriptTimeZone(), "MMMM yyyy").toLowerCase(); // Mês e ano atual em formato "novembro 2024"

    // Converter o mês atual para português
    const [mesInglesPalavra, ano] = mesIngles.split(" ");
    const mesAtual = `${meses[mesInglesPalavra]} ${ano}`;

    // Armazenar colaboradores com registro no mês atual
    const registrosNoMesAtual = new Set();

    // Verifica os registros existentes
    for (let i = 1; i < dados.length; i++) { // Começa em 1 para ignorar o cabeçalho
        const colaborador = dados[i][0];
        const dataMesColuna = dados[i][1].toString(); // Converte a data em string

        // Extrai o mês e ano do formato "1º de novembro de 2024"
        const regex = /de (\w+) de (\d{4})/; // Expressão para extrair o mês e o ano
        const match = dataMesColuna.match(regex);

        if (match) {
            const mesColuna = `${match[1]} ${match[2]}`.toLowerCase(); // Formata como "novembro 2024"

            // Se o registro é do colaborador e do mês atual, adiciona ao set
            if (colaboradoresEmails.hasOwnProperty(colaborador) && mesColuna === mesAtual) {
                registrosNoMesAtual.add(colaborador);
            }
        }
    }

    // Verifica colaboradores ausentes e faz o POST para cada um
    Object.keys(colaboradoresEmails).forEach(colaborador => { // Usa Object.keys para iterar sobre os colaboradores
        if (!registrosNoMesAtual.has(colaborador)) {
            fazerPostAusencia(colaboradoresEmails[colaborador], colaborador); // Passa o e-mail e o nome do colaborador
        }
    });
}

// Função para fazer o POST caso o colaborador esteja ausente no mês
function fazerPostAusencia(email, colaborador) {
    const url = "https://hooks.slack.com/triggers/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"; // Endpoint Slack

    const payload = {
        "Colaborador": email // Usa o e-mail do colaborador
    };

    const options = {
        method: "post",
        contentType: "application/json",
        payload: JSON.stringify(payload)
    };

    try {
        UrlFetchApp.fetch(url, options);
        Logger.log(`E-mail enviado para: ${colaborador} (${email})`); // Loga para quem foi enviado
    } catch (error) {
        Logger.log(`Erro ao fazer POST para ${email}: ${error.message}`);
    }
}
