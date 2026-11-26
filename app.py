"""Dashboard del proyecto final de Electiva II.

Demanda de empleos en datos en Latinoamérica (LinkedIn, consulta del 29/10/2026).
Autores: Camilo Dorado y Sebastián Beltrán.

Ejecutar con:  streamlit run app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

RUTA_DATOS = Path(__file__).parent / 'datos' / 'ofertas_empleo_limpias.csv'
FUENTE = ('Fuente: anuncios públicos de LinkedIn Jobs extraídos con web scraping el 29/10/2026 '
          '(3.045 registros originales; 2.572 tras la limpieza). Elaboración propia.')
COLORES_PAIS = {'Colombia': '#F2C14E', 'Argentina': '#5DA9E9', 'Chile': '#D1495B',
                'Uruguay': '#3A6EA5', 'Estados Unidos': '#8C8C8C'}
COLORES_SENIORITY = {'Junior / Practicante': '#8CD790', 'Semi senior': '#F2C14E',
                     'Senior / Líder': '#D1495B', 'No especificado': '#D9D9D9'}
COLORES_MODALIDAD = {'Remoto': '#3A6EA5', 'Híbrido': '#5DA9E9', 'No especificado': '#D9D9D9'}
ORDEN_SENIORITY = list(COLORES_SENIORITY)
PLANTILLA = 'plotly_white'

st.set_page_config(page_title='Empleos en datos LATAM', page_icon='📊', layout='wide')


@st.cache_data
def cargar_datos():
    df = pd.read_csv(RUTA_DATOS, encoding='utf-8-sig', parse_dates=['Fecha publicación'], dtype={'ID': str})
    return df


def porcentaje(parte, total):
    return 0 if total == 0 else parte / total * 100


df = cargar_datos()

# Filtros
st.sidebar.header('Filtros')
region = st.sidebar.radio('Región', ['Latinoamérica', 'Estados Unidos', 'Todas'], index=0,
                          help='Las búsquedas de México, Brasil y Perú devolvieron ofertas de EE. UU.; '
                               'el análisis principal es solo Latinoamérica.')
base = df if region == 'Todas' else df[df['Región'] == region]

paises = sorted(base['País'].unique())
sel_paises = st.sidebar.multiselect('País', paises, default=paises)
roles = sorted(base['Rol'].unique())
sel_roles = st.sidebar.multiselect('Rol', roles, default=roles)
sel_seniority = st.sidebar.multiselect('Nivel de experiencia', ORDEN_SENIORITY, default=ORDEN_SENIORITY)
modalidades = list(COLORES_MODALIDAD)
sel_modalidad = st.sidebar.multiselect('Modalidad', modalidades, default=modalidades)
incluir_antiguas = st.sidebar.checkbox('Incluir publicaciones antiguas (> 58 días)', value=True,
                                       help='Anuncios atípicos según el rango intercuartílico. '
                                            'Siguen activos, por eso se incluyen por defecto.')

f = base[base['País'].isin(sel_paises) & base['Rol'].isin(sel_roles)
         & base['Seniority'].isin(sel_seniority) & base['Modalidad'].isin(sel_modalidad)]
if not incluir_antiguas:
    f = f[~f['Publicación antigua']]

st.sidebar.markdown('---')
st.sidebar.caption('Proyecto final · Electiva II – Introducción a la Ciencia de Datos · '
                   'Fundación Universitaria de Popayán · Camilo Dorado y Sebastián Beltrán')

# Encabezado
st.title('Demanda de empleos en datos en Latinoamérica')
st.markdown(
    '**Pregunta:** ¿cómo se distribuye la demanda de empleos en datos publicada en LinkedIn en Colombia, '
    'Argentina, Chile y Uruguay según país, ciudad, rol, nivel de experiencia y modalidad?  \n'
    '**Datos:** ofertas para Data Engineer, Data Analyst, Data Scientist, BI Analyst y ML Engineer, '
    'limpiadas en Python (países normalizados, duplicados y ofertas que no son de datos eliminados).'
)

if f.empty:
    st.warning('No hay ofertas con esa combinación de filtros. Amplía la selección en la barra lateral.')
    st.stop()

# Indicadores
n = len(f)
con_nivel = f[f['Seniority'] != 'No especificado']
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric('Ofertas', f'{n:,}'.replace(',', '.'))
k2.metric('Empresas distintas', f"{f['Empresa'].nunique():,}".replace(',', '.'))
k3.metric('% Senior / Líder', help='Calculado solo sobre los anuncios que indican el nivel en el título.', value=
          f"{porcentaje((con_nivel['Seniority'] == 'Senior / Líder').sum(), len(con_nivel)):.1f} %")
k4.metric('% Remoto', help='Anuncios que dicen remoto en el título o la ubicación.', value= f"{porcentaje((f['Modalidad'] == 'Remoto').sum(), n):.1f} %")
k5.metric('Mediana de antigüedad', f"{f['Días publicada'].median():.0f} días")

st.markdown('---')

# Fila 1: geografía
c1, c2 = st.columns(2)
with c1:
    por_pais = f['País'].value_counts().rename_axis('País').reset_index(name='Ofertas')
    por_pais['%'] = por_pais['Ofertas'] / n * 100
    fig = px.bar(por_pais.sort_values('Ofertas'), x='Ofertas', y='País', orientation='h', color='País',
                 color_discrete_map=COLORES_PAIS, text=por_pais.sort_values('Ofertas')['%'].map('{:.1f} %'.format),
                 title='Ofertas por país', template=PLANTILLA)
    fig.update_layout(showlegend=False, xaxis_title='Número de ofertas', yaxis_title='', height=380)
    st.plotly_chart(fig, width='stretch')

with c2:
    con_ciudad = f[f['Ciudad'] != 'No especificada']
    top = con_ciudad.groupby(['Ciudad', 'País']).size().reset_index(name='Ofertas') \
                    .sort_values('Ofertas', ascending=False).head(10)
    fig = px.bar(top.sort_values('Ofertas'), x='Ofertas', y='Ciudad', orientation='h', color='País',
                 color_discrete_map=COLORES_PAIS, title='Top 10 ciudades con más ofertas', template=PLANTILLA)
    fig.update_layout(xaxis_title='Número de ofertas', yaxis_title='', height=380, legend_title='',
                      yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, width='stretch')
    st.caption(f"{porcentaje((f['Ciudad'] == 'No especificada').sum(), n):.1f} % de las ofertas filtradas "
               'solo indica el país o la región, no la ciudad.')

# Fila 2: roles y seniority
c3, c4 = st.columns(2)
with c3:
    por_rol = f['Rol'].value_counts().rename_axis('Rol').reset_index(name='Ofertas')
    fig = px.bar(por_rol.sort_values('Ofertas'), x='Ofertas', y='Rol', orientation='h',
                 color_discrete_sequence=['#3A6EA5'], title='Ofertas por rol (según el título)', template=PLANTILLA)
    fig.update_layout(xaxis_title='Número de ofertas', yaxis_title='', height=380)
    st.plotly_chart(fig, width='stretch')

with c4:
    rol_sen = pd.crosstab(f['Rol'], f['Seniority'], normalize='index').mul(100) \
                .reindex(columns=[s for s in ORDEN_SENIORITY if s in f['Seniority'].unique()])
    largo = rol_sen.reset_index().melt(id_vars='Rol', var_name='Nivel', value_name='%')
    fig = px.bar(largo, x='%', y='Rol', color='Nivel', orientation='h', color_discrete_map=COLORES_SENIORITY,
                 title='Nivel de experiencia pedido por rol', template=PLANTILLA,
                 category_orders={'Nivel': ORDEN_SENIORITY})
    fig.update_layout(barmode='stack', xaxis_title='% de las ofertas del rol', yaxis_title='', height=380,
                      legend_title='', legend=dict(orientation='h', y=-0.25))
    st.plotly_chart(fig, width='stretch')

# Fila 3: modalidad y empresas
c5, c6 = st.columns(2)
with c5:
    mod = pd.crosstab(f['País'], f['Modalidad'], normalize='index').mul(100).reset_index() \
            .melt(id_vars='País', var_name='Modalidad', value_name='%')
    fig = px.bar(mod, x='%', y='País', color='Modalidad', orientation='h', color_discrete_map=COLORES_MODALIDAD,
                 title='Modalidad mencionada en el anuncio, por país', template=PLANTILLA,
                 category_orders={'Modalidad': modalidades})
    fig.update_layout(barmode='stack', xaxis_title='% de las ofertas del país', yaxis_title='', height=380,
                      legend_title='', legend=dict(orientation='h', y=-0.25))
    st.plotly_chart(fig, width='stretch')

with c6:
    emp = f['Empresa'].value_counts().head(10).rename_axis('Empresa').reset_index(name='Ofertas')
    fig = px.bar(emp.sort_values('Ofertas'), x='Ofertas', y='Empresa', orientation='h',
                 color_discrete_sequence=['#D1495B'], title='Top 10 empresas que más publican', template=PLANTILLA)
    fig.update_layout(xaxis_title='Número de ofertas', yaxis_title='', height=380)
    st.plotly_chart(fig, width='stretch')
    st.caption(f"Estas 10 empresas concentran el {porcentaje(emp['Ofertas'].sum(), n):.1f} % de las ofertas filtradas.")

# Fila 4: tiempo
recientes = f[f['Fecha publicación'] >= '2026-09-01']
semana = recientes.groupby([pd.Grouper(key='Fecha publicación', freq='W-MON', label='left', closed='left'), 'País']) \
                  .size().reset_index(name='Ofertas')
fig = px.line(semana, x='Fecha publicación', y='Ofertas', color='País', markers=True, color_discrete_map=COLORES_PAIS,
              title='Ofertas publicadas por semana (septiembre y octubre de 2026)', template=PLANTILLA)
fig.update_layout(xaxis_title='Semana de publicación', yaxis_title='Número de ofertas', height=360, legend_title='')
st.plotly_chart(fig, width='stretch')
st.caption('Las semanas recientes tienen más anuncios porque LinkedIn retira los anuncios viejos: '
           'no es una tendencia de crecimiento.')

# Hallazgos y tabla
with st.expander('Hallazgos principales (base completa de Latinoamérica)', expanded=True):
    st.markdown(
        '1. **Concentración en capitales:** entre las ofertas que indican ciudad, la capital reúne entre el 65 % '
        '(Santiago) y el 80 % (Buenos Aires).\n'
        '2. **Se pide experiencia:** el 53 % no dice el nivel; de las que sí, el 89 % pide Senior/Líder y solo el 5 % Junior.\n'
        '3. **El remoto explícito depende de pocas empresas:** Uruguay 29 %, Colombia 12 %, Chile 9 %, Argentina 4 %; '
        'casi todo viene de BairesDev y FullStack.\n'
        '4. **Mercado fragmentado:** 748 empresas, el 59,5 % publicó una sola oferta; las 10 primeras suman el 19 %.\n\n'
        '*Son observaciones descriptivas, no relaciones de causa y efecto. Los conteos entre países dependen de cuántas '
        'búsquedas hicimos en cada uno; por eso conviene comparar porcentajes.*'
    )

with st.expander('Ver ofertas filtradas'):
    st.dataframe(f[['Título', 'Empresa', 'Rol', 'Seniority', 'Modalidad', 'Ciudad', 'País', 'Fecha publicación', 'URL']]
                 .sort_values('Fecha publicación', ascending=False),
                 width='stretch', hide_index=True,
                 column_config={'URL': st.column_config.LinkColumn('Anuncio'),
                                'Fecha publicación': st.column_config.DateColumn(format='DD/MM/YYYY')})
    st.download_button('Descargar CSV filtrado', f.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig'),
                       file_name='ofertas_filtradas.csv', mime='text/csv')

st.markdown('---')
st.caption(FUENTE)
