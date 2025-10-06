import sqlite3

conn = sqlite3.connect("banco.db")
cursor = conn.cursor()

# =========================
# CONTEÚDOS TRILHA 1 - BITCOIN
# =========================
trilha_1_conteudos = [
    {
        "titulo": "História do Bitcoin",
        "descricao": "Como surgiu o Bitcoin, seu impacto global e evolução da tecnologia blockchain",
        "texto": """
<p>O Bitcoin foi criado em 2009 por <strong>Satoshi Nakamoto</strong>, um pseudônimo de uma pessoa ou grupo ainda desconhecido. A motivação para criar essa criptomoeda surgiu após a crise financeira global de 2008, quando se tornou evidente a fragilidade e a centralização do sistema financeiro tradicional. Bancos centrais imprimiam dinheiro de forma quase ilimitada, governos precisavam socorrer instituições financeiras em colapso e milhões de pessoas perderam suas economias ou tiveram seus empregos afetados. Nesse contexto, o Bitcoin foi idealizado como uma forma de transferir valor de maneira <em>descentralizada</em>, segura, transparente e sem a necessidade de intermediários.</p>

<p>O desenvolvimento do Bitcoin passou por vários marcos históricos importantes. Em <strong>2008</strong>, Satoshi Nakamoto publicou o whitepaper intitulado <a href="https://bitcoin.org/bitcoin.pdf" target="_blank">"Bitcoin: A Peer-to-Peer Electronic Cash System"</a>. Este documento descrevia um sistema financeiro digital baseado em um livro-razão público, chamado <strong>blockchain</strong>, que registraria todas as transações de forma imutável e criptografada. O whitepaper explicava como a combinação de criptografia, consenso distribuído e mineração permitiria criar dinheiro digital confiável sem a necessidade de autoridades centrais.</p>

<p>Em <strong>2009</strong>, o software Bitcoin foi lançado e o primeiro bloco, conhecido como <em>Bloco Gênesis</em>, foi minerado. Este bloco continha uma mensagem oculta: "The Times 03/Jan/2009 Chancellor on brink of second bailout for banks", reforçando a filosofia de descentralização por trás da moeda.</p>

<p>Em <strong>2010</strong>, ocorreu a primeira transação prática com Bitcoin: duas pizzas foram compradas por 10.000 BTC, demonstrando a utilidade da moeda digital. Entre 2013 e 2017, o Bitcoin chamou atenção global com picos de preço próximos de US$ 20.000. Em 2021, atingiu mais de US$ 60.000.</p>

<p>O Bitcoin também inspirou <strong>DeFi</strong>, <strong>smart contracts</strong> e outras inovações no ecossistema cripto.</p>

<p>Vídeo recomendado:</p>
<iframe width="560" height="315" src="https://www.youtube.com/embed/Gc2en3nHxA4" title="História do Bitcoin" frameborder="0" allowfullscreen></iframe>

<p>Referências adicionais:</p>
<ul>
<li><a href="https://www.investopedia.com/terms/b/bitcoin.asp" target="_blank">Investopedia - Bitcoin</a></li>
<li><a href="https://www.coindesk.com/learn/bitcoin-101" target="_blank">CoinDesk - Bitcoin 101</a></li>
<li><a href="https://www.bitcoin.org/bitcoin.pdf" target="_blank">Whitepaper do Bitcoin</a></li>
</ul>
"""
    },
    {
        "titulo": "Como o Bitcoin Funciona",
        "descricao": "Entenda a tecnologia por trás do Bitcoin",
        "texto": """
<p>O Bitcoin utiliza a tecnologia <strong>blockchain</strong>, que é um registro público, imutável e descentralizado. Cada transação é validada por mineradores que resolvem problemas matemáticos complexos, garantindo a segurança da rede.</p>

<p>Componentes principais:</p>
<ul>
<li><strong>Blockchain:</strong> registro de todas as transações.</li>
<li><strong>Mineração:</strong> validação dos blocos e emissão de novos bitcoins.</li>
<li><strong>Chaves criptográficas:</strong> protegem as transações e as carteiras.</li>
<li><strong>Transações peer-to-peer:</strong> sem intermediários como bancos.</li>
</ul>

<p>Vídeo explicativo:</p>
<iframe width="560" height="315" src="https://www.youtube.com/embed/bBC-nXj3Ng4" title="Como o Bitcoin Funciona" frameborder="0" allowfullscreen></iframe>
"""
    },
    {
        "titulo": "Vantagens e Desvantagens",
        "descricao": "Principais pontos positivos e limitações do Bitcoin",
        "texto": """
<p>O Bitcoin oferece diversas vantagens, mas também possui limitações:</p>
<ul>
<li><strong>Vantagens:</strong> descentralização, segurança, anonimato parcial, oferta limitada (21 milhões), liberdade financeira.</li>
<li><strong>Desvantagens:</strong> alta volatilidade, uso limitado como meio de pagamento, consumo energético elevado, riscos regulatórios.</li>
</ul>

<p>Vídeo explicativo:</p>
<iframe width="560" height="315" src="https://www.youtube.com/embed/41JCpzvnn_0" title="Vantagens e Desvantagens do Bitcoin" frameborder="0" allowfullscreen></iframe>
"""
    }
]

