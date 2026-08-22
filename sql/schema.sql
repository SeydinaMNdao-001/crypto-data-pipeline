-- Section 9 du document projet : modèle de données du pipeline crypto.

CREATE TABLE IF NOT EXISTS crypto_market_snapshot (
    id              BIGSERIAL PRIMARY KEY,
    asset_id        VARCHAR(50)  NOT NULL,
    symbol          VARCHAR(10)  NOT NULL,
    timestamp       TIMESTAMPTZ  NOT NULL,
    ingestion_time  TIMESTAMPTZ  NOT NULL,
    price_usd       NUMERIC(20, 8),
    price_xof       NUMERIC(20, 4),
    volume_24h      NUMERIC(24, 4),
    market_cap      NUMERIC(24, 2),
    change_24h      NUMERIC(10, 4),
    source          VARCHAR(20)  NOT NULL
);

-- Les requêtes du dashboard et de l'API vont surtout demander :
-- "historique d'un actif donné, trié par date" -> cet index couvre ce cas.
CREATE INDEX IF NOT EXISTS idx_snapshot_asset_time
    ON crypto_market_snapshot (asset_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_snapshot_ingestion
    ON crypto_market_snapshot (ingestion_time DESC);

-- Table secondaire (section 9 et 11.2) : suivi du peg des 3 stablecoins.
-- Pas encore alimentée à ce stade du projet (phase Analytics).
CREATE TABLE IF NOT EXISTS stablecoin_peg_history (
    id                     BIGSERIAL PRIMARY KEY,
    asset_id               VARCHAR(50)    NOT NULL,
    timestamp              TIMESTAMPTZ    NOT NULL,
    price_usd              NUMERIC(10, 6) NOT NULL,
    peg_deviation          NUMERIC(10, 6) NOT NULL,
    seuil_alerte_franchi   BOOLEAN        NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_peg_asset_time
    ON stablecoin_peg_history (asset_id, timestamp DESC);
