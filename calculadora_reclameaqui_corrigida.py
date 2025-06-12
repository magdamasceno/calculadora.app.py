import streamlit as st
import math

st.set_page_config(page_title="Calculadora RA", layout="centered")

# Estilo CSS customizado
st.markdown(
    """
    <style>
        body {
            background-color: #1B2B1F;
            color: white;
        }
        .stApp {
            background-color: #1B2B1F;
        }
        .stTextInput label, .stNumberInput label {
            color: #ff69b4 !important;
            font-weight: bold;
        }
        input[type="number"], input[type="text"] {
            color: black !important;
            font-weight: bold;
        }
        h1, h2, h3 {
            color: white !important;
            font-weight: bold;
        }
        .stButton>button {
            background-color: #3cba54;
            color: white;
            font-weight: bold;
        }
        .stAlert {
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Calculadora Reclame AQUI")

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

    avaliacoes_positivas_final = avaliacoes_para_is
    ta_final_estimado = total_avaliacoes_atual + avaliacoes_positivas_final

    todos_criterios_met = (
        ir_atual_percent >= meta_ir or respostas_necessarias == 0
    ) and (
        is_atual_percent >= meta_is or avaliacoes_positivas_final == 0
    ) and (
        mn_atual >= meta_mn
    ) and (
        inn_atual_percent >= meta_inn
    ) and (
        ta_final_estimado >= meta_ta
    )

    if todos_criterios_met and avaliacoes_positivas_final == 0 and respostas_necessarias == 0:
         return 0, 0

    return avaliacoes_positivas_final, respostas_necessarias

with st.form("formulario_similar"):
    total_reclamacoes = st.number_input("Total de reclamações", min_value=0, step=1)
    total_respostas = st.number_input("Total de respostas", min_value=0, step=1)
    media_notas_txt = st.text_input("Média das notas", placeholder="Ex: 7,38")
    indice_solucao_txt = st.text_input("Índice de solução (%)", placeholder="Ex: 86,1")
    indice_novos_negocios_txt = st.text_input("Índice de novos negócios (%)", placeholder="Ex: 80,5")
    total_avaliacoes = st.number_input("Total de avaliações", min_value=0, step=1)
    submitted = st.form_submit_button("Calcular Avaliação")

if submitted:
    media_notas_val = to_float(media_notas_txt)
    indice_solucao_val = to_float(indice_solucao_txt)
    indice_novos_negocios_val = to_float(indice_novos_negocios_txt)

    if total_reclamacoes == 0 :
        st.warning("Por favor, Total de Reclamações deve ser maior que zero.")
    else:
        AR_calculado, ir_calculado = calcular_ar_e_ir(total_respostas, total_reclamacoes, media_notas_val, indice_solucao_val, indice_novos_negocios_val)

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

        st.markdown(f"### Sua reputação é **{reputacao_estimada}** e o AR é **{AR_calculado:.1f}**.")

        if not ja_ra1000:
            positivas_ra1000, respostas_ra1000 = estimar_para_ra1000(
                total_avaliacoes, indice_solucao_val, ir_calculado,
                total_reclamacoes, total_respostas, media_notas_val, indice_novos_negocios_val
            )
            st.info(f"Para atingir a reputação RA1000 você precisa de mais **{positivas_ra1000} avaliações positivas** e mais **{respostas_ra1000} novas respostas públicas**.")
        else:
             st.success("Você já atinge os critérios para RA1000!")

        negativas_para_bom = estimar_avaliacoes_para_cair_bom(AR_calculado)
        if reputacao_estimada in ["ÓTIMO", "RA1000"]:
            st.warning(f"Por outro lado se você obter mais **{negativas_para_bom} avaliações negativas**, sua reputação pode descer.")
