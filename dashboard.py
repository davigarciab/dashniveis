import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go

def classificar(total, disciplina):
    if disciplina.upper() == "MATEMÁTICA":
        if total < 9:
            return "MUITO CRÍTICO"
        elif 9 <= total <= 12:
            return "CRÍTICO"
        elif 13 <= total <= 18:
            return "INTERMEDIÁRIO"
        elif total >= 19:
            return "ADEQUADO"
        else:
            return "VALOR INVÁLIDO"
    else:  # Critério padrão (PORTUGUÊS)
        if total < 10:
            return "MUITO CRÍTICO"
        elif 10 <= total <= 17:
            return "CRÍTICO"
        elif 18 <= total <= 22:
            return "INTERMEDIÁRIO"
        elif total >= 23:
            return "ADEQUADO"
        else:
            return "VALOR INVÁLIDO"

cores = {
    "MUITO CRÍTICO": "red",
    "CRÍTICO": "yellow",
    "INTERMEDIÁRIO": "limegreen",
    "ADEQUADO": "deepskyblue"
}
categorias = ["MUITO CRÍTICO", "CRÍTICO", "INTERMEDIÁRIO", "ADEQUADO"]

app = dash.Dash(__name__)

# Carrega a planilha para obter as opções de filtros
df = pd.read_excel("planilha_dash.xlsx", sheet_name="turmas")
# url do Google Sheets exportando como CSV
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSiSs-iPa7L6ShE9vUV-ZYqkFKD-kLC704QBi0z_nHN1NHBDIeVXunVss7mr1qugQ/pub?output=csv"
df = pd.read_csv(url)
df.columns = df.columns.str.strip()  # Remove espaços extras dos nomes das colunas
df["TOTAL"] = pd.to_numeric(df["TOTAL"], errors="coerce")
df["CLASSIFICAÇÃO"] = df["TOTAL"].apply(lambda x: classificar(x, "PORTUGUÊS"))

anos = sorted(df["ANO"].dropna().unique())
series = sorted(df["SERIE"].dropna().unique())
disciplinas = sorted(df["DISCIPLINA"].dropna().unique())
cursos = sorted(df["TURMA"].dropna().unique())

app.layout = html.Div([
    html.H1(
        "Sistema de Acompanhamento de Níveis de Conhecimento",
        style={
            "textAlign": "center",
            "color": "#003366",
            "marginBottom": "10px",
            "fontSize": "2rem"
        }
    ),
    html.Div([
        html.Label("Ano:", style={"fontWeight": "bold", "marginRight": "5px"}),
        dcc.Dropdown(
            id='ano-dropdown',
            options=[{"label": str(ano), "value": ano} for ano in anos],
            value=anos[0],
            style={"width": "10vw", "display": "inline-block", "marginRight": "10px", "verticalAlign": "middle"}
        ),
        html.Label("Serie:", style={"fontWeight": "bold", "marginRight": "5px"}),
        dcc.Dropdown(
            id='serie-dropdown',
            options=[{"label": str(serie), "value": serie} for serie in series],
            value=series[0],
            style={"width": "10vw", "display": "inline-block", "marginRight": "10px", "verticalAlign": "middle"}
        ),
        html.Label("Disciplina:", style={"fontWeight": "bold", "marginRight": "5px"}),
        dcc.Dropdown(
            id='disciplina-dropdown',
            options=[{"label": disc, "value": disc} for disc in disciplinas],
            value=disciplinas[0],
            style={"width": "15vw", "display": "inline-block", "marginRight": "10px", "verticalAlign": "middle"}
        ),
        html.Label("Curso:", style={"fontWeight": "bold", "marginRight": "5px"}),
        dcc.Dropdown(
            id='curso-dropdown',
            options=[{"label": curso, "value": curso} for curso in cursos],
            value=cursos[0],
            style={"width": "15vw", "display": "inline-block", "verticalAlign": "middle"}
        ),
    ], style={
        "marginBottom": "10px",
        "textAlign": "center",
        "background": "#f7f9fa",
        "padding": "10px 0",
        "borderRadius": "8px",
        "boxShadow": "0 1px 4px rgba(0,0,0,0.07)"
    }),
    html.Div([
        html.Div([
            dcc.Graph(id='grafico-niveis', style={
                "background": "#fff",
                "borderRadius": "12px",
                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                "padding": "10px",
                "height": "790px"  # <-- aumente aqui para mais altura vertical
            })
        ], style={"width": "68%", "display": "inline-block", "verticalAlign": "top", "marginRight": "1%"}),
        html.Div([
            dcc.Graph(id='grafico-pizza', style={
                "background": "#fff",
                "borderRadius": "12px",
                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                "padding": "10px",
                "height": "370px"
            }),
            dcc.Graph(id='grafico-pizza-serie', style={
                "background": "#fff",
                "borderRadius": "12px",
                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                "padding": "10px",
                "height": "370px",
                "marginTop": "30px"
            })
        ], style={"width": "30%", "display": "inline-block", "verticalAlign": "top"})
    ], style={"width": "100%", "textAlign": "center", "margin": "0 auto"})
], style={"background": "#f0f4f8", "minHeight": "100vh", "padding": "0", "fontFamily": "Segoe UI, Arial, sans-serif"})