# =========================
# CONTEÚDOS TRILHA 2 - ETHEREUM
# =========================
trilha_2_conteudos = [
    {
        "titulo": "Introdução ao Ethereum",
        "descricao": "Conheça a Ethereum e seu papel no ecossistema de contratos inteligentes",
        "texto": """
<p>A Ethereum foi lançada em 2015 por <strong>Vitalik Buterin</strong> como uma plataforma blockchain que permite a criação de <strong>smart contracts</strong>. Diferente do Bitcoin, que é focado em ser uma moeda digital, a Ethereum possibilita a execução de programas descentralizados de forma imutável e confiável.</p>

<p>Vídeo explicativo:</p>
<iframe width="560" height="315" src="https://www.youtube.com/embed/TDGq4aeevgY" title="Introdução ao Ethereum" frameborder="0" allowfullscreen></iframe>
"""
    },
    {
        "titulo": "Smart Contracts",
        "descricao": "Como funcionam os contratos inteligentes na rede Ethereum",
        "texto": """
<p>Smart contracts são contratos autoexecutáveis com regras programadas diretamente no código. Eles permitem automatizar processos sem necessidade de intermediários, garantindo transparência e confiança.</p>

<p>Exemplo de uso:</p>
<ul>
<li>DeFi: empréstimos, staking, yield farming.</li>
<li>NFTs: criação, compra e venda de tokens não-fungíveis.</li>
<li>Governança: votação descentralizada.</li>
</ul>

<p>Vídeo explicativo:</p>
<iframe width="560" height="315" src="https://www.youtube.com/embed/ZE2HxTmxfrI" title="Smart Contracts Ethereum" frameborder="0" allowfullscreen></iframe>
"""
    }
]

# =========================
# CONTEÚDOS TRILHA 3 - SEGURANÇA
# =========================
trilha_3_conteudos = [
    {
        "titulo": "Segurança em Criptoativos",
        "descricao": "Aprenda boas práticas para proteger suas criptomoedas",
        "texto": """
<p>Segurança é fundamental ao lidar com criptoativos. Alguns cuidados incluem:</p>
<ul>
<li>Não compartilhar chaves privadas.</li>
<li>Usar autenticação de dois fatores (2FA).</li>
<li>Escolher wallets confiáveis (hardware ou software).</li>
<li>Evitar phishing e sites falsos.</li>
<li>Manter backups seguros das chaves.</li>
</ul>

<p>Vídeo explicativo:</p>
<iframe width="560" height="315" src="https://www.youtube.com/embed/Ld2cGd8XW3k" title="Segurança em Criptoativos" frameborder="0" allowfullscreen></iframe>
"""
    },
    {
        "titulo": "Tipos de Carteiras",
        "descricao": "Conheça as carteiras digitais e suas diferenças",
        "texto": """
<p>Existem dois tipos principais de carteiras de criptomoedas:</p>
<ul>
<li><strong>Hot Wallets:</strong> conectadas à internet, mais práticas mas menos seguras.</li>
<li><strong>Cold Wallets:</strong> offline, mais seguras mas menos convenientes.</li>
</ul>

<p>Vídeo explicativo:</p>
<iframe width="560" height="315" src="https://www.youtube.com/embed/7NtqQ9l9XcA" title="Tipos de Carteiras" frameborder="0" allowfullscreen></iframe>
"""
    }
]

# =========================
# Função para inserir conteúdos
# =========================
def inserir_conteudos(trilha_id, conteudos):
    for c in conteudos:
        cursor.execute("""
            INSERT INTO conteudos (trilha_id, titulo, descricao, texto)
            VALUES (?, ?, ?, ?)
        """, (trilha_id, c["titulo"], c["descricao"], c["texto"]))

# Inserindo todos os conteúdos
inserir_conteudos(1, trilha_1_conteudos)
inserir_conteudos(2, trilha_2_conteudos)
inserir_conteudos(3, trilha_3_conteudos)

conn.commit()
conn.close()
print("Todos os conteúdos foram inseridos com sucesso!")
