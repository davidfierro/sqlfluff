# Cuerpos de las PRs contra `sqlfluff/sqlfluff`

Generados desde los mensajes de commit de cada rama. Para abrir cada PR a mano, usar el
enlace de comparación y pegar el cuerpo del fichero correspondiente.

| PR | Rama | Base | Cuerpo | Enlace de comparación |
|----|------|------|--------|------------------------|
| A | `snowflake-governance-policies` | main | [`snowflake-governance-policies.md`](./snowflake-governance-policies.md) | [comparar](https://github.com/sqlfluff/sqlfluff/compare/main...davidfierro:sqlfluff:snowflake-governance-policies?expand=1) |
| B | `snowflake-table-gaps` | main | [`snowflake-table-gaps.md`](./snowflake-table-gaps.md) | [comparar](https://github.com/sqlfluff/sqlfluff/compare/main...davidfierro:sqlfluff:snowflake-table-gaps?expand=1) |
| C | `snowflake-materialized-view` | main | [`snowflake-materialized-view.md`](./snowflake-materialized-view.md) | [comparar](https://github.com/sqlfluff/sqlfluff/compare/main...davidfierro:sqlfluff:snowflake-materialized-view?expand=1) |
| D | `snowflake-view-governance-alter` | snowflake-governance-policies | [`snowflake-view-governance-alter.md`](./snowflake-view-governance-alter.md) | [comparar](https://github.com/sqlfluff/sqlfluff/compare/main...davidfierro:sqlfluff:snowflake-view-governance-alter?expand=1) |
| E1 | `snowflake-dynamic-table-clauses` | main | [`snowflake-dynamic-table-clauses.md`](./snowflake-dynamic-table-clauses.md) | [comparar](https://github.com/sqlfluff/sqlfluff/compare/main...davidfierro:sqlfluff:snowflake-dynamic-table-clauses?expand=1) |
| E2 | `snowflake-dynamic-table-columns-governance` | snowflake-governance-policies | [`snowflake-dynamic-table-columns-governance.md`](./snowflake-dynamic-table-columns-governance.md) | [comparar](https://github.com/sqlfluff/sqlfluff/compare/main...davidfierro:sqlfluff:snowflake-dynamic-table-columns-governance?expand=1) |
| F | `snowflake-stream` | main | [`snowflake-stream.md`](./snowflake-stream.md) | [comparar](https://github.com/sqlfluff/sqlfluff/compare/main...davidfierro:sqlfluff:snowflake-stream?expand=1) |
| G | `snowflake-task` | main | [`snowflake-task.md`](./snowflake-task.md) | [comparar](https://github.com/sqlfluff/sqlfluff/compare/main...davidfierro:sqlfluff:snowflake-task?expand=1) |
| H | `snowflake-procedure` | main | [`snowflake-procedure.md`](./snowflake-procedure.md) | [comparar](https://github.com/sqlfluff/sqlfluff/compare/main...davidfierro:sqlfluff:snowflake-procedure?expand=1) |
| I | `snowflake-scripting-control-flow` | main | [`snowflake-scripting-control-flow.md`](./snowflake-scripting-control-flow.md) | [comparar](https://github.com/sqlfluff/sqlfluff/compare/main...davidfierro:sqlfluff:snowflake-scripting-control-flow?expand=1) |
| J | `snowflake-scripting-cursors-declare-body` | snowflake-scripting-control-flow | [`snowflake-scripting-cursors-declare-body.md`](./snowflake-scripting-cursors-declare-body.md) | [comparar](https://github.com/sqlfluff/sqlfluff/compare/main...davidfierro:sqlfluff:snowflake-scripting-cursors-declare-body?expand=1) |

## Orden de apertura

1. **Ola 1** (independientes, en paralelo): A, B, C, E1, F, G, H.
2. **Ola 2** (tras el merge de A, rebasando antes): D, E2.
3. **Ola 3**: I y, después, J.

