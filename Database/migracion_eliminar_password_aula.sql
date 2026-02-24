-- =============================================
-- MIGRACIÓN: Eliminar columna password_aula
-- Fecha: 2026-02-16
-- Descripción: Elimina la columna password_aula de la tabla aulas
--              ya que la autenticación se maneja por JWT
-- =============================================

USE `control-asistencia`;

-- Eliminar columna password_aula
ALTER TABLE aulas 
DROP COLUMN IF EXISTS password_aula;

-- Verificar la estructura de la tabla
DESCRIBE aulas;

-- Resultado esperado:
-- +--------+-------------+------+-----+---------+----------------+
-- | Field  | Type        | Null | Key | Default | Extra          |
-- +--------+-------------+------+-----+---------+----------------+
-- | id     | int         | NO   | PRI | NULL    | auto_increment |
-- | nombre | varchar(50) | NO   | UNI | NULL    |                |
-- +--------+-------------+------+-----+---------+----------------+
