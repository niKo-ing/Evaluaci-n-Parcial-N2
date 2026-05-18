CREATE OR REPLACE FUNCTION sati_block_updates_deletes()
RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'MODO WORM ACTIVO: No se permite % en transactions', TG_OP;
END;
$$ LANGUAGE plpgsql;
