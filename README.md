# Projeto Voou 🌍✈️

## 📌 Visão Geral
O **Projeto Voou** é uma solução analítica integrada que cruza dados meteorológicos e de aviação civil com o objetivo de fornecer suporte decisório para as áreas de agronomia e marketing aéreo. Ele utiliza um modelo de arquitetura MVC simples em Python para organizar a manipulação, visualização e análise dos dados.

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
- Otimização de calendários agrícola

### ✈️ Aviação Comercial
**Persona**: Gerente de Marketing Aéreo 

**Necessidades**:
- Análise de desempenho de rotas
- Identificação de sazonalidades
- Precificação estratégica

**Benefícios**:
- Visualização de ocupação por rota  
- Detecção de padrões sazonais  
- Análise de ROI por destino

## 📊 Dashboards

### ☀️ Módulo Climático
**KPIs Principais**:
```
🌡️ Temperatura Média Anual

🔥 Última Temperatura Registrada

⛅ Condição Climática Atual
```

### ✈️ Módulo Voos
**KPIs Principais**:
```
📊 Taxa Ocupação Média (RPK/ASK)

🧳 Volume de Passageiros por Aeroporto

📅 Picos de Demanda e Sazonalidades
```

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python, SQLite
- **Visualização**: Streamlit, Matplotlib, Seaborn
- **Processamento**: Pandas, NumPy
- **Estilos**: CSS personalizado

## ▶️ Como Executar

1. Clone o repositório:
```bash
git clone https://github.com/FlavioBarto/Projeto_Voou
```
Instale as dependências:

```bash
pip install streamlit pandas plotly matplotlib seaborn
```
Execute o aplicativo:

```bash
streamlit run .\main.py
```

## 🧱 Estrutura do Projeto
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

## 🤝 Contribuições
Contribuições são bem-vindas!<br>
Se quiser sugerir melhorias ou reportar bugs, sinta-se à vontade para abrir uma issue ou pull request.

## 📄 Licença
Este projeto está sob a licença MIT. Consulte o arquivo ```LICENSE``` para mais detalhes.