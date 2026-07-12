"""Búsqueda de medicamentos, equivalentes y comparación de precios."""

from dataclasses import dataclass
from difflib import get_close_matches

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..modelos import Medicamento, Precio
from .normalizacion import interpretar_consulta, normalizar_texto


@dataclass
class OpcionPrecio:
    medicamento: Medicamento
    farmacia_nombre: str
    precio_bs: float
    unidad_venta: str


@dataclass
class ResultadoConsulta:
    encontrado: bool
    mensaje: str
    medicamento: Medicamento | None = None
    equivalentes: list[Medicamento] | None = None
    opciones: list[OpcionPrecio] | None = None


def buscar_medicamento(sesion: Session, texto: str) -> Medicamento | None:
    """Busca por nombre comercial o principio activo, con tolerancia a errores."""
    consulta = interpretar_consulta(texto)
    nombre = consulta.nombre or normalizar_texto(texto)
    if not nombre:
        return None

    candidatos = list(sesion.scalars(select(Medicamento)))
    if not candidatos:
        return None

    def _filtrar_por_consulta(meds: list[Medicamento]) -> list[Medicamento]:
        resultado = meds
        if consulta.concentracion:
            valor, unidad = consulta.concentracion
            resultado = [
                m for m in resultado
                if m.concentracion_valor == valor and m.concentracion_unidad == unidad
            ] or resultado
        if consulta.forma:
            resultado = [m for m in resultado if m.forma == consulta.forma] or resultado
        return resultado

    # 1) Coincidencia por subcadena en nombre comercial o principio activo
    directos = [
        m for m in candidatos
        if nombre in normalizar_texto(m.nombre_comercial)
        or nombre in normalizar_texto(m.principio_activo)
    ]
    if directos:
        return _filtrar_por_consulta(directos)[0]

    # 2) Coincidencia difusa (errores de tipeo)
    por_nombre = {normalizar_texto(m.nombre_comercial): m for m in candidatos}
    por_nombre.update({normalizar_texto(m.principio_activo): m for m in candidatos})
    cercanos = get_close_matches(nombre, list(por_nombre), n=3, cutoff=0.75)
    if cercanos:
        return _filtrar_por_consulta([por_nombre[c] for c in cercanos])[0]
    return None


def buscar_equivalentes(sesion: Session, medicamento: Medicamento) -> list[Medicamento]:
    """Medicamentos con el mismo principio activo, concentración y forma."""
    return list(
        sesion.scalars(
            select(Medicamento).where(
                Medicamento.principio_activo == medicamento.principio_activo,
                Medicamento.concentracion_valor == medicamento.concentracion_valor,
                Medicamento.concentracion_unidad == medicamento.concentracion_unidad,
                Medicamento.forma == medicamento.forma,
                Medicamento.id != medicamento.id,
            )
        )
    )


def opciones_de_precio(
    sesion: Session, medicamentos: list[Medicamento]
) -> list[OpcionPrecio]:
    """Precios de todos los medicamentos dados, del más barato al más caro."""
    if not medicamentos:
        return []
    precios = sesion.scalars(
        select(Precio)
        .where(Precio.medicamento_id.in_([m.id for m in medicamentos]))
        .options(joinedload(Precio.medicamento), joinedload(Precio.farmacia))
    )
    opciones = [
        OpcionPrecio(
            medicamento=p.medicamento,
            farmacia_nombre=p.farmacia.nombre,
            precio_bs=p.precio_bs,
            unidad_venta=p.unidad_venta,
        )
        for p in precios
    ]
    return sorted(opciones, key=lambda o: o.precio_bs)


AVISO_LEGAL = (
    "⚠️ Esta información es referencial y no reemplaza el criterio de tu médico "
    "ni de tu farmacéutico."
)


def responder_consulta(sesion: Session, texto: str) -> ResultadoConsulta:
    """Flujo completo: interpretar → buscar → equivalentes → precios → mensaje."""
    medicamento = buscar_medicamento(sesion, texto)
    if medicamento is None:
        return ResultadoConsulta(
            encontrado=False,
            mensaje=(
                "No encontré ese medicamento en mi catálogo todavía 😔.\n"
                "Prueba escribiendo el nombre como aparece en la caja o receta "
                "(por ejemplo: *Amoxicilina 500 mg*)."
            ),
        )

    equivalentes = buscar_equivalentes(sesion, medicamento)
    opciones = opciones_de_precio(sesion, [medicamento, *equivalentes])

    concentracion = f"{medicamento.concentracion_valor:g} {medicamento.concentracion_unidad}"
    lineas = [
        f"💊 *{medicamento.nombre_comercial}* {concentracion} ({medicamento.forma})",
        f"Principio activo: *{medicamento.principio_activo.title()}*",
        "",
    ]

    if opciones:
        lineas.append(f"Encontré {len(opciones)} opción(es) con el mismo principio activo:")
        for i, op in enumerate(opciones[:5], start=1):
            etiqueta = " (genérico)" if op.medicamento.es_generico else ""
            lineas.append(
                f"{i}. {op.medicamento.nombre_comercial}{etiqueta} — "
                f"Bs {op.precio_bs:.2f} por {op.unidad_venta} 📍 {op.farmacia_nombre}"
            )
        precio_referencia = max(
            (o.precio_bs for o in opciones if o.medicamento.id == medicamento.id),
            default=None,
        )
        if precio_referencia is not None and opciones[0].precio_bs < precio_referencia:
            ahorro = precio_referencia - opciones[0].precio_bs
            lineas.append("")
            lineas.append(f"💰 Ahorro potencial: *Bs {ahorro:.2f}* por {opciones[0].unidad_venta}.")
    elif equivalentes:
        lineas.append("Existen equivalentes registrados, pero aún no tengo precios cargados.")
    else:
        lineas.append("Por ahora no tengo equivalentes registrados para este medicamento.")

    lineas.extend(["", AVISO_LEGAL])
    return ResultadoConsulta(
        encontrado=True,
        mensaje="\n".join(lineas),
        medicamento=medicamento,
        equivalentes=equivalentes,
        opciones=opciones,
    )
