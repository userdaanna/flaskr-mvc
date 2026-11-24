from flask import Blueprint, render_template, request

bp = Blueprint("calculos", __name__, url_prefix="/calculos")

def calcular_irpf(salario_bruto):
    if salario_bruto <= 2259.20:
        aliquota, deducao = 0.0, 0.0
    elif salario_bruto <= 2826.65:
        aliquota, deducao = 0.075, 169.44
    elif salario_bruto <= 3751.05:
        aliquota, deducao = 0.15, 381.44
    elif salario_bruto <= 4664.68:
        aliquota, deducao = 0.225, 662.77
    else:
        aliquota, deducao = 0.275, 896.00
    desconto = max(0.0, (salario_bruto * aliquota) - deducao)
    return round(desconto, 2), round(aliquota * 100, 1)

def calcular_rescisao_13(salario_base, meses_trabalhados):
    meses = max(0, min(12, meses_trabalhados))
    valor_13 = (salario_base / 12.0) * meses
    return round(valor_13, 2)

@bp.route("/painel", methods=("GET", "POST"))
def painel():
    resultado_irpf = None
    resultado_rescisao = None

    if request.method == "POST":
        tipo = request.form.get("tipo_calculo")
        if tipo == "irpf":
            salario = float(request.form.get("salario_bruto", 0) or 0)
            desconto, aliquota = calcular_irpf(salario)
            resultado_irpf = {
                "salario_bruto": salario,
                "aliquota": aliquota,
                "desconto": desconto,
                "liquido": round(salario - desconto, 2),
            }
        elif tipo == "rescisao":
            salario_base = float(request.form.get("salario_base", 0) or 0)
            meses = int(request.form.get("meses_trabalhados", 0) or 0)
            valor_13 = calcular_rescisao_13(salario_base, meses)
            resultado_rescisao = {
                "salario_base": salario_base,
                "meses": meses,
                "valor_13": valor_13,
            }

    return render_template(
        "calculos/index.html",
        resultado_irpf=resultado_irpf,
        resultado_rescisao=resultado_rescisao,
    )
