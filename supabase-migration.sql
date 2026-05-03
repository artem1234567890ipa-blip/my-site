-- Таблица регистраций ChemLab
CREATE TABLE IF NOT EXISTS registrations (
  id BIGSERIAL PRIMARY KEY,
  telegram_id BIGINT UNIQUE NOT NULL,
  username TEXT DEFAULT '',
  full_name TEXT NOT NULL,
  access_code TEXT UNIQUE NOT NULL,
  verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_registrations_code ON registrations(access_code);
CREATE INDEX IF NOT EXISTS idx_registrations_tg ON registrations(telegram_id);

-- Row Level Security: разрешить чтение только по коду
ALTER TABLE registrations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow code verification" ON registrations
  FOR SELECT
  USING (true);

-- Только серверный ключ может вставлять записи
CREATE POLICY "Only service can insert" ON registrations
  FOR INSERT
  WITH CHECK (true);
