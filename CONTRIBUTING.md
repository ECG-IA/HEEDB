# Convención obligatoria de commits y PR

Todos los commits nuevos y títulos de PR deben seguir [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), con estas reglas del proyecto:

```text
tipo(alcance opcional)!: descripción
```

El alcance y `!` son opcionales; usa `!` cuando el cambio sea incompatible. Tipos permitidos, en minúsculas: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore` y `revert`. La descripción puede escribirse en español. La primera línea tiene un máximo de 100 caracteres y se separa del cuerpo con una línea vacía.

Ejemplos:

```text
feat(metadata): descarga diagnósticos por hospital
fix(aws): corrige la ruta de Emory
docs: explica el inicio de sesión
ci: valida commits y títulos de PR
refactor(metadata)!: cambia la estructura de carpetas
```

## Activación local

Después de clonar, ejecuta una vez:

```bash
git config core.hooksPath .githooks
```

El hook rechaza mensajes mal formados antes de crear el commit. Los hooks no se activan automáticamente al clonar y pueden omitirse localmente; la validación de GitHub funciona por separado.

## Flujo en GitHub

1. Trabaja en `develop` o en una rama de funcionalidad basada en ella.
2. Usa el formato anterior para cada commit y para el título del PR.
3. Espera que el check **Conventional Commits** termine correctamente. Valida el título del PR y cada commit nuevo, y vuelve a ejecutarse cuando cambia el título.
4. Integra mediante **Squash and merge**. El título del PR se utiliza por defecto como título del commit resultante; no lo reemplaces por un mensaje sin formato convencional.
5. Tras un squash de `develop` hacia `main`, sincroniza `main` en `develop` antes del siguiente PR; un commit de sincronización también debe usar un mensaje convencional, por ejemplo `chore(branches): sincroniza develop con main`.

El historial anterior a la adopción de esta política no se reescribe ni se exige corregir. El validador excluye los commits alcanzables desde el commit de referencia `b7af7551cd0c9b784c7ef143d73939ff733a7478`; todos los nuevos sí se comprueban.

## Límite actual de la obligatoriedad en GitHub

Al configurar este repositorio privado, GitHub devolvió HTTP 403 al consultar tanto las protecciones de rama como los rulesets, indicando que se requiere cambiar de plan o visibilidad. Por tanto, la política es obligatoria para contribuir y hay checks automáticos, pero **todavía no existe un bloqueo de fusiones o pushes impuesto por GitHub**. Un usuario con permisos puede ignorar un check fallido. El repositorio permanece privado.

Cuando el plan permita proteger ramas, configurar un ruleset activo para `main` y `develop` que:

- Exija PR y el check `Conventional Commits` (aplicación GitHub Actions).
- Exija estar actualizado con la rama de destino.
- Bloquee eliminación y force-push, sin bypass de administradores.
- Si está disponible, exija este patrón para los mensajes de commit:

```regex
^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9][a-z0-9._/-]*\))?!?: \S[^\r\n]*
```

No convertir el repositorio a público solo para habilitar estas reglas.
