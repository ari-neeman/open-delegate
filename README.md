# OpenDelegate

Asistente de IA centrado en el usuario. No un asistente cautivo de una empresa: uno libre, delegado y auditado.

## Principios

1. **El usuario manda.** El agente solo actúa con consentimiento explícito.
2. **Nunca contraseñas reales.** Solo tokens delegados, tarjetas virtuales y permisos temporales.
3. **El agente se identifica como IA.** Dice siempre en nombre de quién actúa.
4. **Todo queda auditado.** El usuario puede revisar y revocar cada acción.
5. **Aprobación humana antes de pagar.** Nada de gastos automáticos sin confirmación.

## ¿Qué hace?

- Solicita compras en tu nombre, pero no las ejecuta sin tu aprobación.
- Respeta límites de gasto por tienda y caducidad de permisos.
- Genera credenciales de un solo uso (tokens, tarjetas virtuales).
- Registra todo en un log de auditoría que tú controlas.

## Estado

Prototipo Etapa 1 — servidor local en FastAPI. Corre en Linux, sin dependencias de terceros.

## Instalación

    git clone <tu-repo>
    cd open-delegate
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    uvicorn open_delegate:app --reload --port 8000

Abre `http://localhost:8000/docs` en el navegador.

## Licencia

Apache 2.0.
