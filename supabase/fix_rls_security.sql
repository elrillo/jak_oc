-- =============================================================================
-- RLS FIX: jak_oc Supabase Security Hardening
-- Fecha: 2026-03-11
-- Propósito: Habilitar RLS y restringir acceso anon a solo SELECT
--
-- NOTAS DE SEGURIDAD:
-- - Conexiones directas PostgreSQL (usuario postgres) bypassan RLS
-- - La clave service_role bypassea RLS
-- - Solo el acceso vía PostgREST (clave anon) se ve afectado
-- - Este es un dashboard público de solo lectura; no se necesitan escrituras vía API
--
-- INSTRUCCIONES:
-- Ejecutar este script completo en Supabase SQL Editor
-- Es idempotente: se puede ejecutar múltiples veces sin error
-- =============================================================================

DO $$
DECLARE
  tbl TEXT;
  pol RECORD;
  table_exists BOOLEAN;
  policy_exists BOOLEAN;
  all_tables TEXT[] := ARRAY[
    'mociones', 'coautores', 'dim_diputados', 'analisis_ia', 'textos_pdf',
    'dim_comisiones', 'diputados', 'fact_diario_sesion',
    'fact_votaciones_detalle', 'noticias', 'proyectos_ley',
    'senadores', 'sesiones', 'votaciones_sala'
  ];
BEGIN
  FOREACH tbl IN ARRAY all_tables
  LOOP
    -- Verificar si la tabla existe
    SELECT EXISTS (
      SELECT 1 FROM pg_tables
      WHERE schemaname = 'public' AND tablename = tbl
    ) INTO table_exists;

    IF NOT table_exists THEN
      RAISE NOTICE 'Tabla % no existe, saltando...', tbl;
      CONTINUE;
    END IF;

    -- Habilitar RLS (idempotente)
    EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', tbl);

    -- Eliminar todas las políticas existentes
    FOR pol IN
      SELECT policyname FROM pg_policies
      WHERE schemaname = 'public' AND tablename = tbl
    LOOP
      EXECUTE format('DROP POLICY %I ON public.%I', pol.policyname, tbl);
    END LOOP;

    -- Crear política SELECT-only para anon
    EXECUTE format(
      'CREATE POLICY "anon_select_%s" ON public.%I FOR SELECT TO anon USING (true)',
      tbl, tbl
    );

    RAISE NOTICE 'Tabla % asegurada correctamente', tbl;
  END LOOP;
END $$;
