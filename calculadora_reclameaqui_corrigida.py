import streamlit as st
import math

st.set_page_config(page_title="Calculadora Reclame AQUI Similares", layout="centered")

# CSS personalizado
st.markdown("""
    <style>
    /* Fundo geral */
    .stApp {
        background-color: #015e2e;
    }
    /* Título principal */
    h1 {
        color: white !important;
        font-weight: bold !important;
    }
    /* Cor dos números digitados nos campos */
    input[type="number"], input[type="text"] {
        color: black !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

def to_float(text):
    try:
        return float(text.replace(',', '.'))
    except:
        return 0.0

def calcular_ar_e_ir(respostas, reclamacoes, notas, solucao, novos_negocios):
    ir = (respostas / reclamacoes) * 100 if reclamacoes > 0 else 0
    ar_score = ((ir * 2) + (notas * 10 * 3) + (solucao * 3) + (novos_negocios * 2)) / 100
    return ar_score, ir

def estimar_avaliacoes_para_cair_bom(ar_atual):
    if ar_atual <= 7.0:
        return 0
    num_avaliacoes_negativas = (533 / 1.4) * (ar_atual - 7.0)
    return math.ceil(num_avaliacoes_negativas) if num_avaliacoes_negativas > 0 else 0

def estimar_para_ra1000(total_avaliacoes_atual, is_atual_percent, ir_atual_percent, total_reclamacoes, total_respostas_atual, mn_atual, inn_atual_percent):
    meta_ir = 90.0
    meta_is = 90.0
    meta_mn = 7.0
    meta_inn = 70.0
    meta_ta = 50.0

    respostas_necessarias = 0
    if ir_atual_percent < meta_ir and total_reclamacoes > 0:
        respostas_necessarias = math.ceil((meta_ir / 100 * total_reclamacoes) - total_respostas_atual)
        respostas_necessarias = max(0, respostas_necessarias)

    avaliacoes_para_is = 0
    if is_atual_percent < meta_is and total_avaliacoes_atual > 0:
        num_resolvidas_atuais = total_avaliacoes_atual * (is_atual_percent / 100)
        if (1 - meta_is / 100) == 0:
            avaliacoes_para_is = float('inf') if num_resolvidas_atuais < total_avaliacoes_atual else 0
        else:
            avaliacoes_para_is = ((meta_is / 100 * total_avaliacoes_atual) - num_resolvidas_atuais) / (1 - meta_is / 100)
        avaliacoes_para_is = math.ceil(avaliacoes_para_is)
        avaliacoes_para_is = max(0, avaliacoes_para_is)
    elif is_atual_percent < meta_is and total_avaliacoes_atual == 0:
        if is_atual_percent < meta_is:
            avaliacoes_para_is = meta_ta

    ta_final_estimado = total_avaliacoes_atual + avaliacoes_para_is

    todos_criterios_met = (
        ir_atual_percent >= meta_ir or respostas_necessarias == 0
    ) and (
        is_atual_percent >= meta_is or avaliacoes_para_is == 0
    ) and (
        mn_atual >= meta_mn
    ) and (
        inn_atual_percent >= meta_inn
    ) and (
        ta_final_estimado >= meta_ta
    )

    if todos_criterios_met and avaliacoes_para_is == 0 and respostas_necessarias == 0:
        return 0, 0

    return avaliacoes_para_is, respostas_necessarias

st.title("Calculadora de Avaliação – Estimativas Similares")

with st.form("formulario_similar"):
    total_reclamacoes = st.number_input("Total de reclamações", min_value=0, step=1, value=0)
    total_respostas = st.number_input("Total de respostas", min_value=0, step=1, value=0)
    media_notas_txt = st.text_input("Média das notas", placeholder="Ex: 7,38", value="")
    indice_solucao_txt = st.text_input("Índice de solução (%)", placeholder="Ex: 86,1", value="")
    indice_novos_negocios_txt = st.text_input("Índice de novos negócios (%)", placeholder="Ex: 80,5", value="")
    total_avaliacoes = st.number_input("Total de avaliações", min_value=0, step=1, value=0)

    submitted = st.form_submit_button("Calcular Avaliação (Estimativa Similar)")

if submitted:
    media_notas_val = to_float(media_notas_txt)
    indice_solucao_val = to_float(indice_solucao_txt)
    indice_novos_negocios_val = to_float(indice_novos_negocios_txt)

    if total_reclamacoes == 0:
        st.warning("Por favor, Total de Reclamações deve ser maior que zero.")
    else:
        AR_calculado, ir_calculado = calcular_ar_e_ir(
            total_respostas, total_reclamacoes,
            media_notas_val, indice_solucao_val, indice_novos_negocios_val
        )

        reputacao_estimada = "NÃO RECOMENDADA"
        if AR_calculado >= 8: reputacao_estimada = "ÓTIMO"
        elif AR_calculado >= 7: reputacao_estimada = "BOM"
        elif AR_calculado >= 6: reputacao_estimada = "REGULAR"
        elif AR_calculado >= 5: reputacao_estimada = "RUIM"

        ja_ra1000 = (
            ir_calculado >= 90.0 and
            indice_solucao_val >= 90.0 and
            media_notas_val >= 7.0 and
            indice_novos_negocios_val >= 70.0 and
            total_avaliacoes >= 50
        )
        if ja_ra1000:
            reputacao_estimada = "RA1000"

        st.markdown(f"<h4 style='color:white;'>Sua reputação é <b style='color:#00ff99;'>{reputacao_estimada}</b> e o AR é <b style='color:#00ccff;'>{AR_calculado:.1f}</b>.</h4>", unsafe_allow_html=True)

        if not ja_ra1000:
            positivas_ra1000, respostas_ra1000 = estimar_para_ra1000(
                total_avaliacoes, indice_solucao_val, ir_calculado,
                total_reclamacoes, total_respostas, media_notas_val, indice_novos_negocios_val
            )
            st.markdown(f"<p style='color:white; font-weight:bold;'>Para atingir a reputação RA1000 você precisa de mais <span style='color:lightgreen;'>{positivas_ra1000} avaliações positivas</span> e mais <span style='color:cyan;'>{respostas_ra1000} novas respostas públicas</span>.</p>", unsafe_allow_html=True)
        else:
            st.success("Você já atinge os critérios para RA1000!")

        negativas_para_bom = estimar_avaliacoes_para_cair_bom(AR_calculado)
        if reputacao_estimada == "ÓTIMO" or reputacao_estimada == "RA1000":
            st.markdown(f"<p style='color:white; font-weight:bold;'>Por outro lado se você obter mais <span style='color:gold;'>{negativas_para_bom} avaliações negativas</span>, sua reputação pode descer.</p>", unsafe_allow_html=True)
