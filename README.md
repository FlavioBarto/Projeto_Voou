# Projeto Voou 🌍✈️

## 📌 Visão Geral
O **Projeto Voou** é uma solução analítica integrada que combina dados meteorológicos e de aviação civil para suporte decisório em agronomia e marketing aéreo.

## 👥 Personas-Alvo

### 🌾 Agronomia
**Persona**: Gestor Agrícola 

**Necessidades**:
- Monitoramento microclimático
- Previsão de safras
- Prevenção de perdas por eventos extremos

**Benefícios**:
- Análise histórica de padrões climáticos  
- Alertas em tempo real para eventos críticos  
- Otimização de calendários de plantio  

### ✈️ Aviação Comercial
**Persona**: Gerente de Marketing Aéreo 

**Necessidades**:
- Análise de desempenho de rotas
- Identificação de oportunidades de mercado
- Precificação dinâmica

**Benefícios**:
- Visualização de ocupação por rota  
- Detecção de padrões sazonais  
- Análise de ROI em rotas estratégicas  

## 📊 Dashboards

### ☀️ Módulo Climático
**KPIs Principais**:
```
🌡️ Temperatura Média Anual

🔥 Última Temperatura Registrada

⛅ Condição Climática Atual

⏱️ Última Atualização dos Dados
```

**Gráficos Disponíveis**:
```
Mapa-Múndi Interativo: Visualização da temperatura por país

Precipitação Mensal: Análise por país e ano selecionado

Distribuição de Umidade: Gráfico de pizza mostrando a umidade média por condição climática
```

### ✈️ Módulo Voos
**KPIs Principais**:
```
🧑‍🤝‍🧑 Total de Passageiros Pagos (período selecionado)

💺 Média de Assentos Oferecidos por Voo

📊 Taxa Média de Ocupação (RPK/ASK)

🛣️ Número Total de Rotas Ativas
```

**Gráficos Disponíveis**:
```
Evolução Mensal: Linha temporal da demanda e ocupação

Sazonalidade: Heatmap do volume de passageiros por rota

Relação Ocupação x Capacidade: Dispersão entre passageiros pagos e assentos oferecidos
```

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python, SQLite
- **Visualização**: Streamlit, Matplotlib, Seaborn
- **Processamento**: Pandas, NumPy
- **Estilos**: CSS personalizado

## 🚀 Como Executar

1. Clone o repositório:
```bash
git clone https://github.com/FlavioBarto/Projeto_Voou
```
Instale as dependências:

```bash
pip install pandas streamlit matplotlib seaborn
```
Execute o aplicativo:

```bash
streamlit run .\main.py
```

📦 Estrutura de Arquivos:
<pre>
Projeto_Voou/
├── arquivos_csv/                   # Arquivos de dados brutos
│   └── GlobalWeatherRepositort.csv
│   └── resumo_anual_2025.csv
├── assets/                         # Recursos visuais
│   └── style.css
├── Model/                          # Lógica de processamento de dados
│   └── criar_bd_clima.py
│   └── criar_bd_voos.py
├── View/                           # Interface e visualizações
│   └── clima.py
│   └── voos.py
├── Controller/                     # Controle e Estrutura
│   └── functions_clima.py
│   └── function_voos.py
├── voos_database.db                # Banco de dados voos
├── weather_database.db             # Banco de dados clima
└── main.py                         # Aplicação principal
</pre>

📝 Licença
Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

✉️ Contato
Para dúvidas ou sugestões, entre em contato com os desenvolvedores.