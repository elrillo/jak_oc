/**
 * API Route: /api/data
 *
 * Carga todas las tablas desde PostgreSQL (Supabase) usando conexión directa,
 * igual que la versión Python (migrate_to_supabase.py / app.py).
 *
 * Esto evita problemas con RLS y API keys de Supabase JS.
 * Se ejecuta en el servidor (Node.js), no en el navegador.
 */
import { NextResponse } from 'next/server'
import { Pool } from 'pg'

// Pool de conexiones reutilizable (singleton)
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
  max: 5,
  idleTimeoutMillis: 30000,
})

export async function GET() {
  let client
  try {
    client = await pool.connect()

    // Ejecutar las 4 consultas en paralelo
    const [mocionesRes, coautoresRes, diputadosRes, iaRes] = await Promise.all([
      client.query('SELECT * FROM mociones'),
      client.query('SELECT * FROM coautores'),
      client.query('SELECT * FROM dim_diputados'),
      client.query('SELECT * FROM analisis_ia'),
    ])

    console.log(`[API/data] mociones: ${mocionesRes.rowCount}, coautores: ${coautoresRes.rowCount}, dim_diputados: ${diputadosRes.rowCount}, analisis_ia: ${iaRes.rowCount}`)

    // Log de columnas para debug
    if (mocionesRes.rows[0]) {
      console.log('[API/data] mociones columns:', Object.keys(mocionesRes.rows[0]))
    }

    return NextResponse.json({
      mociones: mocionesRes.rows,
      coautores: coautoresRes.rows,
      diputados: diputadosRes.rows,
      analisisIA: iaRes.rows,
    })
  } catch (error) {
    console.error('[API/data] Error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Error desconocido al conectar a PostgreSQL' },
      { status: 500 }
    )
  } finally {
    if (client) client.release()
  }
}
