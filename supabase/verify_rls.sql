-- =============================================================================
-- Verificación RLS: jak_oc
-- Ejecutar después de fix_rls_security.sql para confirmar que todo está correcto
-- =============================================================================

-- 1. Verificar que RLS está habilitado en las 14 tablas
-- Esperado: todas deben mostrar rowsecurity = true
SELECT
  tablename,
  rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN (
    'mociones', 'coautores', 'dim_diputados', 'analisis_ia', 'textos_pdf',
    'dim_comisiones', 'diputados', 'fact_diario_sesion', 'fact_votaciones_detalle',
    'noticias', 'proyectos_ley', 'senadores', 'sesiones', 'votaciones_sala'
  )
ORDER BY tablename;

-- 2. Verificar que solo existen políticas SELECT para anon
-- Esperado: 14 filas, todas con cmd = SELECT y roles = {anon}
SELECT
  tablename,
  policyname,
  roles,
  cmd
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN (
    'mociones', 'coautores', 'dim_diputados', 'analisis_ia', 'textos_pdf',
    'dim_comisiones', 'diputados', 'fact_diario_sesion', 'fact_votaciones_detalle',
    'noticias', 'proyectos_ley', 'senadores', 'sesiones', 'votaciones_sala'
  )
ORDER BY tablename;
