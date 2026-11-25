# AGENT INVEST 0.1

Painel web para celular de acompanhamento e simulação de operações com ações brasileiras.

## O que faz
- Consulta dados de mercado via yfinance (fonte não oficial; pode atrasar ou falhar).
- Calcula sinais experimentais com médias móveis de 20/50 dias e momentum.
- Mantém carteira simulada com capital inicial de R$ 200.
- Permite simular compras e vendas e consultar saldo/posições.

## O que NÃO faz
- Não acessa Nubank.
- Não envia ordens reais.
- Não promete rentabilidade.
- Não substitui análise financeira ou aconselhamento profissional.

## Rodar localmente
1. Instale Python 3.10+.
2. Abra um terminal na pasta do projeto.
3. Execute:
   `pip install -r requirements.txt`
4. Execute:
   `streamlit run app.py`

## Publicar para acessar pelo celular
Uma opção é publicar no Streamlit Community Cloud conectando este projeto a um repositório GitHub. O app será aberto por um link no navegador do celular. A disponibilidade e os limites do serviço dependem das regras atuais da plataforma.

## Próximas etapas
1. Testes automatizados para ordens, saldo e posições.
2. Backtesting com custos e comparação com benchmark.
3. Alertas e limites de risco.
4. Persistência de dados adequada para hospedagem.
5. Verificação de integração oficial de corretora. Não inserir senhas, tokens bancários ou códigos 2FA no projeto.
