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
    source          VARCHAR(20)  NOT NULL,
    CONSTRAINT uq_snapshot_asset_timestamp_source UNIQUE (asset_id, timestamp, source)
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

-- Historique des taux de change — nécessaire pour comparer la volatilité
-- du FCFA à celle des cryptos (section 11.5), pas seulement l'affirmer.
CREATE TABLE IF NOT EXISTS fx_rate_history (
    id                   BIGSERIAL PRIMARY KEY,
    rate_date            DATE         NOT NULL,
    ingestion_time       TIMESTAMPTZ  NOT NULL,
    usd_eur_rate         NUMERIC(10, 6) NOT NULL,
    eur_xof_fixed_rate   NUMERIC(10, 4) NOT NULL,
    usd_xof_rate         NUMERIC(12, 4) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_fx_ingestion ON fx_rate_history (ingestion_time DESC);