@app.callback(
    Output('grafico-niveis', 'figure'),
    Output('grafico-pizza', 'figure'),
    Output('grafico-pizza-serie', 'figure'),
    Input('ano-dropdown', 'value'),
    Input('serie-dropdown', 'value'),
    Input('disciplina-dropdown', 'value'),
    Input('curso-dropdown', 'value')
)
def atualizar_graficos(ano, serie, disciplina, curso):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()  # Remove espaços extras dos nomes das colunas
    df["TOTAL"] = pd.to_numeric(df["TOTAL"], errors="coerce")
    # Aplique a classificação considerando a disciplina selecionada
    df["CLASSIFICAÇÃO"] = df["TOTAL"].apply(lambda x: classificar(x, disciplina))

    # Gráfico da turma selecionada
    df_filtro = df[
        (df["ANO"] == ano) &
        (df["SERIE"] == serie) &
        (df["DISCIPLINA"] == disciplina) &
        (df["TURMA"] == curso)
    ]
    nomes_por_categoria = [
        "<br>".join(df_filtro[df_filtro["CLASSIFICAÇÃO"] == cat]["NOME"].tolist()) or "Nenhum"
        for cat in categorias
    ]
    contagem = [df_filtro[df_filtro["CLASSIFICAÇÃO"] == cat].shape[0] for cat in categorias]

    fig_bar = go.Figure()
    for i, cat in enumerate(categorias):
        fig_bar.add_trace(go.Bar(
            x=[cat],
            y=[contagem[i]],
            marker_color=cores[cat],
            text=[nomes_por_categoria[i]],
            textposition='inside',
            insidetextanchor='middle',
            textangle=0,
            textfont_size=15,
            hovertemplate=f"<b>{cat}</b><br>Quantidade: {contagem[i]}<br><br><b>Alunos:</b><br>{nomes_por_categoria[i] if nomes_por_categoria[i] != '' else 'Nenhum'}<extra></extra>"
        ))
    fig_bar.update_layout(
        transition=dict(duration=500, easing='cubic-in-out'),
        title={
            "text": "Distribuição dos Níveis por Estudante",
            "x": 0.5,
            "xanchor": "center"
        },
        xaxis_title="Nível",
        yaxis_title="Quantidade de Alunos",
        plot_bgcolor='#fff',
        paper_bgcolor='#fff',
        showlegend=False,
        margin=dict(t=90, b=40, l=40, r=40),
        annotations=[
            dict(
                text=f"Disciplina: {disciplina} &nbsp;|&nbsp; Serie: {serie} &nbsp;|&nbsp; Curso: {curso} &nbsp;|&nbsp; Ano: {ano}",
                xref="paper", yref="paper",
                x=0.5, y=1.06, showarrow=False,  # <-- diminua o valor de y para afastar do título
                font=dict(size=14, color="#003366"),
                xanchor="center"
            )
        ],
        bargap=0.01
    )

    fig_pizza = go.Figure(
        data=[go.Pie(
            labels=categorias,
            values=contagem,
            marker_colors=[cores[cat] for cat in categorias],
            textinfo='percent',
            hoverinfo='percent+value'
        )]
    )
    fig_pizza.update_layout(
        transition=dict(duration=500, easing='cubic-in-out'),
        title={
            "text": "Porcentagem de Alunos por Nível",
            "x": 0.5,
            "xanchor": "center"
        },
        plot_bgcolor='#fff',
        paper_bgcolor='#fff',
        margin=dict(t=40, b=100, l=40, r=40),
        annotations=[
            dict(
                text=f"Disciplina: {disciplina} &nbsp;|&nbsp; Serie: {serie} &nbsp;<br>&nbsp; Curso: {curso} &nbsp;|&nbsp; Ano: {ano}",
                xref="paper", yref="paper",
                x=0.5, y=-0.25, showarrow=False,
                font=dict(size=14, color="#003366"),
                xanchor="center"
            )
        ]
    )

    # Gráfico da série selecionada (todas as turmas da série)
    df_serie = df[
        (df["ANO"] == ano) &
        (df["SERIE"] == serie) &
        (df["DISCIPLINA"] == disciplina)
    ]
    # Ordem desejada para o gráfico horizontal
    categorias_ordenadas = ["MUITO CRÍTICO", "CRÍTICO", "INTERMEDIÁRIO", "ADEQUADO"]
    contagem_niveis_serie = [df_serie[df_serie["CLASSIFICAÇÃO"] == cat].shape[0] for cat in categorias_ordenadas]
    fig_pizza_serie = go.Figure(
        data=[go.Bar(
            y=categorias_ordenadas,
            x=contagem_niveis_serie,
            orientation='h',
            marker_color=[cores[cat] for cat in categorias_ordenadas],
            text=contagem_niveis_serie,
            textposition='auto'
        )]
    )
    fig_pizza_serie.update_layout(
        transition=dict(duration=500, easing='cubic-in-out'),
        title={
            "text": f"Níveis da Série Selecionada ({serie})",
            "x": 0.5,
            "xanchor": "center"
        },
        xaxis_title="Quantidade de Alunos",
        yaxis_title="Nível",
        plot_bgcolor='#fff',
        paper_bgcolor='#fff',
        margin=dict(t=40, b=100, l=40, r=40),
        showlegend=False,
        bargap=0.01,         # Diminua esse valor para barras mais largas (ex: 0.05 ou 0)
        bargroupgap=0.01    # Opcional: diminua para barras ainda mais próximas
    )

    return fig_bar, fig_pizza, fig_pizza_serie

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=10000)