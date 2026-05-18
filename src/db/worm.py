from sqlalchemy import text


WORM_SQL = """
CREATE OR REPLACE FUNCTION sati_block_updates_deletes()
RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'MODO WORM ACTIVO: No se permite % en transactions', TG_OP;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS sati_worm_trigger ON transactions;
CREATE TRIGGER sati_worm_trigger
BEFORE UPDATE OR DELETE ON transactions
FOR EACH ROW EXECUTE FUNCTION sati_block_updates_deletes();
"""


def apply_postgres_worm(engine):
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as conn:
        conn.execute(text(WORM_SQL))
